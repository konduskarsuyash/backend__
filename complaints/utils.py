from django.conf import settings
from twilio.rest import Client
from gtts import gTTS
import os
from django.conf import settings

def send_voice_message(phone_number, message):
    # Convert text to speech
    tts = gTTS(message)
    
    # Save to a file in the media directory
    audio_file_path = settings.MEDIA_ROOT / 'temp_audio.mp3'
    tts.save(audio_file_path)
    
    # Make sure the file is accessible via the media URL
    audio_url = settings.MEDIA_URL + 'temp_audio.mp3'
    print(audio_url)
    
    # If testing locally, you may need to use ngrok or similar to expose the URL publicly
    # Example URL for local testing with ngrok: http://<ngrok-subdomain>.ngrok.io/media/temp_audio.mp3
    
    # Twilio client setup
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    # Make a call and play the audio
    call = client.calls.create(
        to=phone_number,
        from_=settings.TWILIO_PHONE_NUMBER,
        twiml=f'<Response><Play>https://c375-103-225-134-62.ngrok-free.app/media/temp_audio.mp3</Play></Response>'
    )
    
    # Optionally, clean up the temporary file
    os.remove(audio_file_path)
    
    return call.sid
