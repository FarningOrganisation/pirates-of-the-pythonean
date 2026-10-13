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


game = PirateGame("./assets/levels/level3.tmx", COMMANDS, True)
arcade.run()