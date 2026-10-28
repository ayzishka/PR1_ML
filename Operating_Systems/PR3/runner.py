
#!/usr/bin/env python3

import os
import sys
import time


def main():
    if len(sys.argv) < 3:
        print("Использование: python3 runner.py N команда [аргументы...]")
        sys.exit(1)

    try:
        count = int(sys.argv[1])
        if count < 1:
            raise ValueError
    except ValueError:
        print("Ошибка: N должно быть положительным целым числом.")
        sys.exit(1)

    command = sys.argv[2:]
    children = []

    for _ in range(count):
        start = time.monotonic()
        pid = os.fork()

        if pid == 0:
            try:
                os.execvp(command[0], command)
            except OSError as error:
                print(f"Не удалось запустить команду: {error}", file=sys.stderr)
                os._exit(127)

        children.append((pid, start))

    for pid, start in children:
        _, status = os.waitpid(pid, 0)
        elapsed = time.monotonic() - start

        if os.WIFEXITED(status):
            code = os.WEXITSTATUS(status)
        elif os.WIFSIGNALED(status):
            code = 128 + os.WTERMSIG(status)
        else:
            code = -1

        print(f"PID={pid} | код возврата={code} | время={elapsed:.3f} с")


if __name__ == "__main__":
    main()
