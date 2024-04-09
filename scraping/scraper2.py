import requests
from bs4 import BeautifulSoup

# Set up the headers dictionary with fake but realistic values
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

# Define the URL of the site you want to scrape
url = "https://apkpure.com/search?q=La+Barbieria+di+Foligno"

# Make the GET request while sending the custom headers
response = requests.get(url, headers=headers)

# Check if the response was successful (status code < 400)
if response.status_code >= 400:
    print("Request failed with status code:", response.status_code)
    sys.exit(1)

with open("tmp.html", 'w') as f:
    f.write(response.text) 

soup = BeautifulSoup(response.content, 'html.parser')

cats = soup \
        .find("div", {"class": "first-tags"}) \
        .find_all("a", {"class": "tag"})
cats = [c.text.strip() for c in cats]
if len(cats) == 0:
    cats = soup \
        .find("div", {"class": "first-tags"}) \
        .find_all("div", {"class": "tag"})
    cats = [c.text.strip() for c in cats]


print(cats)