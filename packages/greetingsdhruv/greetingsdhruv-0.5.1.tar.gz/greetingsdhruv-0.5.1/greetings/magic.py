import time
import random

print("The machine is set to explode in:")
for i in range(10, 0, -1):
    print(i,end=' ', flush=True)
    print('\a', end='', flush=True)
    time.sleep(0.5)
print("BOOM! 💥💥💥")

while True:
    print('\a', end='', flush=True)
    time.sleep(random.uniform(0.02, 0.15))  # between 20ms and 150ms
