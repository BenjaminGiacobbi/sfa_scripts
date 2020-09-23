import random

while True:
    user_input = input("I'm thinking of 3 numbers from 1 to 10. "
                       "Enter your guess or enter 'q' to quit: ")

    while True:
        try:
            user_input = int(user_input)
            if user_input in range(1, 11):
                break

        except ValueError:
            if user_input.lower() == "q":
                break

        user_input = input("Guess must be between 1 and 10. " 
                           "Try again or enter 'q' to quit: ")

    # this break is done before calculation to reduce processing when
    # user wants to quit
    if user_input.lower() == "q":
        break

    int_list = []

    for integer in range(3):
        while True:
            temp_int = random.randint(1, 10)
            if temp_int not in int_list:
                int_list.append(temp_int)
                break

    if user_input in int_list:
        print("You got it!")
    else:
        print("Wrong!")

    # prints numbers regardless of answer, technically not the same as example
    print("The three secret numbers were ", end="")
    print(sorted(int_list), sep=", ")

    # empty line used for better readability on multiple attempts
    print("")

print("Thank you for playing!")