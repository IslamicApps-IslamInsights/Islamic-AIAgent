import requests
import json

BASE_URL = "http://localhost:5001"

def test_route(name, path, method="POST", data=None):
    print(f"Testing {name} ({path})...")
    try:
        if method == "POST":
            response = requests.post(f"{BASE_URL}{path}", json=data)
        else:
            response = requests.get(f"{BASE_URL}{path}")
        
        if response.status_code == 200:
            print(f"✅ {name} Success!")
            # print(json.dumps(response.json(), indent=2)[:200] + "...")
        else:
            print(f"❌ {name} Failed with status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"💥 {name} Exception: {e}")

if __name__ == "__main__":
    # Test cases
    test_route("Health", "/api/health", method="GET")
    test_route("Daily Content", "/api/daily-content", method="GET")
    test_route("Random Hadith", "/api/hadith/random")
    test_route("Adhkar", "/api/adhkar", data={"category": "morning"})
    test_route("Names of Allah", "/api/names-of-allah", data={"query": "1"})
    test_route("Hajj Guidance", "/api/hajj-umrah", data={"ritual": "ihram"})
    test_route("Halal Check", "/api/halal-check", data={"item": "E120"})
    test_route("Zakat (New)", "/api/zakat", data={"cash": 10000})
    test_route("Zakat (Old Alias)", "/api/zakat/calculate", data={"amount": 10000})
