from django.conf import settings
from twilio.rest import Client
from gtts import gTTS
import os
import firebase_admin
from firebase_admin import credentials, storage

# Initialize Firebase Admin SDK
cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred, {
    'storageBucket': f'{settings.FIREBASE_STORAGE_BUCKET}.appspot.com'
})

# Global variable to store the file URL
file_url = None

def send_voice_message(phone_number, message):
    global file_url
    
    # Convert text to speech
    tts = gTTS(message)
    
    # Save to a temporary file
    temp_audio_path = os.path.join(settings.MEDIA_ROOT, 'temp_audio.mp3')
    tts.save(temp_audio_path)
    
    # Upload the file to Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob('temp_audio.mp3')
    blob.upload_from_filename(temp_audio_path)
    blob.make_public()
    
    # Get the public URL
    file_url = blob.public_url
    print(f"Audio file URL: {file_url}")
    
    # Twilio client setup
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    # Make a call and play the audio
    call = client.calls.create(
        to=phone_number,
        from_=settings.TWILIO_PHONE_NUMBER,
        twiml=f'<Response><Play>{file_url}</Play></Response>'
    )
    
    # Optionally, clean up the temporary file
    os.remove(temp_audio_path)
    
    return call.sid
