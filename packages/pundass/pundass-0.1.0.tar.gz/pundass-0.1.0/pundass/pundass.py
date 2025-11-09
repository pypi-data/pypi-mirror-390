import requests
import urllib.parse

def pd(message, model="openai"):
    encoded = urllib.parse.quote(message)
    url = f"https://text.pollinations.ai/{encoded}?model={model}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        text = response.text.strip()
        print(text)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

