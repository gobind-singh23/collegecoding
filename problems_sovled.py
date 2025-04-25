import requests

def get_user_accepted_submissions_in_contest(handle, contest_id):
    url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=1000"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            submissions = data['result']
            
            solved_problems = set()
            for sub in submissions:
                if sub['verdict'] == 'OK' and sub['contestId'] == contest_id:
                    problem_id = sub['problem']['index']  # like 'A', 'B', 'C'
                    problem_name = sub['problem']['name']
                    solved_problems.add((problem_id, problem_name))
            
            # sort by problem index (like A, B, C, etc.)
            solved_problems = sorted(list(solved_problems))
            return solved_problems
        else:
            print("Error in API response:", data['comment'])
    else:
        print(f"HTTP Error: {response.status_code}")
    
    return []

if __name__ == "__main__":
    handle = "codersingh23"     # user's handle
    contest_id = 1927      # contest id you are checking
    
    solved = get_user_accepted_submissions_in_contest(handle, contest_id)
    
    if solved:
        print(f"{handle} solved the following problems in contest {contest_id}:")
        for idx, name in solved:
            print(f"  {idx}. {name}")
    else:
        print(f"{handle} didn't solve any problems in contest {contest_id} or no data found.")
