import csv
import os
import requests
import sys
from urllib.parse import urlparse
from tqdm import tqdm
import threading
import tempfile
import shutil
import time
import signal
import re

# Directory where this script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Path to the CSV file (assuming it's in the 'CSV Files' directory)
csv_file = os.path.join(script_directory, 'CSV Files', 'Atari 2600.csv')

# Directory to save the downloaded ROMs (relative to script directory)
rom_directory = os.path.join(script_directory, '..', 'Games/Atari 2600')

# Directory to save the temporary parts
temp_root_directory = os.path.join(script_directory, 'Temp')

# Number of threads to use for downloading
num_threads = 20

# Global flag to signal threads to stop
stop_flag = threading.Event()

# Global variable for temporary directory
temp_dir = None

# Global list for threads
threads = []

# Global variable to track if we're already handling an interrupt
handling_interrupt = False

# Function to handle CTRL+C
def signal_handler(signum, frame):
    global handling_interrupt
    if handling_interrupt:
        print("\nForced exit. Some temporary files may not be cleaned up.")
        os._exit(1)
    
    handling_interrupt = True
    print("\nCTRL+C detected. Cleaning up and exiting...")
    stop_flag.set()
    
    # Wait for threads to finish with a timeout
    for thread in threads:
        thread.join(timeout=1)  # Wait up to 1 second for each thread
    
    cleanup()
    sys.exit(1)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Function to clean up temporary files and directory
def cleanup():
    global temp_dir
    if temp_dir and os.path.exists(temp_dir):
        print("Cleaning up temporary files...")
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            print("Cleanup completed.")

# Function to download a part of the file with retry logic
def download_part(url, start, end, part_num, results, progress_bar, max_retries=3):
    headers = {'Range': f'bytes={start}-{end}'}
    retry_count = 0
    
    while retry_count < max_retries and not stop_flag.is_set():
        try:
            with requests.get(url, headers=headers, stream=True) as response:
                if response.status_code in (200, 206):
                    part_path = os.path.join(temp_dir, f"part{part_num}")
                    with open(part_path, 'wb') as part_file:
                        for chunk in response.iter_content(chunk_size=8192):
                            if stop_flag.is_set():
                                return
                            part_file.write(chunk)
                            progress_bar.update(len(chunk))
                    results[part_num] = part_path
                    return
                else:
                    print(f"Failed to download part {part_num}. Status code: {response.status_code}")
                    results[part_num] = None
                    return
        except requests.exceptions.RequestException as e:
            print(f"Error downloading part {part_num}: {e}")
            retry_count += 1
        
        if stop_flag.is_set():
            return
    
    print(f"Failed to download part {part_num} after {max_retries} retries.")
    results[part_num] = None

# Function to download a ROM
def download_rom(game_name):
    rom_url = ""

    # Read the CSV file to get the URL for the game
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['game_name'].strip('"') == game_name:
                rom_url = row['rom_url'].replace("\\", "/")  # Replace backslashes with forward slashes
                break

    # Check if ROM URL is found
    if not rom_url:
        print(f"ROM URL not found for game: {game_name}")
        return False

    print(f"ROM URL found: {rom_url}")

    # Ask for confirmation with a break line
    confirmation = input(f"\nAre you sure you want to download the ROM for {game_name}? (Y/N): ").strip().lower()
    if confirmation != 'y' and confirmation != 'yes':
        print("Operation canceled.")
        return False

    print("\nDownloading ROM/Game. Please wait a minute. If it takes too long, relaunch the game.\n")

    # Fetch the filename and extension from the URL
    parsed_url = urlparse(rom_url)
    filename = os.path.basename(parsed_url.path)
    filename_parts = filename.split('.')
    file_extension = filename_parts[-1] if len(filename_parts) > 1 else ''

    # Define paths relative to script location
    rom_filename = f"{game_name}.{file_extension}"
    rom_path = os.path.join(rom_directory, rom_filename)

    # Create the directory if it doesn't exist
    os.makedirs(rom_directory, exist_ok=True)

    # Create a temporary directory for the parts
    global temp_dir
    temp_dir = tempfile.mkdtemp(dir=temp_root_directory)

    try:
        # Initial GET request to verify range support and get the total file size
        response = requests.get(rom_url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            supports_range = 'bytes' in response.headers.get('accept-ranges', '')

            if not supports_range:
                print(f"The server does not support range requests.")
                return False
        else:
            print(f"Failed to connect to server. Status code: {response.status_code}")
            return False

        # Set a smaller part size for more dynamic distribution
        part_size = 5 * 1024 * 1024  # 5MB per part
        num_parts = (total_size + part_size - 1) // part_size  # Calculate number of parts

        results = [None] * num_parts

        # Create the progress bar
        with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as progress_bar:
            # Create and start threads with a small delay between each start
            for i in range(num_parts):
                start = i * part_size
                end = start + part_size - 1 if i < num_parts - 1 else total_size - 1
                thread = threading.Thread(target=download_part, args=(rom_url, start, end, i, results, progress_bar))
                threads.append(thread)
                thread.start()
                time.sleep(0.1)  # Small delay to reduce initial CPU load

            # Wait for all threads to finish or for stop_flag to be set
            for thread in threads:
                thread.join()

        if stop_flag.is_set():
            print("Download interrupted.")
            return False

        # Combine parts into a single file
        with open(rom_path, 'wb') as outfile:
            for part_path in results:
                if part_path and os.path.exists(part_path):
                    with open(part_path, 'rb') as infile:
                        outfile.write(infile.read())

        print(f"\nROM downloaded successfully: {rom_path}")
        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        # Clean up the temporary directory
        cleanup()

# Main script execution
if __name__ == "__main__":
    # Get the game name from the command line arguments
    if len(sys.argv) != 2:
        print("Usage: python download_rom.py <game_name>")
        sys.exit(1)

    game_name = sys.argv[1]

    # Download the first disc
    if not download_rom(game_name):
        sys.exit(1)

    # Check if the game name includes "Disc" and iterate through possible disc numbers
    disc_pattern = re.compile(r"(.*)(Disc (\d+))(.*)")
    match = disc_pattern.match(game_name)
    if match:
        base_name, disc_part, disc_number, rest = match.groups()
        disc_number = int(disc_number)
        
        while True:
            disc_number += 1
            next_game_name = f"{base_name}Disc {disc_number}{rest}"
            
            # Download the next disc
            if not download_rom(next_game_name):
                break
    else:
        base_name = game_name
        disc_number = 1
        
        while True:
            disc_number += 1
            next_game_name = f"{base_name} Disc {disc_number}"
            
            # Download the next disc
            if not download_rom(next_game_name):
                break
