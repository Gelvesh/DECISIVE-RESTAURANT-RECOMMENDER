import os
import requests
import pickle  # For loading the trained model
from flask import Flask, request, jsonify
from nltk.sentiment import SentimentIntensityAnalyzer
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# Load the trained XGBoost model
# MODEL_PATH = 'model.pkl'  # Replace with your actual model file path
MODEL_PATH = 'sen_score_andreview_count.pkl'
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()  

# Google Places API key
GOOGLE_API_KEY = 'AIzaSyDUvzKJ7ZuIGKYt1NRNoz-mbL_epUPEp0I'  # Replace with your actual key

# Google Places API URLs
PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
DETAILS_API_URL = "https://maps.googleapis.com/maps/api/place/details/json"

@app.route('/search', methods=['GET'])
def search_restaurants():
    try:
        # Get latitude, longitude, and radius from request
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')
        radius = request.args.get('radius', 1000)

        if not latitude or not longitude:
            return jsonify({"error": "Latitude and Longitude are required."}), 400

        # Prepare the Places API request
        params = {
            'location': f'{latitude},{longitude}',
            'radius': radius,
            'type': 'restaurant',
            'key': GOOGLE_API_KEY
        }
        response = requests.get(PLACES_API_URL, params=params)
        places_data = response.json()

        if 'results' not in places_data:
            return jsonify({"error": "No restaurants found."}), 404

        restaurants = []
        for place in places_data['results']:
            place_id = place.get('place_id')
            details = get_restaurant_details(place_id)

            if details:
                # Extract sentiment score and review count
                reviews = details.get('reviews', [])
                sentiment_score = np.mean([
                    sia.polarity_scores(review['text'])['compound']
                    for review in reviews
                ]) if reviews else 0
                # review_count = details.get('review_count', 0)
                stars = details.get('stars')
                # Predict rating using the XGBoost model
                features = np.array([[stars, sentiment_score]])
                predicted_rating = model.predict(features)[0]

                details['predicted_rating'] = float(predicted_rating)
                restaurants.append(details)

        # Sort restaurants by predicted rating in descending order
        sorted_restaurants = sorted(restaurants, key=lambda x: x['predicted_rating'], reverse=True)[:5]

        # Return top 5 restaurants as JSON
        return jsonify({'top_5_restaurants': sorted_restaurants})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500


def get_restaurant_details(place_id):
    """Fetch detailed information about a restaurant from Google Places."""
    try:
        params = {
            'place_id': place_id,
            'key': GOOGLE_API_KEY
        }
        response = requests.get(DETAILS_API_URL, params=params)
        details_data = response.json()

        if 'result' in details_data:
            result = details_data['result']
            return {
                'name': result.get('name'),
                'address': result.get('vicinity'),
                'review_count': result.get('user_ratings_total', 0),
                'reviews': result.get('reviews', []),
                'rating': result.get('rating', 'N/A')
            }
        return {}
    except Exception as e:
        print("Error fetching restaurant details:", str(e))
        return {}

if __name__ == '__main__':
    app.run(debug=True)
