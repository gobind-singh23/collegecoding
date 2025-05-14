#!/usr/bin/env python3
"""
data_extractor.py - Module for loading Codeforces data into Qdrant and retrieving similar questions

This script provides functionality to:
1. Precompute embeddings for the Codeforces dataset and store them for faster loading
2. Initialize a Qdrant vector database collection with precomputed embeddings
3. Query for similar questions based on semantic similarity
"""

import os
import pickle
import time
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import numpy as np
import qdrant_client
from qdrant_client.http import models
from datasets import load_dataset
from sentence_transformers import SentenceTransformer

# Constants
COLLECTION_NAME = "codeforces_problems"
EMBEDDING_DIM = 384  # Default for all-MiniLM-L6-v2
MODEL_NAME = "all-MiniLM-L6-v2"
DATA_DIR = Path("codeforces_data")
EMBEDDINGS_FILE = DATA_DIR / "codeforces_embeddings.pkl"
METADATA_FILE = DATA_DIR / "codeforces_metadata.pkl"


def precompute_embeddings(force_recompute: bool = False) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
    """
    Precompute embeddings for the Codeforces dataset and save them to disk.
    
    Args:
        force_recompute: If True, recompute embeddings even if they already exist
        
    Returns:
        A tuple of (embeddings array, metadata list)
    """
    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True)
    
    # Check if embeddings already exist
    if not force_recompute and EMBEDDINGS_FILE.exists() and METADATA_FILE.exists():
        print(f"Loading precomputed embeddings from {EMBEDDINGS_FILE}")
        with open(EMBEDDINGS_FILE, 'rb') as f:
            embeddings = pickle.load(f)
        with open(METADATA_FILE, 'rb') as f:
            metadata = pickle.load(f)
        return embeddings, metadata
    
    # Load the dataset and compute embeddings
    print("Loading Codeforces dataset from Hugging Face...")
    start_time = time.time()
    dataset = load_dataset("open-r1/codeforces")
    print(f"Dataset loaded in {time.time() - start_time:.2f} seconds")
    
    # Initialize the model
    model = SentenceTransformer(MODEL_NAME)
    
    # Extract all problem statements and metadata
    problems = dataset['train']
    
    # Prepare problem texts for embedding (combining important fields)
    problem_texts = []
    for item in problems:
        # Combine fields for better semantic search
        text = f"Title: {item.get('title', '')}\n\n"
        text += f"Description: {item.get('description', '')}\n\n"
        
        if item.get('input_format'):
            text += f"Input Format: {item.get('input_format', '')}\n\n"
        
        if item.get('output_format'):
            text += f"Output Format: {item.get('output_format', '')}"
        
        problem_texts.append(text)
    
    # Prepare metadata with only the important fields
    metadata = [
        {
            "id": item.get("id", ""),
            "contest_name": item.get("contest_name", ""),
            "description": item.get("description", ""),
            "input_format": item.get("input_format", ""),
            "output_format": item.get("output_format", ""),
            "title": item.get("title", "")  # Include title for display purposes
        }
        for item in problems
    ]
    
    # Compute embeddings (batched to save memory)
    print(f"Computing embeddings for {len(problem_texts)} problems...")
    start_time = time.time()
    embeddings = model.encode(
        problem_texts, 
        show_progress_bar=True, 
        batch_size=32,
        convert_to_numpy=True
    )
    print(f"Embeddings computed in {time.time() - start_time:.2f} seconds")
    
    # Save embeddings and metadata to disk
    with open(EMBEDDINGS_FILE, 'wb') as f:
        pickle.dump(embeddings, f)
    with open(METADATA_FILE, 'wb') as f:
        pickle.dump(metadata, f)
        
    print(f"Saved embeddings to {EMBEDDINGS_FILE} and metadata to {METADATA_FILE}")
    
    return embeddings, metadata


