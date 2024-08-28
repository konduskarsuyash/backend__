from django.urls import path
from .views import ImageClassificationView

urlpatterns = [
    path('image/', ImageClassificationView.as_view(), name='classify-image'),
    # path('video/', VideoClassificationView.as_view(), name='video-classification'),

]
