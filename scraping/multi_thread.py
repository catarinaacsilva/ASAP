import os
import threading
import time
import random
import requests
import sys
import csv
import json
import glob
from queue import Queue
from bs4 import BeautifulSoup
import scraping.category_to_csv
from scraping.apk_info import extract_apk_info

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
def scrape(app, proxy=None, thread_id=0):
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

def apk_worker(queue, proxy_list, thread_id):
    global stop_scraping
    while True:
        with lock:
            if queue.empty():
                stop_scraping = True

        if stop_scraping:
            print(f"[{thread_id}] STOPPING")
            break

        try:
            app = queue.get(timeout=1)  # Use timeout to periodically check for stop signal
            if app is None:
                break
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
            info = extract_apk_info(app)
            with lock:
                print(f"[{thread_id}] got info on '{info['app_id']} [{len(app_categories)+1}]")
                app_categories[app] = info
                
        except Exception as e:
            t = 50 + random.randint(0, 30)
            print(f"[RECOVERING] [{thread_id}] Recovering from exception in {t}s {e}")
            time.sleep(t)
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

        scraping.category_to_csv.main()
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

    scraping.category_to_csv.main()
    print("Data written")

def scrape_local_apks(num_threads, proxy_url):
    global all_apps, done_apps, stop_scraping

    # Populate all_apps
    if not os.path.exists("dataset/apk/to_analyse.json"):
        os.mknod("dataset/apk/to_analyse.json")
    with open("dataset/apk/to_analyse.json") as f:
        all_apps = json.loads(f.read()).values()
        all_apps = {f"dataset/apk/{f}" for f in all_apps}

    print(f"All apps: {len(all_apps)}")
    # all_apps = set(all_apps)  # Ensure uniqueness

    # Load done_apps
    if not os.path.exists("dataset/apk/apk_info.csv"):
        os.mknod("dataset/apk/apk_info.csv")
    with open("dataset/apk/apk_info.csv") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            done_apps.add(row[0])

    unfinished = [app for app in all_apps if app not in done_apps]
    print(f"From {len(all_apps)} apps, still missing {len(unfinished)}, {len(done_apps)=}")

    # Fetch proxies
    proxy_list = fetch_proxies(proxy_url)

    # Initialize the queue
    queue = Queue()

    # Enqueue unfinished apps
    for app in unfinished:
        queue.put(app)

    threads = []
    for thread_id in range(num_threads):
        thread = threading.Thread(target=apk_worker, args=(queue, proxy_list, thread_id))
        thread.start()
        threads.append(thread)

    try:
        # Block until all tasks are done
        queue.join()
        print("ALL DONE!")

    except KeyboardInterrupt:
        print("Interrupted! Closing...")
        stop_scraping = True  # Set the flag to stop scraping
        for _ in range(num_threads):
            queue.put(None)  # Signal threads to stop
        for thread in threads:
            thread.join()
    finally:
        print("saving, do not close...")
        # Save the results
        with open(f"dataset/apk/app_info_{len(done_apps)}.json", 'w') as f:
            json.dump(app_categories, f)

        # category_to_csv.main()
        apps = list(app_categories.keys())
        with open('dataset/apk/apk_info.csv', newline='') as f:
            reader = csv.reader(f)
            processed_apks = [e[0] for e in reader]

        with open('dataset/apk/apk_info.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for app in apps + processed_apks:
                csv_writer.writerow([app])

        print("Data written")
        
        # print("Closed")
        return

    # Stop workers
    for _ in range(num_threads):
        queue.put(None)
    for thread in threads:
        thread.join()

    # Save the results
    with open(f"dataset/apk/app_info_{len(done_apps)}.json", 'w') as f:
        json.dump(app_categories, f)


# https://raw.githubusercontent.com/TheSpeedX/PROXY-List/refs/heads/master/http.txt
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python multi_thread.py <proxy_url> <num_threads>")
        sys.exit(1)
    
    proxy_url = sys.argv[1]
    num_threads = int(sys.argv[2])
    
    scrape_local_apks(num_threads, proxy_url)
