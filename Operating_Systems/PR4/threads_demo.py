
#!/usr/bin/env python3

import threading


shared_list = ["исходное значение"]


def worker():
    shared_list.append("изменено потоком")
    print("Внутри потока:", shared_list)


def main():
    print("До запуска потока:", shared_list)

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

    print("В родителе после завершения потока:", shared_list)


if __name__ == "__main__":
    main()
