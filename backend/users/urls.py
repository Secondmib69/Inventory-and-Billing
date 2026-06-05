from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('list/', UserListAPIView.as_view(), name='user_list'),
    path('detail/<int:id>/', UserDetailAPIView.as_view(), name='user_detail'),
]