
#!/usr/bin/env python3

import argparse
import random
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Генерация целых чисел для практической работы PR4."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10_000_000,
        help="Количество чисел (по умолчанию: 10 миллионов).",
    )
    parser.add_argument(
        "--output",
        default="numbers.txt",
        help="Путь к выходному файлу.",
    )
    args = parser.parse_args()

    if args.count <= 0:
        parser.error("--count должен быть положительным числом")

    output = Path(args.output)
    random_generator = random.Random(42)

    with output.open("w", encoding="utf-8") as file:
        for _ in range(args.count):
            file.write(f"{random_generator.randint(1, 100)}\n")

    print(f"Создан файл: {output.resolve()}")
    print(f"Количество чисел: {args.count}")


if __name__ == "__main__":
    main()
