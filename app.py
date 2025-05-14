from collections import defaultdict
from flask import Flask, request, jsonify
import spacy
from geotext import GeoText
import requests

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")
bot_id = '0211520332006026'
city_dict = {}
header={
        "Content-Type": "application/json",
        "Authorization": "Bearer 21bda582-e8d0-45bc-bb8b-a5c6c555d176"
    }
img_ids= ["e96qVcEwWZVvp1X6JYRI5", "d70gRneKCzdaaASP1NS1n", "Zt09htq8OcnHYq138nP8N", "76hrfYS2W66xHVqXXeNXm"]
counter = defaultdict(int)
score = defaultdict(int)

def send_score_user(recipient, score):
    url = f"https://v1-api.swiftchat.ai/api/bots/{bot_id}/messages"

    payload = {
        "to": recipient,
        "type": "scorecard",
        "scorecard": {
            "theme": "theme1",
            "background": "orange",
            "performance": "high",
            "share_message": "Hey! I just got an All India Rank of 10 in the Weekly Quiz.",
            "text1": "Weekly Quiz",
            "text2": "Wow!.",
            "text3": f"Score - {score}",
            "text4": "All India Rank",
            "score": "10",
            "animation": "confetti"
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 21bda582-e8d0-45bc-bb8b-a5c6c555d176"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.json())
    return response.status_code

def send_quiz_templates(recipient, id, op1, op2):
    url = f"https://v1-api.swiftchat.ai/api/bots/{bot_id}/messages"

    payload = {
        "to": recipient,
        "type": "button",
        "button": {
            "body": {
                "type": "image",
                "image": {
                    "id": id,
                    "body": "Guess the Location"
                }
            },
            "buttons": [
                {
                
                    "type": "solid",
                    "body": op1,
                    "reply": "1"
                },
                {
                
                    "type": "solid",
                    "body": op2,
                    "reply": "0"
                }
            ],
            "allow_custom_response": True
        },
        "rating_type": "thumb"
    }
    headers = header

    response = requests.post(url, json=payload, headers=headers)
    print(response.json())

@app.route('/extract-locations', methods=['POST'])
def extract_locations():
    data = request.get_json()
    message = data.get('message', '')

    # Use geotext (quick results for cities/countries)
    places = GeoText(message)
    cities = list(places.cities)
    countries = list(places.countries)

    # Optional: Enhance with spaCy's NER
    doc = nlp(message)
    spacy_locations = [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC")]

    return jsonify({
        "cities": cities,
        "countries": countries,
        "spacy_locations": spacy_locations
    })

def extract_location_from_text(message):
    places = GeoText(message)
    cities = list(places.cities)
    countries = list(places.countries)

    doc = nlp(message)
    spacy_locations = [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC")]

    return {
        "cities": cities,
        "countries": countries,
        "spacy_locations": spacy_locations
    }

def get_city_info(city_name, city):
    if city:
        url = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities"
        querystring = {"namePrefix": city_name}
        headers = {
            "X-RapidAPI-Key": "a0edd873demsh7508773e1eefcc8p1b2506jsnc403f394b40c",
            "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        print(response.json())
        return response.json()
    else:
        url = "https://wft-geo-db.p.rapidapi.com/v1/geo/countries"
        querystring = {"namePrefix": city_name}
        headers = {
            "X-RapidAPI-Key": "a0edd873demsh7508773e1eefcc8p1b2506jsnc403f394b40c",
            "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        print(response.json())
        return response.json()


def explore_nearby(city_name):
    city_data = get_city_info(city_name)
    city_names = [place["name"] for place in city_data["data"]]
    url = f"https://wft-geo-db.p.rapidapi.com/v1/geo/locations/{city_name}/nearbyPlaces?limit=5&offset=0&radius=100"
    querystring = {"namePrefix": city_name}
    headers = {
        "X-RapidAPI-Key": "a0edd873demsh7508773e1eefcc8p1b2506jsnc403f394b40c",
        "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    print(response.json())
    return response.json()


def send_cities_as_buttons(recipient, cities):
    url = f"https://v1-api.swiftchat.ai/api/bots/{bot_id}/messages"

    buttons = [
        {
            "type": "solid",
            "body": text,
            "reply": text
        } for text in cities
    ]

    payload = {
        "to": recipient,  # Replace with actual recipient number
        "type": "button",
        "button": {
            "body": {
                "type": "text",
                "text": {
                    "body": "Hello, click on the button to know about the city."
                }
            },
            "buttons": buttons,
            "allow_custom_response": False
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 21bda582-e8d0-45bc-bb8b-a5c6c555d176"
    }
    response = requests.post(url, json=payload, headers=headers)
    print(response.json())
    return response.status_code


def send_message_to_user(recipient, message_body):
    url = f"https://v1-api.swiftchat.ai/api/bots/{bot_id}/messages"

    payload = {
        "to": recipient,
        "type": "text",
        "text": {
            "body": str(message_body)
        },
        "rating_type": "thumb"
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 21bda582-e8d0-45bc-bb8b-a5c6c555d176"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.json())
    return response.status_code


def send_map_to_user(recipient, message_body, location_data):
    url = f"https://v1-api.swiftchat.ai/api/bots/{bot_id}/messages"
    name = message_body.get("name")
    address = message_body.get("name")
    longitude = message_body.get("longitude")
    latitude = message_body.get("latitude")

    payload = {
        "to": recipient,
        "type": "location",
        "location": {
            "longitude": longitude,
            "latitude": latitude,
            "name": name,
            "address": location_data
        },
        "rating_type": "thumb"
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 21bda582-e8d0-45bc-bb8b-a5c6c555d176"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.json())
    return response.status_code

def format_city_info(city_data):
    name = city_data.get("name", "Unknown")
    country = city_data.get("country", "Unknown")
    population = city_data.get("population", "Not available")
    latitude = city_data.get("latitude", "N/A")
    longitude = city_data.get("longitude", "N/A")

    return (
        f"📍 *{name}*, {country}\n"
        f"🌍 Coordinates: {latitude}, {longitude}\n"
        f"👥 Population: {population}"
    )


@app.route('/', methods=['POST'])
def index_post():
    print("request body ", request.json)
    recipient = request.json.get('from')
    global city_dict
    global score
    global counter
    if(request.json.get('type')=='persistent_menu_response'):
        send_quiz_templates(recipient, "e96qVcEwWZVvp1X6JYRI5", "London", "Paris")
        if counter[recipient]==1:
            send_quiz_templates(recipient, "d70gRneKCzdaaASP1NS1n", "Paris", "India")
        if counter[recipient] == 2:
            send_quiz_templates(recipient, "Zt09htq8OcnHYq138nP8N", "Rome", "Pakistan")
        if counter[recipient] == 3:
            send_quiz_templates(recipient, "76hrfYS2W66xHVqXXeNXm", "Taiwan", "China")
        return 'Hello, quiz!'

    if request.json.get('type') == 'text':
        location = extract_location_from_text(request.json.get('text').get('body'))
        if(len(location['cities'])==0 and len(location['countries'])==0):
            send_message_to_user(recipient, "Please enter a city or country")
        elif(len(location['cities'])>0 and len(location['countries'])==0):
            first_city = location['cities'][0]
            city_data = get_city_info(first_city, True)
            city_names = [place["name"] for place in city_data["data"]]
            city_dict = {place["name"]: place for place in city_data["data"]}
            send_cities_as_buttons(recipient, city_names)
        else:
            first_city = location['countries'][0]
            city_data = get_city_info(first_city, False)
            print("country response ", city_data)
            city_names = [place["name"] for place in city_data["data"]]
            city_dict = {place["name"]: place for place in city_data["data"]}
            send_cities_as_buttons(recipient, city_names)

    elif request.json.get('type') == 'button_response' and (request.json.get('button_response').get('body')=="0" or request.json.get('button_response').get('body')=="1"):
        recipient = request.json.get('from')
        counter[recipient] += 1
        if request.json.get('button_response').get('body')=="1":
            score[recipient] += 1 
        
        if counter[recipient]==1:
            score_float = (score[recipient]/4)*100
            send_score_user(recipient, score_float)
            score[recipient] = 0
            counter[recipient] = 0


    elif request.json.get('type') == 'button_response':
        recipient = request.json.get('from')
        selected_city = request.json.get('button_response', {}).get('body')
        if selected_city in city_dict:
            location_data = city_dict[selected_city]
            if 'longitude' in location_data:
                message_body = format_city_info(location_data)
                send_map_to_user(recipient, location_data, message_body)
                send_message_to_user(selected_city, message_body)
            else:
                message_body = format_city_info(location_data)
                send_message_to_user(recipient, message_body)
        else:
            send_message_to_user(recipient, f"Sorry, no data found for {selected_city}.")
    return 'Hello, index!'



if __name__ == '__main__':
    app.run(port=5002, debug=True)
