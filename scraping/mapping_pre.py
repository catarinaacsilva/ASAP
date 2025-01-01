# https://noxtoolbox.com/androidmanifest/
from bs4 import BeautifulSoup

# Sample HTML content (you can replace this with reading from a file or URL)
with open("/tmp/table.html") as f:
    html_content = f.read()

def extract_permissions(html):
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Create a dictionary to store permission-to-name mapping
    permission_map = {}

    # Find all table rows
    rows = soup.find_all('tr')
    
    # Skip the first row (header) and loop through the rest
    for row in rows[1:]:  # Skip the header row at index 0
        cols = row.find_all('td')
        
        if len(cols) >= 2:
            permission = cols[0].text.strip().split('.')[-1]  # First column (Permission)
            name = cols[1].text.strip()  # Second column (Name)
            permission_map[permission] = name
    
    return permission_map

# Example usage
permission_to_name = extract_permissions(html_content)

# Print the mapping
for permission, name in permission_to_name.items():
    # print(f"Permission: {permission}, Name: {name}")
    print(f"\"{permission}\": \"{name}\",")
