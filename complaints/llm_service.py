import google.generativeai as genai
from PIL import Image
import re
from django.conf import settings
# Configure Google Generative AI
genai.configure(api_key=settings.API_KEY)

def classify_image(img):
    """
    Classifies the given image using Google's Generative AI and returns the description and category.
    
    Args:
        img: A PIL Image object.

    Returns:
        A tuple (description, category) where:
        - description: A string describing the complaint.
        - category: An integer representing the complaint category.
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
        You should act as a Superior and order the employee.
        Also, return the number corresponding to the complain.""", 
        img
    ])

    # Extract the description and category
    description = task.text
    reversed_text = task.text[::-1]
    match = re.search(r'\d+', reversed_text)
    category = int(match.group()[::-1]) if match else None

    return description, category
