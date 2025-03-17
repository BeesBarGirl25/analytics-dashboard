import json
import pandas as pd

def load_and_normalize_json(file_path):
    """Load a JSON file and normalize it into a pandas DataFrame."""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return pd.json_normalize(data)