class CodeforcesProblemDB:
    """Manager for Codeforces problem vector database."""
    
    def __init__(self, 
                 use_precomputed: bool = True, 
                 recreate_collection: bool = False,
                 qdrant_location: str = ":memory:",
                 qdrant_port: Optional[int] = None):
        """
        Initialize the Codeforces problem database.
        
        Args:
            use_precomputed: Whether to use precomputed embeddings
            recreate_collection: If True, delete and recreate the collection if it exists
            qdrant_location: Location for Qdrant database (":memory:" or file path)
            qdrant_port: Port for Qdrant server (None for in-memory or local file)
        """
        # Initialize the sentence transformer model
        self.model = SentenceTransformer(MODEL_NAME)
        
        # Initialize Qdrant client
        if qdrant_port is not None:
            self.client = qdrant_client.QdrantClient(
                location=qdrant_location,
                port=qdrant_port
            )
        else:
            self.client = qdrant_client.QdrantClient(path=qdrant_location)
        
        # Check if collection exists and create if needed
        collections = self.client.get_collections().collections
        collection_exists = any(collection.name == COLLECTION_NAME for collection in collections)
        
        if collection_exists and recreate_collection:
            self.client.delete_collection(COLLECTION_NAME)
            collection_exists = False
            
        if not collection_exists:
            self._create_collection()
            if use_precomputed:
                self._load_precomputed_embeddings()
            else:
                self._load_dataset()
    
    def _create_collection(self):
        """Create a new collection in Qdrant for Codeforces problems."""
        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=EMBEDDING_DIM,
                distance=models.Distance.COSINE
            )
        )
    
    def _load_precomputed_embeddings(self):
        """Load precomputed embeddings into Qdrant."""
        print("Loading precomputed embeddings into Qdrant...")
        start_time = time.time()
        
        # Load embeddings and metadata
        embeddings, metadata = precompute_embeddings()
        
        # Insert in batches
        batch_size = 100
        total_records = len(embeddings)
        
        for i in range(0, total_records, batch_size):
            end_idx = min(i + batch_size, total_records)
            batch_embeddings = embeddings[i:end_idx]
            batch_metadata = metadata[i:end_idx]
            
            # Prepare points to insert
            points = [
                models.PointStruct(
                    id=i + idx,
                    vector=embedding.tolist(),
                    payload=metadata_item
                )
                for idx, (embedding, metadata_item) in enumerate(zip(batch_embeddings, batch_metadata))
            ]
            
            # Insert into Qdrant
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            
            print(f"Inserted {end_idx}/{total_records} problems")
        
        print(f"Finished loading in {time.time() - start_time:.2f} seconds")
    
    def _load_dataset(self):
        """Load Codeforces dataset from Hugging Face and insert into Qdrant."""
        print("Loading Codeforces dataset from Hugging Face...")
        dataset = load_dataset("open-r1/codeforces")
        
        # Process and insert batches
        batch_size = 100
        total_records = len(dataset['train'])
        
        for i in range(0, total_records, batch_size):
            end_idx = min(i + batch_size, total_records)
            batch = dataset['train'][i:end_idx]
            
            # Extract problem texts for embedding
            problem_texts = []
            for item in batch:
                # Combine fields for better semantic search
                text = f"Title: {item.get('title', '')}\n\n"
                text += f"Description: {item.get('description', '')}\n\n"
                
                if item.get('input_format'):
                    text += f"Input Format: {item.get('input_format', '')}\n\n"
                
                if item.get('output_format'):
                    text += f"Output Format: {item.get('output_format', '')}"
                
                problem_texts.append(text)
            
            # Generate embeddings
            embeddings = self.model.encode(problem_texts)
            
            # Prepare points to insert with only the important fields
            points = [
                models.PointStruct(
                    id=i + idx,
                    vector=embedding.tolist(),
                    payload={
                        "id": batch[idx].get("id", ""),
                        "contest_name": batch[idx].get("contest_name", ""),
                        "description": batch[idx].get("description", ""),
                        "input_format": batch[idx].get("input_format", ""),
                        "output_format": batch[idx].get("output_format", ""),
                        "title": batch[idx].get("title", "")  # Include title for display purposes
                    }
                )
                for idx, embedding in enumerate(embeddings)
            ]
            
            # Insert into Qdrant
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            
            print(f"Inserted {end_idx}/{total_records} problems")
    
    def search_similar_problems(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar problems in the database.
        
        Args:
            query: The problem statement to search for
            limit: Maximum number of results to return
            
        Returns:
            List of similar problems with their metadata
        """
        # Generate embedding for the query
        query_vector = self.model.encode(query).tolist()
        
        # Search in Qdrant
        search_results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit
        )
        
        # Format results
        results = []
        for result in search_results:
            problem_data = result.payload
            problem_data["similarity_score"] = result.score
            results.append(problem_data)
            
        return results


# Create a global instance of the database
_db_instance = None

def get_db_instance(
    recreate: bool = False,
    use_precomputed: bool = True,
    qdrant_location: str = ":memory:",
    qdrant_port: Optional[int] = None
) -> CodeforcesProblemDB:
    """
    Get or create the database instance.
    
    Args:
        recreate: If True, recreate the database instance
        use_precomputed: Whether to use precomputed embeddings
        qdrant_location: Location for Qdrant database
        qdrant_port: Port for Qdrant server
        
    Returns:
        Database instance
    """
    global _db_instance
    if _db_instance is None or recreate:
        _db_instance = CodeforcesProblemDB(
            use_precomputed=use_precomputed,
            recreate_collection=recreate,
            qdrant_location=qdrant_location,
            qdrant_port=qdrant_port
        )
    return _db_instance


def generate_embeddings_cache(force_recompute: bool = False) -> None:
    """
    Generate and cache embeddings for the Codeforces dataset.
    This function should be called once before using the database in production.
    
    Args:
        force_recompute: If True, recompute embeddings even if they already exist
    """
    print("Precomputing embeddings for the Codeforces dataset...")
    precompute_embeddings(force_recompute=force_recompute)
    print("Embedding generation complete.")


def process_llm_query(
    query: str, 
    limit: int = 10,
    use_precomputed: bool = True,
    qdrant_location: str = ":memory:",
    qdrant_port: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Process a query for finding similar Codeforces problems.
    
    Args:
        query: A string describing a programming problem
        limit: Maximum number of similar problems to return
        use_precomputed: Whether to use precomputed embeddings
        qdrant_location: Location for Qdrant database
        qdrant_port: Port for Qdrant server
        
    Returns:
        List of similar problems with their metadata
    """
    db = get_db_instance(
        use_precomputed=use_precomputed,
        qdrant_location=qdrant_location,
        qdrant_port=qdrant_port
    )
    similar_problems = db.search_similar_problems(query, limit=limit)
    return similar_problems


if __name__ == "__main__":
    # Generate the embeddings cache for future use
    print("Generating embeddings cache...")
    generate_embeddings_cache()
    
    # Example usage
    test_query = """
    You are given an array of n integers. Find the maximum sum of any contiguous subarray.
    """
    
    print("\nSearching for problems similar to:")
    print(test_query)
    print("\nResults:")
    
    results = process_llm_query(test_query, use_precomputed=True)
    
    for i, result in enumerate(results):
        print(f"\n--- Result {i+1} (Score: {result['similarity_score']:.4f}) ---")
        print(f"Title: {result['title']}")
        print(f"ID: {result['id']}")
        print(f"Contest: {result.get('contest_name', 'N/A')}")
        print(f"\nDescription: {result['description'][:200]}...")