import os
import json

def map_files_to_team_names(directory_path, output_file):
    """
    Maps JSON file names in the specified directory to the team names
    in the 'team.name' field of the JSON content, then writes the result
    to a JSON file.

    Parameters:
        directory_path (str): The path to the directory containing the JSON files.
        output_file (str): Path to the output JSON file.

    Returns:
        None
    """
    file_to_teams = {}

    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        print(filename)
        if filename.endswith(".json"):  # Process only JSON files
            file_path = os.path.join(directory_path, filename)
            
            try:
                # Open and parse the JSON file
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                # Extract team names
                team_names = set()  # Use a set to avoid duplicates
                for event in data:
                    if 'team' in event and 'name' in event['team']:
                        team_names.add(event['team']['name'])
                
                # Add to the dictionary
                file_to_teams[filename] = list(team_names)

            except Exception as e:
                # Log or handle errors
                print(f"Error processing file {filename}: {e}")

    # Write the dictionary to the output JSON file
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Ensure the directory exists
        with open(output_file, 'w', encoding='utf-8') as out_file:
            json.dump(file_to_teams, out_file, indent=4)
        print(f"Mapping successfully written to {output_file}")
    except Exception as e:
        print(f"Error writing to output file {output_file}: {e}")
        
        
        

def create_competition_to_match_mapping(directory_path, output_file):
    """
    Recursively processes all JSON files in the given directory (and its subdirectories)
    to create a mapping from competition IDs to match IDs, and saves the result to a JSON file.

    Parameters:
        directory_path (str): Path to the root directory containing match JSON files.
        output_file (str): Path to the output JSON file to save the mapping.

    Returns:
        dict: A dictionary mapping competition IDs to lists of match IDs.
    """
    competition_to_matches = {}

    # Walk through the directory and its subdirectories
    for root, _, files in os.walk(directory_path):
        for file in files:
            print(file)
            if file.endswith(".json"):  # Only process JSON files
                file_path = os.path.join(root, file)
                try:
                    # Open and load the JSON file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Check if the JSON is a list or a dictionary
                    if isinstance(data, list):
                        # Iterate through each item in the list
                        for item in data:
                            match_id = item.get("match_id")
                            competition_id = item.get("competition", {}).get("competition_id")

                            if competition_id and match_id:
                                if competition_id not in competition_to_matches:
                                    competition_to_matches[competition_id] = []
                                competition_to_matches[competition_id].append(match_id)
                    elif isinstance(data, dict):
                        # Single dictionary (as in previous logic)
                        match_id = data.get("match_id")
                        competition_id = data.get("competition", {}).get("competition_id")

                        if competition_id and match_id:
                            if competition_id not in competition_to_matches:
                                competition_to_matches[competition_id] = []
                            competition_to_matches[competition_id].append(match_id)
                    else:
                        print(f"Unexpected JSON structure in file: {file_path}")

                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

    # Write the mapping to the output JSON file
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Ensure the directory exists
        with open(output_file, 'w', encoding='utf-8') as out_file:
            json.dump(competition_to_matches, out_file, indent=4)
        print(f"Mapping successfully written to {output_file}")
    except Exception as e:
        print(f"Error writing to output file {output_file}: {e}")

    return competition_to_matches


if __name__ == "__main__":
    # Base directory path containing match JSON files
    base_directory = r"C:\Users\enmat\OneDrive\Documents\Development\Statsbomb\Data\open-data\data\matches"
    
    # Output JSON file path to save the mapping
    output_json = r".../../data/competition_to_match_mapping.json"

    # Create and save the mapping
    mapping = create_competition_to_match_mapping(base_directory, output_json)
