import requests
from bs4 import BeautifulSoup
import csv
import os

# URLs to scrape
urls = [
    "https://myrient.erista.me/files/No-Intro/Atari%20-%20Atari%202600/",
]

# Directory where this script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Path to the CSV file in the 'CSV Files' directory
csv_file = os.path.join(script_directory, 'CSV Files', 'Atari 2600.csv')

# Prepare data for CSV
csv_data = [["game_name", "rom_url", "extension"]]

def scrape_and_extract(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.find_all("tr")

    # Construct base URL dynamically from the main URL
    base_url = os.path.dirname(url) + "/"
    
    for row in rows:
        link = row.find("a")
        if link:
            game_name = link.get("title")
            rom_url = base_url + link.get("href")
            if game_name:
                # Remove the file extension from the game name
                game_name = os.path.splitext(game_name)[0]
                # Get the file extension from the ROM URL
                file_extension = os.path.splitext(rom_url)[1].lstrip('.')
                csv_data.append([f'"{game_name}"', rom_url, file_extension])

# Scrape all URLs
for url in urls:
    scrape_and_extract(url)

# Ensure the 'CSV Files' directory exists
os.makedirs(os.path.dirname(csv_file), exist_ok=True)

# Write to CSV
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(csv_data)

print(f"Data successfully written to {csv_file}")
