from datetime import datetime
import json

def date_type(datestr):
    try:
        return datetime.strptime(datestr, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f'Bad date argument: {datestr} (Excepted YYYY-MM-DD)')


def load_subdirectory(subdirectory_name):
    try:
        file_path = f'{subdirectory_name}/directory.json'
        with open(file_path, 'r') as f:
            return json.loads(f.read())
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{file_path}'. The file may be invalid.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
