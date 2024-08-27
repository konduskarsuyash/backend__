from django.urls import path
from .views import UserViewSet

urlpatterns = [
    # List users or create a new user (which might include OTP generation)
    path('user/', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list-create'),

    # Retrieve, update, or delete a user
    path('user/<int:pk>/', UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='user-detail'),

    # Verify OTP for a user
    path('user/<int:pk>/verify-otp/', UserViewSet.as_view({'patch': 'verify_otp'}), name='verify-otp'),

    # Regenerate OTP for a user
    path('user/<int:pk>/regenerate-otp/', UserViewSet.as_view({'patch': 'regenerate_otp'}), name='regenerate-otp'),
]
