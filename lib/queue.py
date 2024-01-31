class Queue():
    def __init__(self) -> None:
        self.elements = []
        
    def put(self, element):
        self.elements.append(element)

    def get(self):
        element = self.elements[0]
        self.elements = self.elements[1:]
        return element

    def empty(self):
        return True if len(self.elements) == 0 else False