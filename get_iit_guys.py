from college_map import map_single_organization
import time 
import requests
def get_user_info(handles):
    """
    Fetch user information (including organization) for a list of handles.
    Max 10000 handles per call as per Codeforces API limit.
    """
    handle_str = ';'.join(handles)
    url = f"https://codeforces.com/api/user.info?handles={handle_str}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['status'] != 'OK':
            print(f"Error fetching user info")
            return []
        return data['result']
    except Exception as e:
        print(f"Exception fetching user info: {e}")
        return []

def get_valid_participants_with_org(participants):
    """
    Given a set of participants, returns a list of (handle, organization) where organization is known.
    """
    valid_participants = []
    participants = list(participants)

    batch_size = 1000  # API allows a big number, but small batch is safer
    for i in range(0, len(participants), batch_size):
        batch = participants[i:i+batch_size]
        user_info_list = get_user_info(batch)
        
        for user in user_info_list:
            organization = user.get('organization', '')
            mapped_org = map_single_organization(organization)
            if mapped_org != 'Unknown':
                valid_participants.append({
                    'handle': user['handle'],
                    'organization': organization,
                    'mapped_organization': mapped_org
                })
        
        time.sleep(0.5)  # Be nice to Codeforces API

    return valid_participants