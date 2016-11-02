import requests
from random import randint
import time

while True:
    time.sleep(randint(1, 120))
    for i in range(1, randint(1, 99)):
        r = requests.get("http://192.168.1.20")
