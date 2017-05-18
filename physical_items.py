
class physical_object():
    def __init__(self, position, color):
        self.position = position
        self.color = color
        self.type = 'cube'
        self.dimensions = (10, 10, 10)

    def __str__(self):
        return 'physical_object'
