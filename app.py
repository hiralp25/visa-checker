import os
import time
import requests
import cv2
import numpy as np
from twilio.rest import Client
from io import BytesIO
from PIL import Image

# Fetch credentials from Railway environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
USER_PHONE_NUMBER = os.getenv("USER_PHONE_NUMBER") 

# Visa Slot API Details
API_URL = "https://checkvisaslots.com/pro.html#api_key_info"
API_KEY = os.getenv("VISA_API_KEY")

# Store last seen screenshots (to compare changes)
last_screenshot = None

# Initialize Twilio Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def fetch_latest_screenshot():
    """Fetch the latest visa slot screenshot from the API."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(API_URL, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return None

        try:
            image_data = response.content  # Get raw image bytes
            return Image.open(BytesIO(image_data))  # Convert to PIL image
        
        except Exception as e:
            print(f"❌ Error: Invalid image data - {e}")
            return None
    
    except requests.RequestException as e:
        print(f"❌ Network Error: {e}")
        return None

def images_are_different(img1, img2):
    """Compare two images and return True if they are different."""
    img1_array = np.array(img1.convert("L"))  # Convert to grayscale
    img2_array = np.array(img2.convert("L"))

    difference = cv2.absdiff(img1_array, img2_array)
    return np.mean(difference) > 5  # Threshold for detecting change

def send_sms_alert():
    """Send an SMS alert via Twilio."""
    message = client.messages.create(
        body="🚨 Visa Slot Available for Mumbai VAC! Book Now! 🚀",
        from_=TWILIO_PHONE_NUMBER,
        to=USER_PHONE_NUMBER
    )
    print(f"📩 SMS sent! Message SID: {message.sid}")

while True:
    print("🔍 Checking for new visa slots...")

    new_screenshot = fetch_latest_screenshot()

    if new_screenshot:
        print("✅ API responded successfully")

        global last_screenshot
        if last_screenshot and images_are_different(last_screenshot, new_screenshot):
            print("🎉 Visa slot detected! Sending SMS alert...")
            send_sms_alert()
        else:
            print("🔄 No new slots detected.")

        last_screenshot = new_screenshot  # Update last screenshot reference
    
    else:
        print("⚠️ API response invalid. Retrying in 1 minute...")

    time.sleep(60)  # Wait for 1 minute before retrying
