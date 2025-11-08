import os
import time

def prints(text, times, size, title):
    sizes = 0
    ot = "-"
    tt = "-" * size
    while not sizes == size:
        os.system("cls")
        print(f"{ot}{text}{tt}")
        time.sleep(times)
        tt = tt[:-1]
        ot = ot + "-"
        sizes += 1

    print(title)
    #print("Create in prints")

def outputs(text, times):
    print(f"gf")

def title(title):
    print(title)