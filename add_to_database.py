import requests
from pymongo import MongoClient, UpdateOne
from extract_div import extract_division
from collections import defaultdict

POPULAR_TAGS = [
    'implementation', 'greedy', 'dp', 'math', 'brute force',
    'data structures', 'binary search', 'constructive algorithms',
    'dfs and similar', 'sorting'
]

def update_users_from_api(valid_participants):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['coding_platform']
    users_col = db['users']

    for entry in valid_participants:
        handle = entry.get('handle')
        mapped_org = entry.get('mapped_organization')
        
        try:
            # API request
            response = requests.get(f"https://codeforces.com/api/user.info?handles={handle}")
            response.raise_for_status()
            data = response.json()

            if data['status'] != 'OK' or not data.get('result'):
                print(f"Skipping {handle}: Invalid API response")
                continue

            user_data = data['result'][0]

            # Construct user document
            user_doc = {
                'handle': user_data.get('handle'),
                'organization': mapped_org,  # Use mapped_organization instead of API's 'organization'
                'rating': user_data.get('rating'),
                'college': mapped_org,       # Assuming college is also mapped
                'lastOnlineTimeSeconds': user_data.get('lastOnlineTimeSeconds'),
                'maxRating': user_data.get('maxRating'),
            }

            # Insert or update user
            users_col.update_one(
                {'handle': handle},
                {'$set': user_doc},
                upsert=True
            )
            print(f"Updated: {handle}")
        
        except Exception as e:
            print(f"Error processing {handle}: {e}")


def update_contests(contests_list):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['coding_platform']
    contests_col = db['contests']

    for contest in contests_list:
        try:
            division = extract_division(contest['name'])

            contest_doc = {
                'contestId': contest['id'],
                'name': contest['name'],
                'div': division,
                'time': contest['startTimeSeconds']
            }

            # Upsert into contests table
            contests_col.update_one(
                {'contestId': contest['id']},
                {'$set': contest_doc},
                upsert=True
            )
            print(f"Updated contest: {contest['name']}")

        except Exception as e:
            print(f"Error updating contest {contest.get('id')}: {e}")


def update_problems_from_participants(valid_participants):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['coding_platform']
    problems_col = db['problems']

    # === 🔧 Step 1: Drop all existing indexes except _id ===
    try:
        indexes = problems_col.index_information()
        for index_name in indexes:
            if index_name != '_id_':
                problems_col.drop_index(index_name)
        print("✅ Cleared existing indexes on 'problems'")
    except Exception as e:
        print(f"⚠️ Failed to drop indexes: {e}")

    # === ✅ Step 2: Create the correct composite unique index ===
    try:
        problems_col.create_index(
            [('problemId', 1), ('organisation', 1)],
            unique=True
        )
        print("✅ Created composite unique index on (problemId, organisation)")
    except Exception as e:
        print(f"⚠️ Failed to create index: {e}")

    # === 🚀 Step 3: Process valid participants ===
    for participant in valid_participants:
        handle = participant.get('handle')
        organisation = participant.get('mapped_organization')

        try:
            response = requests.get(f"https://codeforces.com/api/user.status?handle={handle}")
            response.raise_for_status()
            data = response.json()

            if data['status'] != 'OK':
                print(f"⏭️ Skipping {handle}: Invalid API response")
                continue

            submissions = data.get('result', [])
            solved_problems = set()

            for submission in submissions:
                if submission.get('verdict') != 'OK':
                    continue

                problem = submission.get('problem', {})
                contest_id = problem.get('contestId')
                index = problem.get('index')

                if not contest_id or not index:
                    continue  # Skip malformed entries

                problem_id = f"{contest_id}{index}"
                key = (problem_id, organisation)

                if key in solved_problems:
                    continue  # Already counted for this user

                solved_problems.add(key)

                problems_col.update_one(
                    {'problemId': problem_id, 'organisation': organisation},
                    {
                        '$inc': {'solves': 1},
                        '$setOnInsert': {
                            'tag': problem.get('tags', []),
                            'organisation': organisation
                        }
                    },
                    upsert=True
                )

            print(f"✅ Processed: {handle}")

        except Exception as e:
            print(f"❌ Error processing {handle}: {e}")


import requests
from pymongo import MongoClient
from collections import defaultdict

POPULAR_TAGS = [
    'implementation', 'greedy', 'dp', 'math', 'brute force',
    'data structures', 'binary search', 'constructive algorithms',
    'dfs and similar', 'sorting'
]

def update_tags_table(valid_participants):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['coding_platform']
    contests_col = db['contests']
    tags_col = db['tags']

    # 🧹 Drop existing indexes
    tags_col.drop_indexes()

    # ✅ Create correct unique index
    tags_col.create_index([('userId', 1), ('div', 1)], unique=True)

    for participant in valid_participants:
        handle = participant['handle']
        print(f"Processing {handle}...")

        try:
            response = requests.get(f"https://codeforces.com/api/user.status?handle={handle}")
            response.raise_for_status()
            submissions = response.json().get('result', [])
        except Exception as e:
            print(f"Error fetching submissions for {handle}: {e}")
            continue

        seen_problems = set()
        tag_counts_by_div = defaultdict(lambda: defaultdict(int))

        for submission in submissions:
            if submission.get('verdict') != 'OK':
                continue

            problem = submission.get('problem', {})
            contestId = problem.get('contestId')
            index = problem.get('index')
            if not contestId or not index:
                continue

            problemId = f"{contestId}{index}"
            if problemId in seen_problems:
                continue
            seen_problems.add(problemId)

            # Get div from contests table
            contest_doc = contests_col.find_one({'contestId': contestId})
            if not contest_doc:
                continue
            div = contest_doc.get('div')
            if not div:
                continue

            tags = problem.get('tags', [])
            for tag in tags:
                if tag in POPULAR_TAGS:
                    tag_key = tag.replace(" ", "_")
                    tag_counts_by_div[div][tag_key] += 1

        # Insert/update each (userId, div) individually
        for div, tag_counts in tag_counts_by_div.items():
            update_doc = {
                'userId': handle,
                'div': div,
            }
            for tag in POPULAR_TAGS:
                tag_key = tag.replace(" ", "_")
                update_doc[tag_key] = tag_counts.get(tag_key, 0)

            tags_col.update_one(
                {'userId': handle, 'div': div},
                {'$set': update_doc},
                upsert=True
            )

    print("✅ Tags table updated (iteratively, with correct index).")



