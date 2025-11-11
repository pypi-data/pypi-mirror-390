from time import sleep, time

start = time()
while True:
    now = time()
    print(int(now - start))
    sleep(1)
