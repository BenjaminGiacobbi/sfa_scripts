import random


def generate_secret_nums(length, max=10):
    result = []
    while len(result) < length:
        number = random.randint(1, max)
        if number not in result:
            result.append(number)
    return result


print(generate_secret_nums(3))
print(generate_secret_nums(4, 15))