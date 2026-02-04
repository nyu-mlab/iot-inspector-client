import os
from functools import lru_cache

# This file aims to provide a set of functions to 
from difflib import SequenceMatcher

# This files aims to provide a set of functions to 
# perform model selection for a device based on the
# data available in the database.

@lru_cache(maxsize=128)
def import_models():
    # Import all models from the models directory
    # and return them as a list of models

    # Note: The models are stored in the following directory
    # <project_dir>/models/binary/rf/<model_name>
    models_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'models', 'binary', 'rf')

    #  Check if the models directory exists
    if not os.path.exists(models_dir):
        return []

    model_folders = [name for name in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, name))]
    return model_folders


def is_close_match(str1, str2, threshold=0.75):
    match_score = SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    return 1 if match_score > threshold else 0

@lru_cache(maxsize=128)
def find_best_match(device_name, model_names=None, threshold=0.75):
    best_match = None
    highest_score = 0

    if not model_names:
        model_names = import_models()

    for model_name in model_names:
        match_score = SequenceMatcher(None, device_name.lower(), model_name.lower()).ratio()
        if match_score > highest_score:
            highest_score = match_score
            best_match = model_name

    if highest_score > threshold:
        return device_name, best_match
    else:
        return device_name, "unknown"
    
 

def main():
    test_cases = [
        ("Hello World", "hello_world", 0.8),
        ("Hello", "H3llo", 0.6),
        ("Python", "Java", 0.5),
        ("GitHub", "GitLab", 0.7)
    ]

    for str1, str2, threshold in test_cases:
        result = is_close_match(str1, str2, threshold)
        print(f"Comparing '{str1}' with '{str2}' at threshold {threshold}: {result}")

    

if __name__ == "__main__":
    main()