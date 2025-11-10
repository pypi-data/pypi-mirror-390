

class Interaction:
    def __init__(self, user, channel, message=None):
        self.user = user
        self.channel = channel
        self.message = message

    async def send(self, content: str):
        print(f"[Interaction] → {self.user}: {content}")
