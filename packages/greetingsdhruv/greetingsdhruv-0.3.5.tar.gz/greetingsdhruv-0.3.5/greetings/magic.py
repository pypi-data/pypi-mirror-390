import time
import random

while True:
    print('\a', end='', flush=True)
    time.sleep(random.uniform(0.02, 0.15))  # between 20ms and 150ms
