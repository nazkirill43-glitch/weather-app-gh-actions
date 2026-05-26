"""
Aplikacja pogodowa - Flask
Autor: Kyryl Nazarov

Aplikacja pozwala na wybór kraju i miasta, wyświetlając aktualną pogodę
na podstawie Open-Meteo API
"""

from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import logging
import os
import sys

# ----- Konfiguracja -----

# Inicjalizacja Flask
app = Flask(__name__)

# Konfiguracja loggowania
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Port aplikacji
PORT = os.getenv("PORT", 5000)
AUTHOR = "Kyryl Nazarov"

# Predefiniowana lista miast
CITIES_DATA = {
    "Polska": {
        "Warszawa": {"lat": 52.2297, "lon": 21.0122},
        "Kraków": {"lat": 50.0647, "lon": 19.9450},
        "Wrocław": {"lat": 51.1079, "lon": 17.0385},
        "Poznań": {"lat": 52.4082, "lon": 16.9454},
        "Gdańsk": {"lat": 54.3520, "lon": 18.6466},
    },
    "Niemcy": {
        "Berlin": {"lat": 52.5200, "lon": 13.4050},
        "Monachium": {"lat": 48.1351, "lon": 11.5820},
        "Hamburg": {"lat": 53.5511, "lon": 9.9937},
        "Kolonia": {"lat": 50.9375, "lon": 6.9603},
    },
    "Francja": {
        "Paryż": {"lat": 48.8566, "lon": 2.3522},
        "Lyon": {"lat": 45.7640, "lon": 4.8357},
        "Marsylia": {"lat": 43.2965, "lon": 5.3698},
    },
    "Włochy": {
        "Rzym": {"lat": 41.9028, "lon": 12.4964},
        "Mediolan": {"lat": 45.4642, "lon": 9.1900},
        "Wenecja": {"lat": 45.4408, "lon": 12.3155},
    },
    "Anglia": {
        "Londyn": {"lat": 51.5074, "lon": -0.1278},
        "Manchester": {"lat": 53.4808, "lon": -2.2426},
        "Liverpool": {"lat": 53.4084, "lon": -2.9916},
    },
    "Portugalia": {
        "Lizbona": {"lat": 38.7223, "lon": -9.1393},
        "Porto": {"lat": 41.1579, "lon": -8.6291},
        "Faro": {"lat": 37.0141, "lon": -7.9365},
        "Braga": {"lat": 41.5454, "lon": -8.4265},
    },
    "Ukraina": {
        "Kijów": {"lat": 50.4501, "lon": 30.5234},
        "Charków": {"lat": 50.0028, "lon": 36.2304},
        "Lwów": {"lat": 49.8397, "lon": 24.0297},
        "Odessa": {"lat": 46.4856, "lon": 30.7326},
        "Dnipro": {"lat": 48.4647, "lon": 35.0467},
    },
}


def log_startup():
    print(f"Autor: {AUTHOR}", flush=True)
    print(f"Data startu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(f"Port TCP: {PORT}", flush=True)
    print(f"URL: http://localhost:{PORT}", flush=True)
    sys.stdout.flush()


# ----- Routes -----
# Strona główna
@app.route("/")
def index():
    return render_template("index.html", countries=list(CITIES_DATA.keys()))


# Zwracanie miast dla kraju
@app.route("/api/cities/<country>")
def get_cities(country):
    if country in CITIES_DATA:
        return jsonify(list(CITIES_DATA[country].keys()))
    return jsonify([]), 404


# Pobieranie pogody dla wybranego miasta
@app.route("/api/weather/<country>/<city>")
def get_weather(country, city):
    try:
        if country not in CITIES_DATA:
            return jsonify({"error": "Kraj nie znaleziony"}), 404

        if city not in CITIES_DATA[country]:
            return jsonify({"error": "Miasto nie znalezione"}), 404

        coords = CITIES_DATA[country][city]
        lat, lon = coords["lat"], coords["lon"]

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
            "timezone": "auto",
        }

        logger.info(f"Pobieranie pogody dla: {city}, {country} (lat={lat}, lon={lon})")

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        current = data.get("current", {})

        weather_codes = {
            0: "Czysty błękit",
            1: "Przede wszystkim pogodnie",
            2: "Częściowo pochmurno",
            3: "Pochmurno",
            45: "Mgła",
            48: "Mgła zapamiętana",
            51: "Drażniła mżawka",
            53: "Umiarkowana mżawka",
            55: "Gęsta mżawka",
            61: "Słaby deszcz",
            63: "Umiarkowany deszcz",
            65: "Intensywny deszcz",
            71: "Słaby śnieg",
            73: "Umiarkowany śnieg",
            75: "Intensywny śnieg",
            80: "Przelotne opady",
            81: "Umiarkowane przelotne opady",
            82: "Intensywne przelotne opady",
            85: "Lekkie przelotne opady śniegu",
            86: "Silne przelotne opady śniegu",
            95: "Burza",
            96: "Burza ze słabym gradem",
            99: "Burza z intensywnym gradem",
        }

        weather_code = current.get("weather_code", 0)
        weather_description = weather_codes.get(weather_code, "Brak danych")

        weather_data = {
            "city": city,
            "country": country,
            "latitude": lat,
            "longitude": lon,
            "temperature": current.get("temperature_2m", "N/A"),
            "humidity": current.get("relative_humidity_2m", "N/A"),
            "wind_speed": current.get("wind_speed_10m", "N/A"),
            "weather_code": weather_code,
            "weather_description": weather_description,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(
            f"Pogoda pobrana pomyślnie: {weather_description}, {current.get('temperature_2m')}°C"
        )
        return jsonify(weather_data)

    except requests.exceptions.RequestException as e:
        logger.error(f"Błąd połączenia z API pogody: {str(e)}")
        return jsonify({"error": f"Błąd pobierania danych pogody: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd: {str(e)}")
        return jsonify({"error": "Błąd serwera"}), 500


@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200


# ----- Uruchomienie -----
if __name__ == "__main__":
    log_startup()
    app.run(host="0.0.0.0", port=int(PORT), debug=False)
