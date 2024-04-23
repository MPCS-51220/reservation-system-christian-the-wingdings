import requests
import json

def get_root():
    response = requests.get("http://localhost:8000/")
    return response.json()

if __name__ == "__main__":
    print(get_root())
