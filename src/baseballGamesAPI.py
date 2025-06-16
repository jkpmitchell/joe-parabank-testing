import requests

# Initialize the URL and headers for the HTTP request
url = "https://tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com/getMLBGamesForDate?gameDate=20250328"
headers = {
    "x-rapidapi-host": "tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com",
    "x-rapidapi-key": "dc471cba25msh5c583a111447780p134253jsn2699499f350a"
}

# Send a GET request to the URL with the headers
response = requests.get(url, headers=headers)

# Get the response code from the HTTP response
status_code = response.status_code

# Get the JSON data from the response
get_baseball_data = response.json()

