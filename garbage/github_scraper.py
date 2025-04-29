import requests
from bs4 import BeautifulSoup

def scrape_github_profile(username):
    url = f"https://github.com/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch profile: {username}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract Name
    name_tag = soup.find('span', class_='p-name')
    name = name_tag.text.strip() if name_tag else "No name found"
    
    # Extract Bio
    bio_tag = soup.find('div', class_='p-note')
    bio = bio_tag.text.strip() if bio_tag else "No bio found"
    
    # Extract Location
    location_tag = soup.find('span', class_='p-label')
    location = location_tag.text.strip() if location_tag else "No location found"
    
    return {
        "Username": username,
        "Name": name,
        "Bio": bio,
        "Location": location
    }

from googlesearch import search

def search_github_profiles(company, university, num_results=10):
    query = f'site:github.com "{company}" "{university}"'
    print(f"Searching Google for: {query}")
    
    github_profiles = []
    for url in search(query, num_results=num_results):
        if "github.com/" in url:
            username = url.split("github.com/")[1].split('/')[0]
            github_profiles.append(username)
    
    return github_profiles

# # Example usage
# if __name__ == "__main__":
#     company = "Google"
#     university = "IIT Bombay"
#     profiles = search_github_profiles(company, university, num_results=10)
#     print(profiles)


# Example usage
if __name__ == "__main__":
    company = "Google"
    university = "IIT Bombay"
    profiles = search_github_profiles(company, university, num_results=10)
    # usernames = ["torvalds", "gvanrossum", "sindresorhus"]  # You can replace with whatever
    for user in profiles:
        profile = scrape_github_profile(user)
        print(profile)
