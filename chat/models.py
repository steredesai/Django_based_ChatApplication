from django.contrib.auth.models import User
from django.db import models


class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    bots = models.ManyToManyField('Bot', blank=True)  # Allow bots in chat rooms

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # For user messages
    bot = models.ForeignKey('Bot', on_delete=models.SET_NULL, null=True, blank=True)  # For bot messages
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = self.user.username if self.user else self.bot.name
        return f'{sender}: {self.content[:50]}'


class Bot(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def get_ai_response(self, message_content):
        from .openai_config import openai  # Import the OpenAI configuration
        try:
            # Generate a response using the ChatCompletion endpoint
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  
                messages=[
                    {"role": "system", "content": f"{self.name} is a helpful assistant."},
                    {"role": "user", "content": message_content},
                ],
                max_tokens=150,
                temperature=0.7,
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting AI response: {e}")
            return "Sorry, I couldn't process your request. Please try again later."

    def __str__(self):
        return self.name


