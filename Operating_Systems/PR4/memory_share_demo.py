
#!/usr/bin/env python3

import multiprocessing as mp


shared_list = ["исходное значение"]


def worker():
    shared_list.append("изменено процессом")
    print("В дочернем процессе:", shared_list, flush=True)


def main():
    print("До запуска процесса:", shared_list)

    process = mp.Process(target=worker)
    process.start()
    process.join()

    print("В родительском процессе после join():", shared_list)


if __name__ == "__main__":
    mp.freeze_support()
    main()
