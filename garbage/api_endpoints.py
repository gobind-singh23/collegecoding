import requests
import time
import ast  # to safely parse the list from file

def read_organization_list(filepath):
    with open(filepath, "r") as f:
        content = f.read()
        organizations = ast.literal_eval(content)  # safely parse list from file
    return set(organizations)  # no lowercasing or modifications

def get_contest_list():
    url = "https://codeforces.com/api/contest.list"
    resp = requests.get(url)
    data = resp.json()
    if data["status"] != "OK":
        raise Exception("Failed to get contest list")
    return [contest for contest in data["result"] if contest["phase"] == "FINISHED"]

def get_contest_standings(contest_id):
    url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=5000"
    resp = requests.get(url)
    data = resp.json()
    if data["status"] != "OK":
        raise Exception(f"Failed to get standings for contest {contest_id}")
    return data["result"]["rows"]

def extract_iit_handles(rows, organization_set):
    handles = set()
    for row in rows:
        party = row["party"]
        members = party["members"]
        for member in members:
            if "organization" in member and member["organization"]:
                org_name = member["organization"]
                if org_name in organization_set:
                    handles.add(member["handle"])
    return handles

def main():
    organization_set = read_organization_list("organization_list.txt")
    print(organization_set)
    contests = get_contest_list()
    contests = contests[:1]  # Last 500 contests
    print(contests)
    all_handles = set()

    for idx, contest in enumerate(contests):
        contest_id = contest["id"]
        print(f"Processing contest {idx+1}/5 - ID: {contest_id}")

        try:
            rows = get_contest_standings(contest_id)
            handles = extract_iit_handles(rows, organization_set)
            all_handles.update(handles)
        except Exception as e:
            print(f"Failed to process contest {contest_id}: {e}")

        # Respect API rate limits
        time.sleep(1.5)

    # Save results
    with open("iit_handles.txt", "w") as f:
        for handle in sorted(all_handles):
            f.write(handle + "\n")

    print(f"Collected {len(all_handles)} unique handles.")

if __name__ == "__main__":
    main()
