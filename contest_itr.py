import requests
import time
from get_iit_guys import get_valid_participants_with_org
from extract_div import extract_division
from add_to_database import store_valid_participants_in_users
def get_recent_contests(n=10):
    # API URL
    url = "https://codeforces.com/api/contest.list"

    # Fetch contests
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch contests: {response.status_code}")

    data = response.json()
    if data['status'] != 'OK':
        raise Exception("Error fetching contest list")

    # Filter out only finished contests
    contests = [contest for contest in data['result'] if contest['phase'] == 'FINISHED']

    # Get the most recent 'n' contests
    recent_contests = contests[:n]
    return recent_contests

def get_participants_from_contest(contest_id):
    """
    Given a contest ID, fetch the list of participant handles.
    """
    url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['status'] != 'OK':
            print(f"Error fetching standings for contest {contest_id}")
            return []

        rows = data['result']['rows']
        participants = []

        for row in rows:
            party = row['party']
            if party['participantType'] == 'CONTESTANT':  # Only real contestants
                for member in party['members']:
                    participants.append(member['handle'])
    
        return participants

    except Exception as e:
        print(f"Exception fetching standings for contest {contest_id}: {e}")
        return []
def get_all_participants(contests):
    """
    Iterate through all contests and collect unique participants.
    """
    all_participants = set()

    for idx, contest in enumerate(contests):
        contest_id = contest['id']
        print(f"Fetching participants for contest {contest_id} ({idx+1}/{len(contests)})...")
        
        participants = get_participants_from_contest(contest_id)
        all_participants.update(participants)
        
        time.sleep(0.5)  # Be nice to the API (0.5 sec delay)

    return all_participants


# Example usage
if __name__ == "__main__":
    contests = get_recent_contests(1)
    all_participants = get_all_participants(contests)
    # print(f"Fetched {len(contests)} contests.")
    # print("Some example participants:", list(all_participants))
    valid_participants = get_valid_participants_with_org(all_participants)
    print(f"Total valid participants with known organizations: {len(valid_participants)}")
    for p in valid_participants[:5]:  # Print first 10 as example
        print(p)
    store_valid_participants_in_users(valid_participants, db_name='collegecoding',collection_name='users')
    for contest in contests[:5]:  # Just printing first 5 for demo
        division = extract_division(contest['name'])
        # print(f"Name: {contest['name']}, ID: {contest['id']}, Division: {division}")
