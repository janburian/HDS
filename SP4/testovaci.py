from datetime import time

class Sample:
    def __init__(self, hodnota, timestamp):
        self.hodnota = hodnota
        self.timestamp = timestamp

samples = []
sample1 = Sample(2, 3)
samples.append(sample1)
