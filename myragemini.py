import requests
import json

# आपकी 100% वर्किंग API Key
API_KEY = "AIzaSyArbnraHvbgpbA83KVqGUwddkesvh-JpE0"

# यह URL मॉडल को बिना किसी वर्जन या गेटवे के सीधे कॉल करता है
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

def ask_myra(text):
    headers = {'Content-Type': 'application/json'}
    # सबसे बेसिक पेलोड जो गूगल का हर सर्वर समझता है
    payload = {
        "contents": [{"parts": [{"text": text}]}]
    }
    
    try:
        # सीधा इंटरनेट से रिक्वेस्ट
        response = requests.post(URL, headers=headers, json=payload)
        result = response.json()
        
        if 'candidates' in result:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # यहाँ गूगल का असली कच्चा-चिट्ठा खुलेगा
            return f"❌ असली तकनीकी एरर: {json.dumps(result)}"
            
    except Exception as e:
        return f"❌ कनेक्शन फेल: {str(e)}"

print("="*40)
print("Myra: [The Final Stand] Hunter, I'm ready.")
print("="*40)

while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'bye']:
        break
    
    answer = ask_myra(user_input)
    print(f"\nMyra: {answer}\n")
