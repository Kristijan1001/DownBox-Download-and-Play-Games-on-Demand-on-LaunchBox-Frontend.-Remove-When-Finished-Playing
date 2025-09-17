import requests
from bs4 import BeautifulSoup
import csv
import os
import concurrent.futures
import urllib.parse

# URLs to scrape
urls = [
    "https://archive.org/download/PS2-part1-CHD-Arquivista",
    "https://archive.org/download/PS2-part2-CHD-Arquivista",
    "https://archive.org/download/PS2-part3-CHD-Arquivista",
    "https://archive.org/download/PS2-EU-part1-CHD-Arquivista",
    "https://archive.org/download/PS2-EU-part2-CHD-Arquivista",
    "https://archive.org/download/PS2-EU-part3-CHD-Arquivista",
    "https://archive.org/download/PS2-EU-part4-CHD-Arquivista",
    "https://archive.org/download/PS2-EU-part5-CHD-Arquivista",
    "https://archive.org/download/PS2-part1-Japan-CHD-Arquivista",
    "https://archive.org/download/PS2-part2-Japan-CHD-Arquivista",
    "https://archive.org/download/PS2-part3-Japan-CHD-Arquivista",
    "https://archive.org/download/PS2-part4-Japan-CHD-Arquivista",
    "https://archive.org/download/PS2-part5-Japan-CHD-Arquivista"
]

# Directory where this script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Path to the CSV file in the 'CSV Files' directory
csv_directory = os.path.join(script_directory, 'CSV Files')
os.makedirs(csv_directory, exist_ok=True)
csv_file = os.path.join(csv_directory, 'Sony Playstation 2.csv')

# Prepare data for CSV
csv_data = [["game_name", "rom_url", "extension", "subfolder"]]

def decode_url(url):
    return urllib.parse.unquote(url)

def scrape_and_extract(url, base_folder=""):
    print(f"Scraping URL: {url} | Base folder: {base_folder}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find_all("tr")

        tasks = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for row in rows:
                link = row.find("a")
                if link:
                    href = link.get("href")
                    decoded_href = decode_url(href)
                    if href.endswith("/") and not href.startswith("../"):
                        # Recursively scrape subfolders
                        subfolder = os.path.join(base_folder, decoded_href.strip('/'))
                        print(f"Found subfolder: {subfolder}")
                        task = executor.submit(scrape_and_extract, os.path.join(url, href), subfolder)
                        tasks.append(task)
                    else:
                        # Check if the file is a .chd or .zip
                        if href.endswith(".chd") or href.endswith(".zip"):
                            game_name = link.get("href")
                            rom_url = os.path.join(url, href)
                            if game_name:
                                # Decode URL-encoded strings
                                game_name = decode_url(game_name)
                                rom_url = decode_url(rom_url)
                                # Remove the file extension from the game name
                                game_name = os.path.splitext(game_name)[0]
                                # Get the file extension from the ROM URL
                                file_extension = os.path.splitext(rom_url)[1].lstrip('.')
                                print(f"Found file: {game_name} | URL: {rom_url} | Extension: {file_extension} | Subfolder: {base_folder}")
                                csv_data.append([f'"{game_name}"', rom_url, file_extension, base_folder])

            # Ensure all tasks are completed
            for task in concurrent.futures.as_completed(tasks):
                task.result()

    except Exception as e:
        print(f"Error while scraping URL: {url} | Error: {e}")

# Scrape all URLs
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(scrape_and_extract, url) for url in urls]
    for future in concurrent.futures.as_completed(futures):
        future.result()

# Write to CSV
try:
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)
    print(f"Data successfully written to {csv_file}")
except Exception as e:
    print(f"Error writing to CSV file: {csv_file} | Error: {e}")
