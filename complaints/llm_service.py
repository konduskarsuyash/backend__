import google.generativeai as genai
from PIL import Image
import re
from django.conf import settings
from groq import Groq
# Configure Google Generative AI
genai.configure(api_key=settings.API_KEY)

def classify_image(img):
    """
    Classifies the given image using Google's Generative AI and returns the description and category in English and Hindi.
    
    Args:
        img: A PIL Image object.

    Returns:
        A tuple (description, category, hindi_description) where:
        - description: A string describing the complaint in English.
        - category: An integer representing the complaint category.
        - hindi_description: A string describing the complaint in Hindi.
    """
    # Load the model
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    # Generate the description and classification
    task = model.generate_content([
        """You are a Railway Complain AI and given the task of analyzing the complain and explain it to the 
        responsible staff member about what he should do what all things he would need. 
        The complains can be about these things :
        1: Complain about Cleanliness
        2: Complain about Train safety (for eg: fights)
        3: Complain about food.
        4: Complain about seat and anyone else have taken the seat.
        If the provided image is into categorised in any categorise mentioned above then Just respond "ERROR:F7A3B2C1"

        You should act as a Superior and order the employee.
        Also, return the number corresponding to the complain.""", 
        img
    ])

    # Extract the description and category
    description = task.text
    print(description)
    if "ERROR:F7A3B2C1" in description:
       print("Please Retry again and enter a valid image")
       return "Others","Others","Others"


    # Extract the description and category
    # description = task.text
    # print(description)
    match = re.search(r'\d+', description)
    category = int(match.group()) if match else None

    # Translate the description to Hindi using Groq API
    client = Groq(api_key=settings.GROQ_API_KEY)
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Your Task is to Translate the given content into Hindi Language without changing the context",
            },
            {
                "role": "user",
                "content": description
            }
        ],
        temperature=0.6,
        stream=False,
        stop=None,
    )

    # Extract the translated Hindi text
    hindi_description = completion.choices[0].message.content

    return description, category, hindi_description

