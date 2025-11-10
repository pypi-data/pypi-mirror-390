name = input("What's your name? ").capitalize()
print("Hello "+name)
food = input(name + ", what's your favorite food? ").lower()
l = len(name)
if food == "pizza" or food == "gnocchi":
    print("I like " + food + " too! ")
else :
    print(f"I don't like {food} ")
print("The last letter of your name is " + name[-1])
print(f"Your name is {l} letters long")