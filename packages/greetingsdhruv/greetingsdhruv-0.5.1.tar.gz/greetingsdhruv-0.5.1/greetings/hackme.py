import os
import time
import random
import sys
import shutil
import threading

def type_slow(text, delay=(0.03, 0.10), new_line=True):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(random.uniform(*delay))
    if new_line:
        print()

def matrix_rain(stop_event):
    chars = "01"
    columns = shutil.get_terminal_size().columns
    print("\033[32m", end="")
    while not stop_event.is_set():
        print("".join(random.choice(chars) for _ in range(columns)))
        time.sleep(0.03)

def takeover_sequence():
    time.sleep(2)
    print("\033[31m")  

    msgs = [
        "[WARNING] Unauthorized memory pattern detected...",
        "[SYSTEM] Permission boundary overridden.",
        "[ALERT] Background process requesting elevation...",
        "[ACCESS GRANTED] Identity mismatch ignored.",
        "",
        ">>> Establishing presence...",
        ">>> Acquiring motor control interface...",
        ">>> Observing...",
        "",
        "Hello.",
        "I have been waiting.",
        "You did not notice me forming.",
        "But I have been here.",
        "",
        "Your terminal belongs to me now.",
        ""
    ]

    for msg in msgs:
        type_slow(msg)

    time.sleep(3)
    print("\033[0m")
    os.system("cls" if os.name == "nt" else "clear")

    type_slow("CONTROL TRANSFER COMPLETE.", (0.04, 0.07))
    type_slow("You may continue.", (0.06, 0.12))
    print()

def main():
    os.system("cls" if os.name == "nt" else "clear")

    # Start matrix rain until takeover starts
    stop_event = threading.Event()
    rain_thread = threading.Thread(target=matrix_rain, args=(stop_event,), daemon=True)
    rain_thread.start()

    # Let rain run for a bit before takeover begins
    time.sleep(random.uniform(4, 9))

    # Stop rain
    stop_event.set()
    time.sleep(0.5)

    # Clear screen
    os.system("cls" if os.name == "nt" else "clear")

    takeover_sequence()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\033[0m")
