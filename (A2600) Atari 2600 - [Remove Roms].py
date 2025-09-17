import os
import sys
import re

# Directory where this script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Define the base path where games are stored (relative to script directory)
games_directory = os.path.join(script_directory, '..', 'Games', 'Atari 2600')

# Resolve the relative path to an absolute path
games_directory = os.path.abspath(games_directory)

# Print a newline to create a break between the command and the prompt
print()

# Get the game name from the command line arguments
if len(sys.argv) != 2:
    print("Usage: python remove_rom.py <game_name>")
    sys.exit(1)

game_name = sys.argv[1]

# Function to remove a ROM and create a fake ROM
def remove_rom(game_name):
    matching_files = [f for f in os.listdir(games_directory) if os.path.isfile(os.path.join(games_directory, f)) and f.startswith(game_name + '.')]

    if not matching_files:
        print(f"No ROM file found for {game_name}.")
        return False

    # Assuming there's only one matching file
    rom_filename = matching_files[0]
    file_extension = os.path.splitext(rom_filename)[1]

    # Construct full paths
    rom_path = os.path.join(games_directory, rom_filename)
    fake_rom_path = os.path.join(games_directory, f"{game_name}{file_extension}")

    # Ask for confirmation
    confirmation = input(f"Are you sure you want to remove the ROM for {game_name}? (Y/N): ").strip().lower()

    if confirmation != 'y' and confirmation != 'yes':
        print("Operation canceled.")
        return False

    # Remove the ROM file
    try:
        os.remove(rom_path)
        print(f"Removed downloaded ROM for {rom_filename}")

        # Create a fake ROM (empty file) with the same name and extension
        try:
            open(fake_rom_path, 'a').close()  # Create an empty file
            print(f"Created empty fake ROM: {fake_rom_path}")
        except Exception as e:
            print(f"Failed to create empty fake ROM: {fake_rom_path}. Error: {e}")

    except Exception as e:
        print(f"Failed to remove ROM file: {rom_path}. Error: {e}")

    return True

# Remove the first disc
if not remove_rom(game_name):
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
        
        # Remove the next disc
        if not remove_rom(next_game_name):
            break
else:
    base_name = game_name
    disc_number = 1
    
    while True:
        disc_number += 1
        next_game_name = f"{base_name} Disc {disc_number}"
        
        # Remove the next disc
        if not remove_rom(next_game_name):
            break
