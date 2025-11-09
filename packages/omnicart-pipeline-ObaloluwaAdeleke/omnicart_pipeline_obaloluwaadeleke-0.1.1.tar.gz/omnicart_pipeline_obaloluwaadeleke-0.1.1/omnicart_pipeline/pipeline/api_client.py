import requests
import time


class APIClient:
    def __init__(self, base_url="https://fakestoreapi.com", limit=5):
        self.base_url = base_url
        self.limit = limit

    def get_all_products(self):
        products = []
        skip = 0
        total_pages = 3

        while skip < total_pages * self.limit:
            url = f"{self.base_url}/products?limit={self.limit}&skip={skip}"
            print(f"Fetching page with skip={skip}...")
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()

                if not data:
                    break

                products.extend(data)
                skip += self.limit
                time.sleep(1)  # simulate delay like real pagination
            

            except requests.exceptions.ConnectionError:
                    print("Connection dropped. Retrying in 3 seconds...")
                    time.sleep(3)
                    continue  # try again

            except requests.exceptions.Timeout:
                    print("Request timed out. Retrying...")
                    time.sleep(2)
                    continue

            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                break

        return products

    def get_all_users(self):
        response = requests.get(f"{self.base_url}/users")
        response.raise_for_status()
        return(response.json())
