from api_client import APIClient

client = APIClient("https://fakestoreapi.com", limit=5)
products = client.get_all_products()
print(len(products))
print(products[:2])  # show the first two

users = client.get_all_users()
print(users)
