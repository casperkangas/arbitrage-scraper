import requests

def fetch_data(url: str) -> None:
    # Mimicking a standard browser on MacOS to reduce the chance of being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Connection successful. Ready to parse data.")
            # JSON parsing logic will be implemented here
        else:
            print("Failed to retrieve data.")
            
    except requests.RequestException as e:
        print(f"A network error occurred: {e}")

if __name__ == "__main__":
    # Using the Veikkaus homepage as an initial connectivity test
    test_url = "https://www.veikkaus.fi/" 
    fetch_data(test_url)