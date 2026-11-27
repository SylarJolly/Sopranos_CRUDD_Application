import requests

API_URL = "http://127.0.0.1:8000"
TIMEOUT = 5 


# Sends a GET request to the API and returns the JSON response.
def get_json(path, params=None):
    response = requests.get(f"{API_URL}{path}", params=params, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


# Retrieves all characters optionally filtering by name.
def get_characters(name=None):
    return get_json("/characters/", params={"name": name, "limit": 100})


# Retrieves a character by ID or returns None if it is not found.
def get_character(character_id):
    response = requests.get(f"{API_URL}/characters/{character_id}", timeout=TIMEOUT)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


# Adds a new character to the database through the API.
def add_character(character):
    response = requests.post(f"{API_URL}/characters/", json=character, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


# Updates an existing character using its ID.
def update_character(character_id, character):
    response = requests.put(
        f"{API_URL}/characters/{character_id}", json=character, timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()


# Deletes a character from the database using its ID.
def delete_character(character_id):
    response = requests.delete(f"{API_URL}/characters/{character_id}", timeout=TIMEOUT)
    response.raise_for_status()