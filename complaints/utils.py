from django.conf import settings
from twilio.rest import Client
from gtts import gTTS
import os
import firebase_admin
from firebase_admin import credentials, storage
from moviepy.editor import VideoFileClip
import cv2
import base64
import google.generativeai as genai
import re

# Initialize Firebase Admin SDK
cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred, {
    'storageBucket': f'{settings.FIREBASE_STORAGE_BUCKET}.appspot.com'
})

# Global variable to store the file URL
file_url = None
def get_firebase_image_url(image_file):
    bucket = storage.bucket()
    
    # Reset the file pointer to the beginning
    image_file.seek(0)
    
    # Define a unique blob name if needed
    blob = bucket.blob(f'images/{image_file.name}')
    
    # Upload the file to Firebase Storage
    blob.upload_from_file(image_file)
    blob.make_public()  # Make the file publicly accessible

    # Return the public URL of the uploaded image
    return blob.public_url

def send_voice_message(phone_number, message, image_file=None):
    global file_url
    
    # Convert text to speech
    tts = gTTS(message)
    
    # Save to a temporary file
    temp_audio_path = os.path.join(settings.MEDIA_ROOT, 'temp_audio.mp3')
    tts.save(temp_audio_path)
    
    # Upload the audio file to Firebase Storage
    bucket = storage.bucket()
    audio_blob = bucket.blob('audio/temp_audio.mp3')
    audio_blob.upload_from_filename(temp_audio_path)
    audio_blob.make_public()
    
    # Get the public URL for the audio file
    file_url = audio_blob.public_url
    print(f"Audio file URL: {file_url}")
    
    # If an image file is provided, upload it and get the URL
    image_url = None
    if image_file:
        try:
            image_url = get_firebase_image_url(image_file)
            print(f"Image file URL: {image_url}")
        except Exception as e:
            print(f"Failed to upload image to Firebase: {e}")

    # Twilio client setup
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    try:
        if image_url:
            whatsapp_message = client.messages.create(
                body=message,
                from_='whatsapp:' + settings.TWILIO_WHATSAPP_NUMBER,
                to='whatsapp:' + phone_number,
                media_url=image_url
            )
        else:
            whatsapp_message = client.messages.create(
                body=message,
                from_='whatsapp:' + settings.TWILIO_WHATSAPP_NUMBER,
                to='whatsapp:' + phone_number
            )
        print(f"WhatsApp message sent. SID: {whatsapp_message.sid}")
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")


    # Make a call and play the audio
    call = client.calls.create(
        to=phone_number,
        from_=settings.TWILIO_PHONE_NUMBER,
        twiml=f'<Response><Play>{file_url}</Play></Response>'
    )
    
    # Optionally, clean up the temporary file
    os.remove(temp_audio_path)
    
    return call.sid, whatsapp_message.sid



# # Configure Google Generative AI
# genai.configure(api_key=settings.OPENAI_KEY)

# def process_video_file(video_file):
#     """
#     Processes a video file to extract frames and audio, then uses a generative AI model to classify the content.
    
#     Args:
#         video_file: The video file object.

#     Returns:
#         A tuple (description, category).
#     """
#     # Save the uploaded video to a temporary file
#     video_path = os.path.join(settings.MEDIA_ROOT, video_file.name)
#     with open(video_path, 'wb') as f:
#         for chunk in video_file.chunks():
#             f.write(chunk)
    
#     # Extract frames and audio
#     base64_frames, audio_path = extract_frames_and_audio(video_path)
    
#     # Generate a task using the AI model
#     task_description, category = classify_video(base64_frames, audio_path)

#     # Optionally, clean up temporary files
#     os.remove(video_path)
#     os.remove(audio_path)

#     return task_description, category

# def extract_frames_and_audio(video_path):
#     """
#     Extracts frames and audio from a video file.

#     Args:
#         video_path: Path to the video file.

#     Returns:
#         A tuple (base64_frames, audio_path) where:
#         - base64_frames: A list of base64-encoded images of the frames.
#         - audio_path: Path to the extracted audio file.
#     """
#     base64_frames = []
#     video = cv2.VideoCapture(video_path)
#     total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
#     fps = video.get(cv2.CAP_PROP_FPS)
#     frames_to_skip = int(fps * 1)  # 1 frame per second

#     curr_frame = 0
#     while curr_frame < total_frames:
#         video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
#         success, frame = video.read()
#         if not success:
#             break
#         _, buffer = cv2.imencode(".jpg", frame)
#         base64_frames.append(base64.b64encode(buffer).decode("utf-8"))
#         curr_frame += frames_to_skip
#     video.release()

#     # Extract audio using MoviePy
#     base_video_path, _ = os.path.splitext(video_path)
#     audio_path = f"{base_video_path}.mp3"
#     clip = VideoFileClip(video_path)
#     clip.audio.write_audiofile(audio_path, bitrate="32k")
#     clip.audio.close()
#     clip.close()

#     return base64_frames, audio_path

# def classify_video(base64_frames, audio_path):
#     """
#     Classifies the content of a video using frames and audio.

#     Args:
#         base64_frames: A list of base64-encoded images of the frames.
#         audio_path: Path to the extracted audio file.

#     Returns:
#         A tuple (description, category).
#     """
#     transcription = genai.audio.transcriptions.create(
#         model="whisper-1",
#         file=open(audio_path, "rb"),
#     )
    
#     response = genai.chat.completions.create(
#         model="gpt-4o",
#         messages=[
#             {"role": "system", "content": """You are a Railway Complain AI tasked with analyzing complaints..."""},
#             {"role": "user", "content": f"The audio transcription is: {transcription.text}"}
#         ],
#         temperature=0,
#     )
    
#     task = response.choices[0].message.content
#     category = extract_category_from_task(task)
    
#     return task, category

# def extract_category_from_task(task):
#     """
#     Extracts the category number from the AI-generated task description.

#     Args:
#         task: The AI-generated task description.

#     Returns:
#         The extracted category as an integer.
#     """
#     match = re.search(r'\d+', task[::-1])
#     return int(match.group()[::-1]) if match else None
