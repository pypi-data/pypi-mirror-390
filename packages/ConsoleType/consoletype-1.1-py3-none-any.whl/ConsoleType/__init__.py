import os
import time
import requests

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

def login(homeurl, error, name):
    print(f"IDLogin {name}")
    data = {"username": "example", "password": "example"}
    data["username"] = input("Имя Пользователя: ")
    data["password"] = input("Пароль: ")
    session = requests.Session()
    resp = session.post(homeurl, data=data)
    if "dp" in resp.text:
        print("Вход выполнен IDLogin")
        IDLogin = resp.text[4:]
        return IDLogin
    else:
        print(error)