
#!/usr/bin/env python3

import os
import time


def get_rss_kb():
    with open("/proc/self/status", encoding="utf-8") as file:
        for line in file:
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    return 0


def main():
    data = [0] * 2_000_000
    print(f"Родитель PID={os.getpid()}, размер списка={len(data)}", flush=True)

    pid = os.fork()

    if pid == 0:
        print(f"Ребёнок PID={os.getpid()}", flush=True)
        print(f"RSS до изменения: {get_rss_kb()} kB", flush=True)

        for i in range(0, len(data), 4096):
            data[i] = 1

        print(f"RSS после изменения: {get_rss_kb()} kB", flush=True)
        os._exit(0)

    os.waitpid(pid, 0)
    print("Родитель дождался завершения ребёнка.", flush=True)


if __name__ == "__main__":
    main()
