import threading
import time
import random
import requests
import sys
import csv
import json
from queue import Queue
from bs4 import BeautifulSoup
import category_to_csv

# Global shared variables
all_apps = set()
done_apps = set()
app_categories = {}
lock = threading.Lock()
stop_scraping = False  # Flag to signal threads to stop

# Function to fetch proxy list
def fetch_proxies(proxy_url):
    try:
        response = requests.get(proxy_url)
        return response.text.splitlines()  # Assuming proxies are listed one per line
    except Exception as e:
        print(f"Error fetching proxies: {e}")
        return []

# Scraping function
def scrape(app, proxy, thread_id):
    global app_categories
    url = f"https://apkpure.com/search?q={app}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    try:
        proxies = {
            "http": proxy, 
            # "https": proxy
        }
        response = requests.get(url, headers=headers, proxies=proxies)

        # Check if the response was successful
        if response.status_code >= 400:
            raise Exception("Request failed with status code:", response.status_code)

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract categories
        try:
            cats = soup \
                    .find("div", {"class": "first-tags"}) \
                    .find_all("a", {"class": "tag"})
            cats = [c.text.strip() for c in cats]
            if len(cats) == 0:
                cats = soup \
                    .find("div", {"class": "first-tags"}) \
                    .find_all("div", {"class": "tag"})
                cats = [c.text.strip() for c in cats]
            if not cats:
                print(f"[{thread_id}] ERROR FOR APP https://apkpure.com/search?q={app}")
                with lock:
                    app_categories[app] = []
            else:
                with lock:
                    app_categories[app] = cats
        except AttributeError as e:
            print(f"[{thread_id}] Failed to load {app}: {e}")
            with lock:
                app_categories[app] = ['__ERROR__']
        print(f"[{thread_id}] Scraped {app}")

    except requests.exceptions.RequestException as e:
        print(f"[{thread_id}] [ERROR] Request failed for {app}: {e}")
        with lock:
            app_categories[app] = ['__ERROR__']

# Worker function for each thread
def worker(queue, proxy_list, thread_id):
    global stop_scraping
    while True:
        if stop_scraping:
            break

        try:
            app = queue.get(timeout=1)  # Use timeout to periodically check for stop signal
        except Exception:
            continue  # If the queue is empty, continue checking for stop signal

        # Ensure unique proxy usage
        with lock:
            if proxy_list:
                proxy = proxy_list.pop(0)
                # print(f"[{thread_id}] Using proxy '{proxy}'")
            else:
                print(f"No more proxies available for thread {thread_id}.")
                break

        try:
            scrape(app, proxy, thread_id)
        except Exception as e:
            # print(f"[RECOVERING] [{thread_id}] Recovering from exception in 60s {e}")
            time.sleep(50 + random.randint(0, 30))
            continue

        # Return the proxy to the list after use
        with lock:
            proxy_list.append(proxy)

        queue.task_done()

# Main function to set up threading and proxy management
def main(urls, num_threads, proxy_url):
    global all_apps, done_apps, stop_scraping

    # Populate all_apps
    with open('data/selected_data.csv') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            all_apps.add(row[0].lower())

    print(f"All apps: {len(all_apps)}")
    all_apps = set(all_apps)  # Ensure uniqueness

    # Load done_apps
    with open('data/new_app_cats.csv') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            done_apps.add(row[0].lower())

    unfinished = [app for app in all_apps if app not in done_apps]
    print(f"From {len(all_apps)} apps, still missing {len(unfinished)}")

    # Fetch proxies
    proxy_list = fetch_proxies(proxy_url)

    # Initialize the queue
    queue = Queue()

    # Enqueue unfinished apps
    for app in unfinished:
        queue.put(app)

    threads = []
    for thread_id in range(num_threads):
        thread = threading.Thread(target=worker, args=(queue, proxy_list, thread_id))
        thread.start()
        threads.append(thread)

    try:
        # Block until all tasks are done
        queue.join()

    except KeyboardInterrupt:
        print("Interrupted! Closing...")
        stop_scraping = True  # Set the flag to stop scraping
        for _ in range(num_threads):
            queue.put(None)  # Signal threads to stop
        for thread in threads:
            thread.join()
        
        print("saving, do not close...")
        # Save the results
        with open(f"data/app_cats_{len(done_apps)}.json", 'w') as f:
            json.dump(app_categories, f)

        category_to_csv.main()
        print("Data written")
        
        # print("Closed")
        return

    # Stop workers
    for _ in range(num_threads):
        queue.put(None)
    for thread in threads:
        thread.join()

    # Save the results
    with open(f"data/app_cats_{len(done_apps)}.json", 'w') as f:
        json.dump(app_categories, f)

    category_to_csv.main()
    print("Data written")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python scraper.py <proxy_url> --threads <num_threads>")
        sys.exit(1)

    proxy_url = sys.argv[1]
    num_threads = int(sys.argv[sys.argv.index('--threads') + 1])

    main([], num_threads, proxy_url)
