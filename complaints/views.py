from PIL import Image
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import RailwayComplaint, Employee, Department
from .serializers import RailwayComplaintSerializer
from .llm_service import classify_image
from django.shortcuts import get_object_or_404
from .utils import send_voice_message

class ImageClassificationView(APIView):
    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image')

        if not image_file:
            return Response({"error": "No image provided."}, status=status.HTTP_400_BAD_REQUEST)

        img = Image.open(image_file)
        description, category, hindi_messages = classify_image(img)

        
        if description == "Others" or category =="Others" or hindi_messages=="Others":
            # If the category is "Others", send a message indicating a wrong image upload
            return Response(
                {"error": "You have uploaded the wrong image."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Determine department and employee
        department_mapping = {
            1: "Cleanliness",
            2: "Train Safety",
            3: "Food",
            4: "Seat",
            5: "Others",
        }

        department_name = department_mapping.get(category)
        print(department_name)


        if department_name:
            department = get_object_or_404(Department, name=department_name)
            employee = Employee.objects.filter(department=department).first()

            # Save the complaint
            complaint = RailwayComplaint.objects.create(
                image=image_file,
                description=description,
                category=category,
                department=department,
                assigned_employee=employee
            )

            # Notify the assigned employee via voice call and WhatsApp
            if employee and employee.phone_number:
                print("Employee found, it is being assigned.")
                message = f"Complaint ID {complaint.id} requires your attention. Details: {description}"
                call_sid, whatsapp_sid = send_voice_message(employee.phone_number, hindi_messages, image_file)
                print(f"Voice message sent, Call SID: {call_sid}, WhatsApp SID: {whatsapp_sid}")

            serializer = RailwayComplaintSerializer(complaint)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({"error": "Invalid category."}, status=status.HTTP_400_BAD_REQUEST)




# class VideoClassificationView(APIView):
#     def post(self, request, *args, **kwargs):
#         video_file = request.FILES.get('video')

#         if not video_file:
#             return Response({"error": "No video provided."}, status=status.HTTP_400_BAD_REQUEST)

#         # Process the video file
#         description, category = process_video_file(video_file)

#         # Determine department and employee
#         department_mapping = {
#             1: "Cleanliness",
#             2: "Train Safety",
#             3: "Food",
#             4: "Seat"
#         }

#         department_name = department_mapping.get(category)
#         if department_name:
#             department = get_object_or_404(Department, name=department_name)
#             employee = Employee.objects.filter(department=department).first()

#             # Save the complaint
#             complaint = RailwayComplaint.objects.create(
#                 video=video_file,
#                 description=description,
#                 category=category,
#                 department=department,
#                 assigned_employee=employee
#             )

#             # Notify the assigned employee via voice call
#             if employee and employee.phone_number:
#                 message = f"Complaint ID {complaint.id} requires your attention. Details: {description}"
#                 call_sid = send_voice_message(employee.phone_number, message)
#                 print(f"Voice message sent, Call SID: {call_sid}")

#             serializer = RailwayComplaintSerializer(complaint)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         return Response({"error": "Invalid category."}, status=status.HTTP_400_BAD_REQUEST)