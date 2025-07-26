import requests
import os
from datetime import datetime

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, city="Hyderabad"):
        """Get current weather for a city"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'  # Celsius
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return self.format_weather_data(data)
            else:
                return self.get_fallback_weather()
                
        except Exception as e:
            print(f"Weather API Error: {e}")
            return self.get_fallback_weather()
    
    def get_forecast(self, city="Hyderabad", days=5):
        """Get weather forecast"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return self.format_forecast_data(data)
            else:
                return self.get_fallback_forecast()
                
        except Exception as e:
            print(f"Forecast API Error: {e}")
            return self.get_fallback_forecast()
    
    def format_weather_data(self, data):
        """Format weather data for display"""
        return {
            'temperature': round(data['main']['temp']),
            'feels_like': round(data['main']['feels_like']),
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'description': data['weather'][0]['description'].title(),
            'wind_speed': round(data['wind']['speed'] * 3.6),  # Convert m/s to km/h
            'visibility': data.get('visibility', 0) / 1000,  # Convert to km
            'city': data['name'],
            'country': data['sys']['country'],
            'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
            'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
            'icon': data['weather'][0]['icon']
        }
    
    def format_forecast_data(self, data):
        """Format forecast data"""
        daily_forecasts = []
        current_date = None
        daily_data = []
        
        for item in data['list']:
            date = datetime.fromtimestamp(item['dt']).date()
            
            if current_date != date:
                if daily_data:
                    daily_forecasts.append(self.aggregate_daily_data(daily_data, current_date))
                current_date = date
                daily_data = []
            
            daily_data.append(item)
        
        # Add the last day
        if daily_data:
            daily_forecasts.append(self.aggregate_daily_data(daily_data, current_date))
        
        return daily_forecasts[:5]  # Return 5 days
    
    def aggregate_daily_data(self, daily_data, date):
        """Aggregate hourly data into daily summary"""
        temps = [item['main']['temp'] for item in daily_data]
        humidity = [item['main']['humidity'] for item in daily_data]
        
        # Check for rain
        rain_chance = 0
        total_rain = 0
        for item in daily_data:
            if 'rain' in item:
                rain_chance += 1
                total_rain += item['rain'].get('3h', 0)
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'day': date.strftime('%A'),
            'max_temp': round(max(temps)),
            'min_temp': round(min(temps)),
            'avg_humidity': round(sum(humidity) / len(humidity)),
            'rain_chance': round((rain_chance / len(daily_data)) * 100),
            'total_rain': round(total_rain, 1),
            'description': daily_data[len(daily_data)//2]['weather'][0]['description'].title(),
            'icon': daily_data[len(daily_data)//2]['weather'][0]['icon']
        }
    
    def get_farming_advice(self, weather_data):
        """Get farming advice based on weather"""
        temp = weather_data['temperature']
        humidity = weather_data['humidity']
        description = weather_data['description'].lower()
        
        advice = []
        
        # Temperature advice
        if temp > 35:
            advice.append("🌡️ बहुत गर्मी है - फसलों की अतिरिक्त सिंचाई करें")
        elif temp < 15:
            advice.append("❄️ ठंड है - फसलों को ठंड से बचाने के उपाय करें")
        
        # Rain advice
        if 'rain' in description:
            advice.append("🌧️ बारिश होने वाली है - खेत की जल निकासी चेक करें")
        elif humidity < 40:
            advice.append("💧 हवा में नमी कम है - सिंचाई की योजना बनाएं")
        
        # Wind advice
        if weather_data['wind_speed'] > 25:
            advice.append("💨 तेज हवा है - फसल को सहारा दें")
        
        return advice if advice else ["🌱 मौसम खेती के लिए अनुकूल है"]
    
    def get_fallback_weather(self):
        """Fallback weather data when API fails"""
        return {
            'temperature': 30,
            'feels_like': 33,
            'humidity': 65,
            'pressure': 1013,
            'description': 'Clear Sky',
            'wind_speed': 12,
            'visibility': 10,
            'city': 'Hyderabad',
            'country': 'IN',
            'sunrise': '06:00',
            'sunset': '18:30',
            'icon': '01d'
        }
    
    def get_fallback_forecast(self):
        """Fallback forecast when API fails"""
        return [
            {
                'date': '2025-07-25',
                'day': 'Friday',
                'max_temp': 32,
                'min_temp': 24,
                'avg_humidity': 70,
                'rain_chance': 20,
                'total_rain': 0,
                'description': 'Partly Cloudy',
                'icon': '02d'
            }
        ]