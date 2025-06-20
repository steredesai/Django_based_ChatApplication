from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_rooms, name='chat_rooms'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('poll/<int:room_id>/', views.poll_messages, name='poll_messages'),
    path('create-room/', views.create_room, name='create_room'),
    path('send/<int:room_id>/', views.send_message, name='send_message'),  # Add this line
    path('register/', views.register, name='register'),
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
]
