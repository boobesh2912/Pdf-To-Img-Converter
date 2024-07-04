import secrets
import os
def generate_api_key():
    api_key = secrets.token_urlsafe(32)
    with open('config.py', 'w') as f:
        f.write(f'API_KEY = "{api_key}"')
    print(f"New API key generated and saved to config.py: {api_key}")
    print("Keep this key secure and provide it to the company for API access.")
if __name__ == "__main__":
    generate_api_key()