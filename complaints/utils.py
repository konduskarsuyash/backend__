from twilio.rest import Client
from django.conf import settings

def send_voice_message(to_phone, message):
    """
    Send a voice message using Twilio.
    """
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    call = client.calls.create(
        twiml=f'<Response><Say>{message}</Say></Response>',
        to=to_phone,
        from_=settings.TWILIO_PHONE_NUMBER
    )
    
    print(f"Call SID: {call.sid}")
    return call.sid
