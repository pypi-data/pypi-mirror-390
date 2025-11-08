# magic.py
import random
import time
import os

def main():
    
    GREEN = "\033[32m"
    RESET = "\033[0m"
    print("Welcome to the Matrix! System compromised by hackers")

    os.system("cls" if os.name == "nt" else "clear")
    print(GREEN, end="")

    while True:
        print(random.choice(["0", "1"]), end="", flush=True)
        time.sleep(0.01)

    print(RESET)

if __name__ == "__main__":
    main()
