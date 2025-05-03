import os
from typing import Dict, Any, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import json
from unsloth import FastLanguageModel
class LLMRouter:
    """
    A class that routes LLM queries to the appropriate specialized model based on query content.
    """
    
    def __init__(self, 
                 master_model_id: str = "microsoft/phi-2",
                 mongodb_model_id: str = "Chirayu/phi-2-mongodb",
                 codeforces_model_id: str = "qgallouedec/gemma-3-27b-it-codeforces-SFT"):
        """
        Initialize the LLM router with the specified models.
        
        Args:
            master_model_id: Model ID for the master LLM (classifier)
            mongodb_model_id: Model ID for the MongoDB query generator
            codeforces_model_id: Model ID for the CodeForces problem solver
        """
        self.master_model_id = master_model_id
        self.mongodb_model_id = mongodb_model_id
        self.codeforces_model_id = codeforces_model_id
        
        # Load the master model (smaller model for classification)
        print(f"Loading master model: {master_model_id}")
        self.master_tokenizer = AutoTokenizer.from_pretrained(master_model_id, trust_remote_code= True)
        self.master_model = AutoModelForCausalLM.from_pretrained(
            master_model_id,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code = True
        )
        
        # Initialize the slave models as None (load on-demand to save memory)
        self.mongodb_tokenizer = None
        self.mongodb_model = None
        self.codeforces_tokenizer = None
        self.codeforces_model = None
        
        # Flag to track which models are loaded
        self.mongodb_loaded = False
        self.codeforces_loaded = False
    
    def _load_mongodb_model(self):
        """Load the MongoDB query generator model"""
        if not self.mongodb_loaded:
            print(f"Loading MongoDB model: {self.mongodb_model_id}")
            self.mongodb_tokenizer = AutoTokenizer.from_pretrained(self.mongodb_model_id)
            self.mongodb_model = AutoModelForCausalLM.from_pretrained(
                self.mongodb_model_id,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            self.mongodb_loaded = True
    
    def _load_codeforces_model(self):
        """Load the CodeForces problem solver model"""
        if not self.codeforces_loaded:
            print(f"Loading CodeForces model: {self.codeforces_model_id}")
            self.codeforces_tokenizer = AutoTokenizer.from_pretrained(self.codeforces_model_id)
            self.codeforces_model = AutoModelForCausalLM.from_pretrained(
                self.codeforces_model_id,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            self.codeforces_loaded = True
    
    def _classify_query(self, query: str) -> str:
        """
        Use the master model to classify whether the query is for MongoDB or CodeForces.
        
        Args:
            query: The user query
            
        Returns:
            Classification result: "mongodb" or "codeforces"
        """
        # Prepare prompt for classification
        classification_prompt = f"""
        You are a query classifier that determines the right specialized model to handle a user query.
        
        The query will be sent to one of two specialized models:
        1. MongoDB Query Generator: For queries about database operations, MongoDB queries, aggregation, or data retrieval.
        2. CodeForces Problem Solver: For queries about competitive programming, algorithmic problems, or specific CodeForces challenges.
        
        User Query: {query}
        
        Which specialized model should handle this query? Respond with only one word: "mongodb" or "codeforces".
        """
        
        # Generate a response from the master model
        inputs = self.master_tokenizer(classification_prompt, return_tensors="pt").to(self.master_model.device)
        with torch.no_grad():
            output = self.master_model.generate(
                **inputs,
                max_new_tokens=10,
                temperature=0.2,
                do_sample=False
            )
        
        response = self.master_tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Extract classification from response
        response = response.lower().strip()
        if "mongodb" in response:
            return "mongodb"
        elif "codeforces" in response:
            return "codeforces"
        else:
            # Default to CodeForces if classification is unclear
            return "codeforces"
    
    def _generate_mongodb_query(self, query: str, db_schema: str) -> str:
        """
        Generate a MongoDB query based on the user's query.
        
        Args:
            query: The user query
            
        Returns:
            Generated MongoDB query
        """
        self._load_mongodb_model()
        
        # Format the prompt for MongoDB query generation
        with open("db_schema.json", "r") as f:
            db_schema = json.load(f)

        prompt = f"""<s> 
        Task Description:
        Your task is to create a MongoDB query that accurately fulfills the provided Instruct while strictly adhering to the given MongoDB schema. Ensure that the query solely relies on keys and columns present in the schema. Minimize the usage of lookup operations wherever feasible to enhance query efficiency.

        MongoDB Schema: 
        {db_schema}

        ### Instruct:
        {query}

        ### Output:
        """
        
        inputs = self.mongodb_tokenizer(prompt, return_tensors="pt").to(self.mongodb_model.device)
        with torch.no_grad():
            output = self.mongodb_model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True
            )
        
        response = self.mongodb_tokenizer.decode(output[0], skip_special_tokens=True)
        return response
    
    def _solve_codeforces_problem(self, query: str) -> str:
        """
        Generate a solution for a CodeForces problem based on the user's query.
        
        Args:
            query: The user query
            
        Returns:
            Generated solution or explanation
        """
        self._load_codeforces_model()
        
        # Format the prompt for CodeForces problem-solving
        prompt = f"""
        You are a competitive programming expert specializing in CodeForces problems.
        
        User Query: {query}
        
        Provide a detailed explanation or solution:
        """
        
        inputs = self.codeforces_tokenizer(prompt, return_tensors="pt").to(self.codeforces_model.device)
        with torch.no_grad():
            output = self.codeforces_model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.7,
                do_sample=True
            )
        
        response = self.codeforces_tokenizer.decode(output[0], skip_special_tokens=True)
        return response
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query by first classifying it and then routing to the appropriate model.
        
        Args:
            query: The user query
            
        Returns:
            Dictionary containing the query, model used, and response
        """
        # Classify the query
        query_type = self._classify_query(query)
        
        # Route to the appropriate model
        if query_type == "mongodb":
            response = self._generate_mongodb_query(query, "db_schema.json")
            model_used = self.mongodb_model_id
        else:  # Default to codeforces
            response = self._solve_codeforces_problem(query)
            model_used = self.codeforces_model_id
        
        # Return the results
        return {
            "query": query,
            "query_type": query_type,
            "model_used": model_used,
            "response": response
        }
    
    def unload_models(self, keep_master: bool = True):
        """
        Unload models to free up GPU memory
        
        Args:
            keep_master: Whether to keep the master model loaded
        """
        if self.mongodb_loaded:
            del self.mongodb_model
            del self.mongodb_tokenizer
            self.mongodb_model = None
            self.mongodb_tokenizer = None
            self.mongodb_loaded = False
            torch.cuda.empty_cache()
        
        if self.codeforces_loaded:
            del self.codeforces_model
            del self.codeforces_tokenizer
            self.codeforces_model = None
            self.codeforces_tokenizer = None
            self.codeforces_loaded = False
            torch.cuda.empty_cache()
        
        if not keep_master:
            del self.master_model
            del self.master_tokenizer
            self.master_model = None
            self.master_tokenizer = None
            torch.cuda.empty_cache()

# Function to create a singleton instance
_llm_router = None

def get_llm_router() -> LLMRouter:
    """
    Get a singleton instance of the LLMRouter.
    
    Returns:
        LLMRouter instance
    """
    global _llm_router
    if _llm_router is None:
        _llm_router = LLMRouter()
    return _llm_router

# Simple wrapper function for the Streamlit app
def process_llm_query(query: str) -> str:
    """
    Process an LLM query for the Streamlit app.
    
    Args:
        query: The user query
        
    Returns:
        Formatted response string
    """
    router = get_llm_router()
    result = router.process_query(query)
    
    # Format the response for the UI
    response = f"""
    Query: {result['query']}
    
    Query Type: {result['query_type'].upper()}
    Model Used: {result['model_used']}
    
    Response:
    {result['response']}
    """
    
    return response