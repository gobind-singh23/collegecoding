import requests
import json

def get_contest_problems_with_tags(contest_id):
    url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&showUnofficial=true"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            contest_name = data['result']['contest']['name']
            problems = data['result']['problems']
            return contest_name, problems
        else:
            print("Error in API response:", data['comment'])
    else:
        print(f"HTTP Error: {response.status_code}")
    
    return None, None

if __name__ == "__main__":
    contest_id = 1922  # example contest
    contest_name, problems = get_contest_problems_with_tags(contest_id)
    
    if contest_name:
        print(f"Contest Name: {contest_name}")
        print("\nProblems with Tags:")
        for problem in problems:
            tags = ", ".join(problem['tags']) if problem['tags'] else "No tags available"
            print(f"  {problem['index']}. {problem['name']}  |  Tags: {tags}")
