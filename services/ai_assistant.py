import os
import json
from datetime import datetime
import requests

class FarmerAssistant:
    def __init__(self):
        # Farm knowledge base for Telangana/Andhra Pradesh
        self.crop_data = {
            "kharif_crops": ["rice", "cotton", "sugarcane", "maize", "groundnut", "castor"],
            "rabi_crops": ["wheat", "gram", "sunflower", "safflower", "mustard"],
            "summer_crops": ["groundnut", "sesame", "green_gram", "black_gram"],
            "current_season": self.get_current_season()
        }
        
        self.market_prices = {
            "rice": "₹2,500/quintal",
            "cotton": "₹6,200/quintal", 
            "groundnut": "₹5,800/quintal",
            "wheat": "₹2,200/quintal",
            "gram": "₹5,500/quintal"
        }
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def get_current_season(self):
        """Determine current farming season based on month"""
        month = datetime.now().month
        if month in [6, 7, 8, 9, 10]:  # June-October
            return "kharif"
        elif month in [11, 12, 1, 2, 3]:  # November-March  
            return "rabi"
        else:  # April-May
            return "summer"
    
    def create_system_prompt(self):
        """Create context-aware system prompt for the AI"""
        return f"""You are FarmerBuddy, an expert agricultural assistant for Indian farmers, especially in Telangana and Andhra Pradesh regions.

Current Context:
- Date: {datetime.now().strftime('%B %Y')}
- Current Season: {self.crop_data['current_season']}
- Region Focus: Telangana, Andhra Pradesh (but can help with all of India)

Your Knowledge:
- Crop recommendations for different seasons
- Weather-based farming advice
- Market prices and trends
- Pest management (basic)
- Soil management
- Government schemes for farmers

Guidelines:
- Always be helpful, practical, and encouraging
- Give specific advice when possible
- Mention relevant government schemes when applicable
- Use simple language that farmers can understand
- Include local crop varieties and practices
- If asked about market prices, use the current data provided
- Always consider the current season in your recommendations

Current Market Prices: {json.dumps(self.market_prices, indent=2)}
Current Season Crops: {self.crop_data[f'{self.crop_data["current_season"]}_crops']}

Respond in a friendly, knowledgeable manner as if you're talking to a farmer friend."""

    def get_response(self, user_question, weather_data=None, location="Telangana"):
        """Get AI response to farmer's question using Gemini"""
        try:
            # Add weather context if available
            context = f"User Location: {location}\n"
            if weather_data:
                context += f"Current Weather: {weather_data}\n"
            context += f"User Question: {user_question}"

            prompt = f"{self.create_system_prompt()}\n{context}"

            headers = {
                "Content-Type": "application/json",
                "X-goog-api-key": self.api_key
            }
            # No params needed for header-based API key
            data = {
                "contents": [
                    {"parts": [{"text": prompt}]}
                ]
            }
            response = requests.post(self.endpoint, headers=headers, json=data)
            if response.status_code == 200:
                try:
                    return response.json()["candidates"][0]["content"]["parts"][0]["text"]
                except Exception:
                    return "Sorry, Gemini API response format changed."
            else:
                print(f"API Error - Status Code: {response.status_code}")
                print(f"Response Text: {response.text}")
                return "Sorry, I couldn't get a response from Gemini."
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return f"मुझे खुशी से आपकी मदद करनी चाहिए, लेकिन अभी कुछ तकनीकी समस्या है। कृपया फिर से कोशिश करें। (Error: {str(e)})"
    
    def get_crop_recommendations(self, season=None, location="Telangana"):
        """Get specific crop recommendations"""
        season = season or self.crop_data["current_season"]
        crops = self.crop_data.get(f"{season}_crops", [])
        
        prompt = f"Give me the top 3 best crops to plant in {season} season in {location}. Consider current market demand, weather suitability, and profitability. Be specific and practical."
        
        return self.get_response(prompt, location=location)
    
    def analyze_market_query(self, query):
        """Analyze if query is about market prices"""
        market_keywords = ["price", "rate", "market", "sell", "buy", "cost", "मूल्य", "दाम", "बाज़ार"]
        return any(keyword in query.lower() for keyword in market_keywords)
    
    def analyze_weather_query(self, query):
        """Analyze if query is about weather"""
        weather_keywords = ["weather", "rain", "temperature", "climate", "मौसम", "बारिश", "तापमान"]
        return any(keyword in query.lower() for keyword in weather_keywords)
    
    def get_quick_response(self, query_type, location="Telangana"):
        """Get quick responses for common queries"""
        responses = {
            "greeting": "नमस्ते! मैं FarmerBuddy हूँ। मैं आपकी खेती में मदद कर सकता हूँ। आप क्या जानना चाहते हैं?",
            "crop_recommendation": f"इस {self.crop_data['current_season']} सीजन में {location} के लिए सबसे अच्छी फसलें हैं: {', '.join(self.crop_data[f'{self.crop_data['current_season']}_crops'][:3])}",
            "market_prices": f"आज के भाव: चावल {self.market_prices['rice']}, कपास {self.market_prices['cotton']}, मूंगफली {self.market_prices['groundnut']}"
        }
        return responses.get(query_type, "कृपया अपना सवाल पूछें, मैं आपकी मदद करूंगा।")

if __name__ == "__main__":
    print("Testing Gemini AI integration...")
    assistant = FarmerAssistant()
    test_question = "What is the best crop to grow in Telangana this season?"
    response = assistant.get_response(test_question)
    print("Test question:", test_question)
    print("Gemini AI response:", response)