import random


def talk(N: int = 5):
    times = random.randint(1, N)
    for _ in range(times):
        print("meow")


def main():
    print("Hello from holymeow!")
    talk(3)  


if __name__ == '__main__':
    main()
    