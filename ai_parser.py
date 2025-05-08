import os
from google import genai
from google.genai import types
from dotenv import load_dotenv


load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=GEMINI_API_KEY)

def parse_signal(raw_signal: str) -> dict:
    """
    Parse the raw signal and return a dict
    """

    prompt = f"""
    Extract trading signal details from this message and return ONLY JSON:
    
    {raw_signal}
    
    Required JSON format:
    {{
        "action": "BUY/SELL",
        "order_type": "limit/market",
        "symbol": "XXX/USDT",
        "entry_price": float,
        "take_profit": float,
        "stop_loss": float,
        "confidence": 0-1
    }}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
            system_instruction="You are a trading assistant. Extract trading signals from messages.",),
            contents=prompt,
)
        # Extract JSON from Gemini's response
        json_str = response.text.strip().replace('```json', '').replace('```', '')
        print(f"AI response: {json_str}")
        return eval(json_str)  # Convert string to dict
        
    except Exception as e:
        print(f"AI parsing failed: {e}")
        return None




