import random
import sys
import termios
import tty
import os
import time
import select

def main():
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    os.system("clear")
    print("\033[32m")  # Green

    while True:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            if getch() == 'q':
                break
        
        print(random.choice(["0", "1"]), end="", flush=True)
        time.sleep(0.01)

    print("\033[0m")  # Reset color
    
if __name__ == "__main__":
    main()


