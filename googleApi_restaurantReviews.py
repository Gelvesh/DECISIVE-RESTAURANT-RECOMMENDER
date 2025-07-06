import os
import requests
from flask import Flask, request, jsonify

# Initialize the Flask app
app = Flask(__name__)

# Your Google API key (replace with your actual API key)
GOOGLE_API_KEY = 'AIzaSyDUvzKJ7ZuIGKYt1NRNoz-mbL_epUPEp0I'

# Google Places API URL for nearby search
PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

@app.route('/search', methods=['GET'])
def search_restaurants():
    try:
        # Get the latitude, longitude, and radius from the query string
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')
        radius = request.args.get('radius', 1000)  # Default radius 1000 meters
        
        # Validate inputs
        if not latitude or not longitude:
            return jsonify({"error": "Latitude and Longitude are required."}), 400

        # Prepare the parameters for the Places API request
        params = {
            'location': f'{latitude},{longitude}',
            'radius': radius,
            'type': 'restaurant',
            'key': GOOGLE_API_KEY
        }

        # Log the Places API request parameters
        print("Places API Request Parameters:", params)

        # Make the request to the Google Places API
        response = requests.get(PLACES_API_URL, params=params)
        data = response.json()

        # Log the raw Places API response
        print("Places API Response:", data)

        # Check if the response contains results
        if 'results' not in data:
            return jsonify({"error": "No results found."}), 404

        # Extract restaurant details
        restaurants = []
        for place in data['results']:
            name = place.get('name')
            address = place.get('vicinity')
            place_id = place.get('place_id')

            # Get full details (including reviews, rating, etc.) for each restaurant
            restaurant_details = get_restaurant_details(place_id)

            restaurants.append(restaurant_details)

        return jsonify({'restaurants': restaurants})

    except Exception as e:
        print("Error in searching restaurants:", str(e))  # Debugging
        return jsonify({"error": str(e)}), 500

def get_restaurant_details(place_id):
    """ Fetch full details of a restaurant including reviews and other information """
    try:
        # Google Places API URL for getting details of a place (reviews and more)
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        details_params = {
            'place_id': place_id,
            'key': GOOGLE_API_KEY
        }

        # Log the Place Details API request parameters
        print("Place Details API Request Parameters:", details_params)

        # Make the request to fetch place details
        response = requests.get(details_url, params=details_params)
        details_data = response.json()

        # Log the raw Place Details API response
        print("Place Details API Response:", details_data)

        # Extract details if available
        if 'result' in details_data:
            result = details_data['result']
            reviews = result.get('reviews', [])
            review_count = result.get('user_ratings_total', 0)
            rating = result.get('rating', 'N/A')
            phone_number = result.get('formatted_phone_number', 'N/A')
            website = result.get('website', 'N/A')
            opening_hours = result.get('opening_hours', {}).get('weekday_text', 'N/A')

            # Organize restaurant details into a dictionary
            restaurant_details = {
                'name': result.get('name'),
                'address': result.get('vicinity'),
                'rating': rating,
                'review_count': review_count,
                'phone_number': phone_number,
                'website': website,
                'opening_hours': opening_hours,
                'reviews': reviews
            }

            return restaurant_details
        else:
            return {}

    except Exception as e:
        print("Error in fetching restaurant details:", str(e))  # Debugging
        return {}

if __name__ == '__main__':  
    app.run(debug=True)

#http://127.0.0.1:5000/search?latitude=33.9746&longitude=-117.3281&radius=3218