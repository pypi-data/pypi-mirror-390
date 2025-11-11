import random


def talk(N: int = 5):
    times = random.randint(1, N)
    for _ in range(times):
        print("meow")


def chase_laser():
    """Simulate a cat chasing a laser pointer."""
    moves = ["zooms left!", "zooms right!", "pounces!", "spins in circles!"]
    print("The cat", random.choice(moves))


def main():
    print("Hello from holymeow!")
    talk(3)  


if __name__ == '__main__':
    main()
