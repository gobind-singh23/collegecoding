import requests
import json

def get_user_info(handle):
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    response = requests.get(url)
    # print(len(response.json()['result']['rows']))
    if response.status_code == 200:
        data = response.json()
        print(data)
    
    return None

if __name__ == "__main__":
    handle = "wwreckker"
    info = get_user_info(handle)
    
    # if info:
        # print(json.dumps(info, indent=4))
