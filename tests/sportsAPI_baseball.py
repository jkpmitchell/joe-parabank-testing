import pytest
from src.sportsAPI import get_baseball_data, get_player_stats

# Verify the response code
if status_code == 200:
    print("Request was successful")
else:
    print(f"Request failed with status code: {status_code}")

# Verify the response content
def test_get_baseball_data():
    data = get_baseball_data("20250328")
    assert isinstance(data, list), "Data should be a list"
    assert len(data) > 0, "Data should not be empty"