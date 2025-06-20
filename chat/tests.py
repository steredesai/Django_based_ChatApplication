from django.test import TestCase
from chat.message_filters import SpamFilter, LanguageFilter


class MessageFilterTests(TestCase):
    def test_spam_filter(self):
        filter_chain = SpamFilter()
        message = {"user": "user1", "content": "Hello"}

        # First message passes
        filter_chain.filter_message(message)

        # Repeated message raises ValueError
        with self.assertRaises(ValueError, msg="Spam detected! Repeated message."):
            filter_chain.filter_message(message)

    def test_language_filter(self):
        filter_chain = LanguageFilter()
        message = {"user": "user1", "content": "This is an offensive message"}

        # Message with banned words raises ValueError
        with self.assertRaises(ValueError, msg="Offensive language detected!"):
            filter_chain.filter_message(message)

        # Clean message passes
        clean_message = {"user": "user1", "content": "This is a clean message"}
        filter_chain.filter_message(clean_message)

    def test_combined_filters(self):
        filter_chain = SpamFilter(LanguageFilter())
        message = {"user": "user1", "content": "Hello"}

        # First message passes
        filter_chain.filter_message(message)

        # Offensive message fails
        offensive_message = {"user": "user1", "content": "This contains offensive language"}
        with self.assertRaises(ValueError):
            filter_chain.filter_message(offensive_message)
