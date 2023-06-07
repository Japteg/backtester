from django.urls import path
from .views import ShortStraddle

urlpatterns = [
    path('short-straddle/', ShortStraddle.as_view()),
]