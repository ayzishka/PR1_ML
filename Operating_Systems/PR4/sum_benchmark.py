
#!/usr/bin/env python3

import argparse
import multiprocessing as mp
import statistics
import threading
import time
from concurrent.futures import ProcessPoolExecutor


def sum_chunk(numbers):
    total = 0
    for number in numbers:
        total += number
    return total


def split_chunks(numbers, workers):
    chunk_size = (len(numbers) + workers - 1) // workers
    return [
        numbers[start:start + chunk_size]
        for start in range(0, len(numbers), chunk_size)
    ]


def sequential_sum(numbers):
    return sum_chunk(numbers)


def threaded_sum(numbers, workers=4):
    chunks = split_chunks(numbers, workers)
    results = [0] * len(chunks)

    def worker(index, chunk):
      results[index] = sum_chunk(chunk)

    threads = [
        threading.Thread(target=worker, args=(i, chunk))
        for i, chunk in enumerate(chunks)
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return sum(results)


def process_sum(numbers, workers=4):
    chunks = split_chunks(numbers, workers)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return sum(executor.map(sum_chunk, chunks))


def measure(function, repeats=3):
    times = []
    result = None

    for _ in range(repeats):
        start = time.perf_counter()
        result = function()
        times.append(time.perf_counter() - start)

    return result, statistics.median(times), times


def main():
    parser = argparse.ArgumentParser(
        description="Сравнение последовательной, многопоточной "
                    "и многопроцессной суммы."
    )
    parser.add_argument("--input", default="numbers.txt")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()

    if args.workers < 1 or args.repeats < 1:
        parser.error("--workers и --repeats должны быть положительными")

    # Чтение файла выполняется до замеров, чтобы не включать I/O.
    with open(args.input, encoding="utf-8") as file:
        numbers = [int(line) for line in file]

    print(f"Чисел: {len(numbers)}")
    print(f"Повторов: {args.repeats}")
    print(f"Потоков/процессов: {args.workers}")
    print()

    methods = [
        ("Последовательно", lambda: sequential_sum(numbers)),
        ("4 потока", lambda: threaded_sum(numbers, args.workers)),
        ("4 процесса", lambda: process_sum(numbers, args.workers)),
    ]

    expected = None

    print(f"{'Метод':<20} {'Медиана, с':>12} {'Результат':>16}")
    print("-" * 52)

    for name, function in methods:
        result, median, samples = measure(function, args.repeats)

        if expected is None:
            expected = result
        elif result != expected:
            raise RuntimeError(f"Суммы не совпали: метод {name}")

        print(f"{name:<20} {median:>12.3f} {result:>16}")
        print("  Повторы:", ", ".join(f"{value:.3f}" for value in samples))


if __name__ == "__main__":
    mp.freeze_support()
    main()
