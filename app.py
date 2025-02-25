import os
import time
import requests
import cv2
import numpy as np
from twilio.rest import Client
from io import BytesIO
from PIL import Image

# Twilio Credentials (fetched from Railway Environment Variables)
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")
YOUR_PHONE_NUMBER = os.environ.get("YOUR_PHONE_NUMBER")

# Visa Slot API Access Key
ACCESS_KEY = "N8724G"

# CheckVisaSlots URL (modified to include API access)
CHECK_VISA_SLOTS_URL = f"https://checkvisaslots.com/api/snapshots?key={ACCESS_KEY}"

# Initialize Twilio Client
twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def fetch_latest_screenshot():
    """Fetch the latest screenshot for Mumbai VAC from CheckVisaSlots API."""
    headers = {"Authorization": f"Bearer {ACCESS_KEY}"}
    response = requests.get(CHECK_VISA_SLOTS_URL, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # Extract the latest Mumbai VAC screenshot URL
        mumbai_vac_images = [
            snap["image_url"] for snap in data.get("snapshots", []) 
            if "Mumbai VAC" in snap["location"]
        ]
        
        if mumbai_vac_images:
            return requests.get(mumbai_vac_images[-1]).content  # Get latest image
    return None

def compare_images(img1_bytes, img2_bytes):
    """Compare two images and return True if they are different."""
    image1 = Image.open(BytesIO(img1_bytes)).convert("L")
    image2 = Image.open(BytesIO(img2_bytes)).convert("L")
    
    img1 = np.array(image1)
    img2 = np.array(image2)
    
    # Ensure same size
    if img1.shape != img2.shape:
        return True  # Different sizes mean they are different
    
    # Compute difference
    diff = cv2.absdiff(img1, img2)
    return np.sum(diff) > 0  # Returns True if different

def send_sms_alert():
    """Send an SMS alert when a visa slot is available."""
    message = twilio_client.messages.create(
        body="🚨 Visa slot available for Mumbai VAC! Check now: https://www.ustraveldocs.com/",
        from_=TWILIO_PHONE_NUMBER,
        to=YOUR_PHONE_NUMBER
    )
    print("📩 SMS sent:", message.sid)

# Store the last fetched image
last_mumbai_vac_image = None

while True:
    print("🔍 Checking for new visa slots...")
    new_image = fetch_latest_screenshot()
    
    if new_image:
        if last_mumbai_vac_image and compare_images(last_mumbai_vac_image, new_image):
            print("✅ Slot detected! Sending SMS...")
            send_sms_alert()
        
        last_mumbai_vac_image = new_image  # Update the stored image
    
    time.sleep(60)  # Wait 1 minute before checking again
