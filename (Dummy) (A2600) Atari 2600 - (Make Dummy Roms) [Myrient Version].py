import csv
import os

# Directory where this script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Path to the CSV file (assuming it's in the 'CSV Files' directory within the script directory)
csv_file = os.path.join(script_directory, 'CSV Files', 'Atari 2600.csv')

# Directory to save the fake ROMs (going up one directory and then to 'Games/Atari 2600')
rom_directory = os.path.join(script_directory, '..', 'Games', 'Atari 2600')

# Function to create an empty file with specified extension
def create_empty_file(file_path, extension):
    # Create an empty file with the specified extension
    open(file_path, 'a').close()

# Read the CSV file and create empty files with specified extensions
with open(csv_file, 'r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        game_name = row['game_name'].strip('"')  # Remove double quotes from game name
        extension = row['extension'].strip()     # Get extension from CSV

        # Construct the path to save the fake ROM
        fake_rom_path = os.path.join(rom_directory, f"{game_name}.{extension}")

        # Create the empty file
        create_empty_file(fake_rom_path, extension)
        print(f"Created empty fake ROM: {fake_rom_path}")
