from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from time import sleep
import time
from django.views.decorators.csrf import csrf_exempt

from .forms import RegisterForm
from .models import ChatRoom, Message, Bot
from django.contrib import messages
from .message_filters import MessageFilterChain
import logging
logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after registration
            return redirect('chat:chat_rooms')  # Redirect to the chat rooms page
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def chat_rooms(request):
    rooms = ChatRoom.objects.all()
    return render(request, 'chat/chat_rooms.html', {'rooms': rooms})

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    messages = room.messages.order_by('timestamp')  # Ensure messages are sorted
    logger.debug(f"Messages for room {room_id}: {messages}")
    return render(request, 'chat/chat_room.html', {'room': room, 'messages': messages})

@login_required
def poll_messages(request, room_id):
    last_message_id = int(request.GET.get('last_message_id', 0))
    room = get_object_or_404(ChatRoom, id=room_id)

    timeout = 30  # Long polling timeout
    start = time.time()

    while time.time() - start < timeout:
        new_messages = room.messages.filter(id__gt=last_message_id).order_by('timestamp')
        if new_messages.exists():
            # Let bots respond to the latest user messages
            for bot in room.bots.all():
                for message in new_messages.filter(user__isnull=False):  # Only respond to user messages
                    bot_response = bot.get_ai_response(message.content)
                    if bot_response:
                        Message.objects.create(bot=bot, room=room, content=bot_response)

            messages = [{
                'id': message.id,
                'user': message.user.username if message.user else None,
                'bot': message.bot.name if message.bot else None,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
            } for message in new_messages]
            return JsonResponse({'messages': messages})

        sleep(1)  # Sleep for a short while before checking again

    return JsonResponse({'messages': []})


@login_required
def create_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        bot_ids = request.POST.getlist('bots')  # Fetch selected bots

        if name:
            room = ChatRoom.objects.create(name=name, created_by=request.user)
            if bot_ids:
                bots = Bot.objects.filter(id__in=bot_ids)
                room.bots.set(bots)  # Associate selected bots with the room
            messages.success(request, "Chat room created successfully!")
            return redirect('chat:chat_rooms')

    bots = Bot.objects.all()  # Fetch all available bots
    return render(request, 'chat/create_room.html', {'bots': bots})


@csrf_exempt
@login_required
def send_message(request, room_id):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        room = get_object_or_404(ChatRoom, id=room_id)

        if content:
            # Create a filter chain and apply it to the message
            filter_chain = MessageFilterChain()
            message = Message(user=request.user, room=room, content=content)
            is_valid, error_message = filter_chain.filter_message(message)

            if not is_valid:
                # Return the error message to the sender
                return JsonResponse({'success': False, 'error': error_message}, status=400)

            # Save the message if it's valid
            message.save()
            return JsonResponse({'success': True, 'message': 'Message sent successfully'})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


def handle_bot_message(room, content):
    if room.bots.exists():
        bot_message = content.replace("/bot", "").strip()
        for bot in room.bots.all():
            bot_response = bot.get_ai_response(bot_message)
            Message.objects.create(bot=bot, room=room, content=bot_response)
        return "Bot response sent."
    return "No bots available in this chat room."


@login_required
def delete_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, created_by=request.user)
    room.delete()
    messages.success(request, "Chat room deleted successfully!")
    return redirect('chat:chat_rooms')