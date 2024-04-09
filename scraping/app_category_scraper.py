import csv
import json

import requests
from bs4 import BeautifulSoup

import category_to_csv

all_apps = []

# already_seen = 0
with open('data/selected_data.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        # if row[1].lower() in all_apps:
            # already_seen += 1
            # print(row[1])
        all_apps.append(row[1].lower())

print(len(all_apps))
all_apps = set(all_apps[1:])
print(len(all_apps))
# print(len(all_apps), already_seen, len(all_apps) + already_seen)

done_apps = set()

with open('data/new_app_cats.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        done_apps.add(row[0].lower())

unfinished = [app for app in all_apps if app not in done_apps]

app_categories = {}

# with open('data/scraper.out') as f:
#      count = sum(1 for ln in f if ln.strip() == '----')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

# print(f"{count=} {len(all_apps)=} {len(unfinished)=}")
print(f"{len(all_apps)=} {len(unfinished)=}")

iter_i = 0
for app in unfinished:
    try:
        url = f"https://apkpure.com/search?q={app}"
        print(url)

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
        if len(cats) == 0:
            print(f"ERROR FOR APP https://apkpure.com/search?q={app}")
            app_categories[app] = []
        else:
            app_categories[app] = cats
        print(app)
        print('----')
        iter_i += 1
    except KeyboardInterrupt:
        break
    except AttributeError as e:
        print(e)
        print(f"Failed to load {app}")
        print('----')
        app_categories[app] = []
    except Exception as e:
        print(e)
        print(f"[CRITICAL] Failed to load {app}")
        print('----')
        app_categories[app] = []

with open(f"data/app_cats_{len(done_apps)}_{iter_i}.json", 'w') as f:
    f.write(json.dumps(app_categories))
category_to_csv.main()

print("Data written")
