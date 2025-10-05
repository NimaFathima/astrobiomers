import requests
import time

def test_backend():
    """Test backend connectivity and return the URL"""
    
    possible_urls = [
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    print("CHECKING BACKEND AVAILABILITY:")
    print("=" * 40)
    
    for url in possible_urls:
        try:
            response = requests.get(f"{url}/health", timeout=3)
            if response.status_code == 200:
                data = response.json()
                print(f"Backend ACTIVE at: {url}")
                print(f"Status: {data.get('status', 'unknown')}")
                print(f"Version: {data.get('version', 'unknown')}")
                return url
        except requests.exceptions.ConnectionError:
            print(f"{url} - Connection refused")
        except Exception as e:
            print(f"{url} - Error: {e}")
    
    print("BACKEND NOT RUNNING")
    return None

if __name__ == "__main__":
    backend_url = test_backend()
    
    if backend_url:
        print("\n" + "=" * 40)
        print(f"YOUR BACKEND_BASE_URL IS: {backend_url}")
        print("\nSet this environment variable:")
        print(f"BACKEND_BASE_URL={backend_url}")
    else:
        print("\nBACKEND NOT RUNNING")
        print("Expected URL: http://localhost:8000")
        print("\nTo start backend:")
        print("1. cd backend")
        print("2. python -m api.main")