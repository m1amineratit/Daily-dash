import requests

API_KEY = "d4e44aad08f14106980d336cf91f26d1"
headers = {
    "accept": "application/json",
    "CB-VERSION": "2023-10-01",
    "Authorization": f"Bearer {API_KEY}"
}

url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"

response = requests.get(url, headers=headers)
data = response.json()

print("Bitcoin price (USD):", data["data"]["amount"])
