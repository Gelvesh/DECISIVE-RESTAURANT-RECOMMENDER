import requests

def find_restaurants(api_key, location, radius=1500, keyword="restaurant"):
    """
    Find nearby restaurants using Google Places API.
    """
    url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={location}&radius={radius}&type=restaurant&keyword={keyword}&key={api_key}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'results' in data:
            return data['results']  # List of restaurants
        else:
            return []
    else:
        print(f"Error: {response.status_code}")
        return []

def get_reviews(api_key, place_id):
    """
    Get reviews for a specific restaurant using Google Places Details API.
    """
    url = (
        f"https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&fields=name,rating,reviews&key={api_key}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'result' in data:
            return data['result']  # Restaurant details with reviews
        else:
            return {}
    else:
        print(f"Error: {response.status_code}")
        return {}

def main():
    api_key = "AIzaSyDUvzKJ7ZuIGKYt1NRNoz-mbL_epUPEp0I"  # Replace with your actual API key
    location = "37.7749,-122.4194"  # Replace with your desired location (latitude,longitude)
    radius = 1500  # Search radius in meters
    
    # Step 1: Find restaurants
    print("Searching for restaurants...")
    restaurants = find_restaurants(api_key, location, radius)

    if not restaurants:
        print("No restaurants found.")
        return

    # Step 2: Get reviews for each restaurant
    for restaurant in restaurants[:5]:  # Limiting to 5 restaurants for demonstration
        print("\n---")
        name = restaurant.get("name")
        place_id = restaurant.get("place_id")
        print(f"Fetching reviews for: {name}")

        details = get_reviews(api_key, place_id)
        if "name" in details and "reviews" in details:
            print(f"Restaurant: {details['name']}")
            print(f"Rating: {details['rating']}")
            for review in details['reviews'][:3]:  # Limiting to 3 reviews
                print(f" - {review['author_name']}: {review['rating']} stars")
                print(f"   {review['text']}")
        else:
            print("No reviews found.")

if __name__ == "__main__":
    main()
