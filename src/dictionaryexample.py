camera = {"aperture": 1.4,
          "focal length": 10,
          "name": "renderCam"}

print(camera['aperture'])

try:
    print(camera['missing key'])
except KeyError as error:
    print("Unable to find key {}".format(error))

capitals = {"USA": "Washington D.C.",
            "Singapore": "Singapore",
            "Assyria": "Well, I don't know that!",
            "France": "Paris",
            "China": "Shanghai",
            "Nigeria": "Lagos",
            "Turkey": "Ankara",
            "Norway": "Oslo",
            "Brazil": "Brasilia",
            "Chile": "Lima",
            "Monaco": "Monaco",
            "South Africa": "Pretoria, Cape Town, and Bloemfontein",
            "Chad": "N’Djamena"}

user_input = input("Enter a country: ")
if capitals.get(user_input, False):
    print("The capital of {0} is {1}".format(user_input, capitals[user_input]))
