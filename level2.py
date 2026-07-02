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
shoot()
lt(45)
fd(300)
lt(25)
shoot()
rt(25)
fd(100)
rt(45)
fd(100)
rt(10)
shoot()
lt(10)
fd(300)
lt(40)
fd(750)
collect()


game = PirateGame("./assets/levels/level1.tmx", COMMANDS)
arcade.run()