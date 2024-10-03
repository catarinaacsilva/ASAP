import subprocess
import json
import re
import requests
from bs4 import BeautifulSoup

def run_command(command):
    """Run shell command and capture output."""
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout

def extract_permissions(apk_file):
    """Extract and clean permissions from the APK."""
    # Run aapt to dump permissions
    aapt_output = run_command(['aapt', 'dump', 'permissions', apk_file])
    
    # Extract permissions, stripping out package names, and cleaning quotes
    permissions = re.findall(r'uses-permission: name=\'([^\']+)\'', aapt_output)
    cleaned_permissions = [perm.split('.')[-1] for perm in permissions]  # Get only the last part of permission
    return cleaned_permissions

def extract_app_id(apk_file):
    """Extract the app ID (package name) from the APK."""
    aapt_output = run_command(['aapt', 'dump', 'badging', apk_file])
    
    # Find the app ID (package name)
    match = re.search(r'package: name=\'([^\']+)\'', aapt_output)
    if match:
        return match.group(1)
    return None

def generate_play_store_url(app_id):
    """Generate the Play Store URL based on the app ID."""
    if app_id:
        return f"https://play.google.com/store/apps/details?id={app_id}"
    return None

def fetch_app_categories(play_store_url):
    """Fetch the app's Play Store page and extract all categories."""
    categories = []
    try:
        response = requests.get(play_store_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            category_links = soup.find_all('a', href=re.compile(r'^/store/apps/category/'))
            categories = [link['href'].split('/')[-1] for link in category_links]
        else:
            print(f"Failed to fetch the page, status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error fetching app page: {e}")
    
    return categories

def extract_apk_info(apk_file):
    """Extract app info from an APK and return as JSON."""
    app_id = extract_app_id(apk_file)
    permissions = extract_permissions(apk_file)
    play_store_url = generate_play_store_url(app_id)

    categories = fetch_app_categories(play_store_url) if play_store_url else []

    result = {
        "app_id": app_id,
        "play_store_url": play_store_url,
        "permissions": permissions,
        "categories": categories
    }

    return result
