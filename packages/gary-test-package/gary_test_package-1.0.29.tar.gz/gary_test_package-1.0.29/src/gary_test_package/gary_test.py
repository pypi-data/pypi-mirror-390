import sys


def hello_world(message):
    print(message)
    return message


def main():
    hello_world("hello world!")


if __name__ == '__main__':
    sys.exit(main())
