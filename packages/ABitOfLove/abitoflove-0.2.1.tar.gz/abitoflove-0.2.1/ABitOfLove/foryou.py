from turtle import *
import math
def main():
    print("Here is some love, just for you! ❤️")
    

    # Define heart equations
    def hearta(k):
        return 15 * math.sin(k) ** 3

    def heartb(k):
        return 12 * math.cos(k) - 5 * math.cos(2*k) - 2 * math.cos(3*k) - math.cos(4*k)

    # Setup turtle
    speed(0)          # fastest
    bgcolor("black")  # background
    hideturtle()

    # Draw heart
    for i in range(6000):
        x = hearta(i) * 20
        y = heartb(i) * 20
        goto(x, y)
        for j in range(5):
            color("#ff7587")   # pink color
        goto(0, 0)

    done()
    


if __name__ == "__main__":
    main()