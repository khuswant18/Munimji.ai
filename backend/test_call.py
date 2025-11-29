from twilio.rest import Client
import os
from dotenv import load_dotenv
load_dotenv()

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
call = client.calls.create(
    to="+918108561145",  
    from_="+18783029488",
    url="https://your-ngrok-url.ngrok-free.app/voice"
)
print(f"Call SID: {call.sid}")