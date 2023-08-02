class Vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

def get_vector():
    return Vector2(1, 2) 

x = 0
y = 0
x, y = x + get_vector()
print(x, y) # 1 2

x, y = x + get_vector() 
print(x, y) # 2 4