import arcade
from pirates_of_the_pythonean import PirateGame

COMMANDS = []

def fd(distance):
    COMMANDS.append(("fd", distance))

def rt(angle):
    COMMANDS.append(("rt", angle))

def lt(angle):
    COMMANDS.append(("lt", angle))

def shoot():
    COMMANDS.append(("shoot",))

def collect():
    COMMANDS.append(("collect",))


# Schreibe hier deinen Code
#TODO
fd(500)
lt(90)
fd(500)


game = PirateGame("./assets/levels/level1.tmx", COMMANDS)
arcade.run()