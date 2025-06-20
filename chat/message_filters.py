class MessageFilter:
    """
    Base filter in the Chain of Responsibility. Each filter checks a message
    and optionally passes it to the next filter.
    """
    def __init__(self, next_filter=None):
        self.next_filter = next_filter

    def filter_message(self, message):
        """
        Filter the message. If this filter passes, it forwards to the next filter.
        """
        if self.next_filter:
            return self.next_filter.filter_message(message)
        return True, None  # If no next filter, the message is valid


class SpamFilter(MessageFilter):
    spam_keywords = ['buy now', 'click here', 'free', 'spamword1']  # Add more spam keywords here

    def filter_message(self, message):
        for keyword in self.spam_keywords:
            if keyword in message.content.lower():
                return False, f"Message contains spam: {keyword}"
        # Pass to the next filter
        return super().filter_message(message)


class AbuseFilter(MessageFilter):
    abuse_keywords = ['abuse1', 'abuse2', 'abuse3']  # Add more offensive keywords here

    def filter_message(self, message):
        for keyword in self.abuse_keywords:
            if keyword in message.content.lower():
                return False, f"Message contains offensive content: {keyword}"
        # Pass to the next filter
        return super().filter_message(message)


class MessageFilterChain:
    """
    Chain together multiple filters.
    """
    def __init__(self):
        # Create the chain: SpamFilter -> AbuseFilter
        self.chain = SpamFilter(next_filter=AbuseFilter())

    def filter_message(self, message):
        # Start the chain
        return self.chain.filter_message(message)
