from flask import Flask, request, render_template
import requests
from datetime import datetime
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENWEATHERMAP_API_KEY")

app = Flask(__name__)

def get_current_weather(city_name):
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": city_name,
        "appid":api_key,
        "units":"metric",
        "lang":"tr"
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if response.status_code != 200:
        return f"Hata: Şehir bulunamadı ({city_name})"
    
    weather_description = data["weather"][0]["description"]
    temperature = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    pressure = data["main"]["pressure"]
    sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M:%S')
    sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M:%S')
    icon_code = data["weather"][0]["icon"]
    icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
    
    alerts= data.get("alerts",[])
    alert_messages =[]
    
    for alert in alerts:
        alert_messages.append(f"{alert['event']}:{alert['description']}")

    result = {
        "city":city_name,
        "weather":weather_description.capitalize(),
        "temperature":f"{temperature}°C",
        "feels_like":f"{feels_like}°C",
        "humidity":f"{humidity}%",
        "wind_speed":f"{wind_speed} m/s",
        "pressure":f"{pressure} hPa",
        "sunrise":sunrise,
        "sunset":sunset,
        "icon_url":icon_url,
        "alerts":alert_messages 
        }
    
    return result

def get_weather_forecast(city_name):
    
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    
    params = {
        "q": city_name,
        "appid":api_key,
        "units":"metric",
        "lang":"tr"
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if response.status_code != 200:
        return f"Hata: Tahmin alınamadı({city_name})"
    
    forecast_list = data["list"]
    forecast_result = [] 
    for forecast in forecast_list:
        dt = datetime.fromtimestamp(forecast["dt"]) 
        temperature = forecast["main"]["temp"]
        weather_description = forecast["weather"][0]["description"]
    
        forecast_result.append({
        "datetime": dt.strftime('%Y-%m-%d %H:%M:%S'),
        "weather":weather_description.capitalize(), 
        "temperature":f"{(temperature)}°C"
        })
    
    return forecast_result

@app.route("/weather/location",methods=["POST"])
def weather_by_location():
    
    latitude = request.json.get("latitude")
    longitude = request.json.get("longitude")
    
    if not latitude or not longitude:
        return {"error":"Konum bilgisi alınamadı"},400
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "lat":latitude,
        "lon":longitude,
        "appid":api_key,
        "units":"metric",
        "lang":"tr"
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if response.status_code != 200:
        return {"error":"Hava durumu bilgisi alınamadı!"},400
    
    sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M:%S')
    sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M:%S')
    
    weather = {
        "city": data["name"],
        "weather": data["weather"][0]["description"].capitalize(),
        "temperature": f"{data['main']['temp']}°C",
        "feels_like": f"{data['main']['feels_like']}°C",
        "humidity": f"{data['main']['humidity']}%",
        "wind_speed": f"{data['wind']['speed']} m/s",
        "pressure": f"{data['main']['pressure']} hPa",
        "sunrise": sunrise,
        "sunset": sunset,
        "icon_url": f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
    }
    return weather

@app.route("/location-weather")
def location_weather():
    return render_template("location_weather.html")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/weather", methods=["GET","POST"])
def weather():
    if request.method == "POST":
        cities_input = request.form.get("cities")
    
        if not cities_input:
            return "Hata: Şehir adı boş olamaz!"
    
        city_names = [city.strip() for city in cities_input.split(",")]
    
    elif request.method == "GET":
        cities_input = request.args.get("cities")
        
        if not cities_input:
            return "Hata: Şehir adı boş olamaz!"
        
        city_names = [city.strip() for city in cities_input.split(",")]
        
    weather_data_list = []
    
    for city in city_names:
        current_weather = get_current_weather(city)
        weather_forecast = get_weather_forecast(city)
    
        weather_data_list.append({
            "current_weather": current_weather,
            "weather_forecast": weather_forecast
        })
    
    return render_template(
        "weather.html",
        weather_data_list=weather_data_list
    )
    
if __name__ == "__main__":
    app.run(debug=True)
    