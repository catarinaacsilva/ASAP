import json
import os.path

import requests
from bs4 import BeautifulSoup

N_PAGES = 3

# GET CATEGORIES

URL = "https://f-droid.org/en/packages/"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

if not os.path.exists("data/categories.txt"):
    links = [f"https://f-droid.org{a['href']}\n" for a in soup.find_all("a") if a["href"].startswith("/en/categories/")]

    with open("data/categories.txt", 'w') as f:
        f.writelines(links)
else:
    with open("data/categories.txt") as f:
        links = f.read().split('\n')

if N_PAGES > 0:
    old = links
    links = []
    for n in range(N_PAGES):
        for l in old:
            links.append(f"{l}{n + 2}/index.html")

APPS: {str: {str: [str]}} = {cat: {} for cat in links}

# GET APPS IN EACH CATEGORY

for cat_url in links:
    try:
        page = requests.get(cat_url)
    except requests.exceptions.MissingSchema:
        print(f"Failed to load {cat_url}")
        continue
    soup = BeautifulSoup(page.content, "html.parser")

    try:
        app_urls = [
            f"https://f-droid.org{a['href']}" for a in
            soup
            .find("div", {"id": "package-list"})
            .find_all("a", {"class": "package-header"})
        ]
    except AttributeError as e:
        print(f"Failed to load {cat_url}: {e.args}")
        with open(f"./err/{cat_url.replace('/', '_')}", 'w') as f:
            f.write(str(soup))
        continue

    for app in app_urls:
        APPS[cat_url][app] = []

    for app_url in app_urls:
        page = requests.get(app_url)
        soup = BeautifulSoup(page.content, "html.parser")

        try:
            permissions = [
                p.find("div", {"class": "permission-label"}).text
                for p in soup
                .find("li", {"class": "package-version", "id": "latest"})
                .find_all("li", {"class": "permission"})
            ]
        except AttributeError as e:
            print(f"Failed to load {app_url}: {e.args}")
            with open(f"./err/{app_url.replace('/', '_')}", 'w') as f:
                f.write(str(soup))
            continue

        APPS[cat_url][app_url] = permissions

with open("dataset_more.json", 'w') as f:
    f.write(json.dumps(APPS))
