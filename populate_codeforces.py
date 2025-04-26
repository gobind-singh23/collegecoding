import requests
import time

# Clear output files
open('users.txt', 'w').close()
open('contests.txt', 'w').close()
open('rating.txt', 'w').close()
open('problems.txt', 'w').close()

def fetch_contests():
    url = "https://codeforces.com/api/contest.list"
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json()
        if data['status'] != 'OK':
            return []
        return data['result']
    except:
        return []

contests = fetch_contests()
contests = contests[:500]

rated_contest_ids = set()
user_set = set()

with open('contests.txt', 'w') as f_contest, open('rating.txt', 'w') as f_rating, open('users.txt', 'w') as f_users:
    for contest in contests:
        contest_id = contest['id']
        url = f"https://codeforces.com/api/contest.ratingChanges?contestId={contest_id}"
        try:
            resp = requests.get(url, timeout=15)
            data = resp.json()
            if data['status'] != 'OK' or not data['result']:
                continue  # Skip unrated contests

            name = contest['name'].replace(',', ' ')
            div = 1 if 'Div. 1' in name else 2 if 'Div. 2' in name else 3 if 'Div. 3' in name else 4
            time_seconds = contest.get('startTimeSeconds', 0)
            f_contest.write(f"{contest_id},{name},{div},{time_seconds}\n")
            rated_contest_ids.add(contest_id)

            for r in data['result']:
                handle = r['handle']
                old_rating = r['oldRating']
                new_rating = r['newRating']
                f_rating.write(f"{handle},{contest_id},{div},{old_rating},{new_rating}\n")
                if handle not in user_set:
                    # Write minimal fields instead of "Unknown"
                    f_users.write(f"{handle},,0,,0,0\n")
                    user_set.add(handle)

            time.sleep(0.5)
        except:
            continue

print("✅ Rated contests, users, and ratings written!")

# Fetch and filter problems only from rated contests
def fetch_problems():
    url = "https://codeforces.com/api/problemset.problems"
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json()
        if data['status'] != 'OK':
            return [], []
        return data['result']['problems'], data['result']['problemStatistics']
    except:
        return [], []

problems, stats = fetch_problems()
solves_map = {(s['contestId'], s['index']): s['solvedCount'] for s in stats}

with open('problems.txt', 'w') as f:
    for p in problems:
        contest_id = p.get('contestId')
        index = p.get('index')
        if contest_id not in rated_contest_ids or not index:
            continue
        problem_id = f"{contest_id}{index}"
        tags = ','.join(p.get('tags', [])) or 'None'
        solves = solves_map.get((contest_id, index), 0)
        f.write(f"{problem_id},{tags},-,{solves}\n")

print("✅ Problems written!")
