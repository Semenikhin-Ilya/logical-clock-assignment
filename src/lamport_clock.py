class LamportClock:
    def __init__(self):
        self.value = 0
    def increment(self):
        self.value += 1
        return self.value
    def update(self, received):
        self.value = max(self.value, received) + 1
        return self.value

