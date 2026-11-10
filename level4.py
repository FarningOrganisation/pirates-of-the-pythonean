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


"""
fd(100)      - nach vorne gehen
rt(90)       - nach rechts drehen
lt(90)       - nach links drehen
collect()    - Schatz aufsammeln
shoot()      - schießen
"""

# Schreibe hier deinen Code




















game = PirateGame("./assets/levels/level4.tmx", COMMANDS, True)
arcade.run()