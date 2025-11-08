from PIL import Image
import random
import time
import os
import os
import shutil

def main():
    # Change this to your image file name
    image_path = "hacked.png"  

    img = Image.open(image_path)
    img.show()   # Opens image in the default image viewer app
    
    import random


    columns, _ = shutil.get_terminal_size()
    chars = "01"

    # set green
    print("\033[32m", end="")

    # endless loop
    while True:
        line = "".join(random.choice(chars) for _ in range(columns))
        print(line)
        time.sleep(0.03)



if __name__ == "__main__":
    main()
