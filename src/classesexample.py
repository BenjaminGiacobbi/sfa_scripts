class Particle(object):

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def kill(self):
        print("Killed")


class Animal(object):

    def __init__(self, name="None", sound="Blank"):
        self.name = name
        self.sound = sound

    def vocalize(self):
        print(self.sound)


part1 = Particle(1.0, 3.0, 5.0)
part1.kill()

part2 = Particle()
part2.kill()

print(part1.x, part1.y, part1.z)
print(part2.x, part2.y, part2.z)

new_animal = Animal("Dog", "Bark")
new_animal.vocalize()
