import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_port():
    with open(os.path.join(BASE_DIR, "../config.json"), 'r') as f:
        data = json.load(f)
    return data['http']['port']
