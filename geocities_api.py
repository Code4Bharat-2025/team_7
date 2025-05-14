import requests

def get_city_trivia(city_name):
    url = f"https://wft-geo-db.p.rapidapi.com/v1/geo/cities?CountryIds={city_name}"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",  # Replace with your real key
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return {"error": f"Could not fetch data for {city_name}"}
