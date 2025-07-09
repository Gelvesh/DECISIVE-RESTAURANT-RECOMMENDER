from flask import Flask, jsonify, request
import random
import requests
import api
app = Flask(__name__)

# Your Yelp API Key
YELP_API_KEY = api.fun_api()

# Yelp API endpoint
YELP_API_URL = 'https://api.yelp.com/v3/businesses/search'

# Headers for the Yelp API request
headers = {
    'Authorization': f'Bearer {YELP_API_KEY}',
}

@app.route('/random-restaurant', methods=['GET'])
def get_random_restaurant():
    # Get search parameters from query string
    latitude = request.args.get('latitude', None)  # Latitude of the location
    longitude = request.args.get('longitude', None)  # Longitude of the location
    term = request.args.get('term', 'restaurants')  # Default to searching for restaurants
    radius = request.args.get('radius', None)  # Radius in meters

    # Validate latitude and longitude
    if not latitude or not longitude:
        return jsonify({'error': 'Latitude and longitude are required'}), 400

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return jsonify({'error': 'Invalid latitude or longitude values'}), 400

    # Validate radius
    try:
        if radius:
            radius = int(radius)
            if radius > 40000:  # Limit to Yelp's max allowed radius
                return jsonify({'error': 'Radius cannot exceed 40000 meters (25 miles)'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid radius value. Please provide a numeric value in meters'}), 400

    limit = 10  # Set the limit to 10 restaurants

    # Parameters to send in the Yelp API request
    params = {
        'term': term,
        'latitude': latitude,
        'longitude': longitude,
        'limit': limit,
    }

    # Add radius to parameters if provided
    if radius:
        params['radius'] = radius

    # Send request to Yelp API
    response = requests.get(YELP_API_URL, headers=headers, params=params)

    if response.status_code == 200:
        # Inspect the response content to understand the structure
        businesses = response.json().get('businesses', [])

        if not businesses:
            return jsonify({'error': 'No restaurants found for the given search parameters'}), 404
        
             
        
        
        
        # Randomly select a restaurant from the list
        random_restaurant = random.choice(businesses)

        # Extract the relevant details from the selected restaurant
        restaurant_details = {
            'name': random_restaurant.get('name'),
            'rating': random_restaurant.get('rating'),
            'location': ' '.join(random_restaurant.get('location', {}).get('address1', [])) or 'Address not available',
            'phone': random_restaurant.get('phone', 'Phone not available'),
            'url': random_restaurant.get('url'),
            'categories': [category['title'] for category in random_restaurant.get('categories', [])],
            'image_url': random_restaurant.get('image_url', 'Image not available'),
        }

        return jsonify(restaurant_details), 200
    else:
        return jsonify({'error': 'Failed to fetch data from Yelp API'}), response.status_code


if __name__ == '__main__':
    app.run(debug=True)

'''
Valid Coordinates: http://127.0.0.1:5000/random-restaurant?latitude=33.9533&longitude=-117.3962
Missing Coordinates: http://127.0.0.1:5000/random-restaurant?latitude=&longitude=
Invalid coordinates: http://127.0.0.1:5000/random-restaurant?latitude=not_a_number&longitude=not_a_number
Radius: http://127.0.0.1:5000/random-restaurant?latitude=37.7749&longitude=-122.4194&radius=5000
Exceed Radius: http://127.0.0.1:5000/random-restaurant?latitude=37.7749&longitude=-122.4194&radius=50000

UCR within 2 miles: http://127.0.0.1:5000/random-restaurant?latitude=33.9746&longitude=-117.3281&radius=3218
'''

# @app.route('/random-restaurant', methods=['GET'])
# def get_random_restaurant():
#     # Hardcoded inputs for testing
#     latitude = 33.9533  # Latitude of Riverside, California
#     longitude = -117.3962  # Longitude of Riverside, California
#     term = 'Mexican'  # Example cuisine type
#     radius = 5000  # Example radius in meters (5 km)

#     limit = 10  # Set the limit to 10 restaurants

#     # Parameters to send in the Yelp API request
#     params = {
#         'term': term,
#         'latitude': latitude,
#         'longitude': longitude,
#         'limit': limit,
#         'radius': radius,
#     }

#     # Send request to Yelp API
#     response = requests.get(YELP_API_URL, headers=headers, params=params)

#     if response.status_code == 200:
#         # Inspect the response content to understand the structure
#         businesses = response.json().get('businesses', [])

#         if not businesses:
#             return jsonify({'error': 'No restaurants found for the given search parameters'}), 404
        
#         # Randomly select a restaurant from the list
#         random_restaurant = random.choice(businesses)

#         # Extract the relevant details from the selected restaurant
#         restaurant_details = {
#             'name': random_restaurant.get('name'),
#             'rating': random_restaurant.get('rating'),
#             'location': ' '.join(random_restaurant.get('location', {}).get('address1', [])) or 'Address not available',
#             'phone': random_restaurant.get('phone', 'Phone not available'),
#             'url': random_restaurant.get('url'),
#             'categories': [category['title'] for category in random_restaurant.get('categories', [])],
#             'image_url': random_restaurant.get('image_url', 'Image not available'),
#         }

#         return jsonify(restaurant_details), 200
#     else:
#         return jsonify({'error': 'Failed to fetch data from Yelp API'}), response.status_code

# if __name__ == '__main__':
#     app.run(debug=True)