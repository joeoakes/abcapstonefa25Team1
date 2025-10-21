import argparse
from testMethods import greet
# Define a simple function with an argument (PLACEHOLDER UNTIL CODE IS READY)

# Set up a command-line interface
def main():
    parser = argparse.ArgumentParser(description="A simple greeting tool")
    parser.add_argument("--name", "-n", required=True, help="Your name")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the function with the command-line value
    greet(args.name)

if __name__ == "__main__":
    main()