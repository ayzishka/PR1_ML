
#!/usr/bin/env python3

import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from urllib.request import Request, urlopen


DEFAULT_URLS = [
    "https://example.com",
    "https://www.iana.org",
    "https://www.python.org",
    "https://www.gnu.org",
    "https://www.kernel.org",
    "https://www.wikipedia.org",
    "https://www.github.com",
    "https://www.openstreetmap.org",
    "https://www.rfc-editor.org",
    "https://www.w3.org",
    "https://www.debian.org",
    "https://www.ubuntu.com",
    "https://www.djangoproject.com",
    "https://pypi.org",
    "https://docs.python.org",
    "https://www.mozilla.org",
    "https://www.linux.org",
    "https://www.apache.org",
    "https://www.microsoft.com",
    "https://www.apple.com",
]


def download(url):
    request = Request(
        url,
        headers={"User-Agent": "PR4-Thread-Benchmark/1.0"},
    )

    try:
        with urlopen(request, timeout=15) as response:
            body = response.read()
            return url, len(body), response.status, None
    except Exception as error:
        return url, 0, None, str(error)


def run_sequential(urls):
    return [download(url) for url in urls]


def run_threads(urls, workers=4):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(download, urls))


def run_processes(urls, workers=4):
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(download, urls))


def measure(function, repeats=3):
    durations = []
    last_results = None

    for _ in range(repeats):
        start = time.perf_counter()
        last_results = function()
        durations.append(time.perf_counter() - start)

    return statistics.median(durations), durations, last_results


def main():
    parser = argparse.ArgumentParser(
        description="Сравнение способов загрузки 20 URL."
    )
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()

    if args.workers < 1 or args.repeats < 1:
        parser.error("--workers и --repeats должны быть положительными")

    urls = DEFAULT_URLS

    methods = [
        ("Последовательно", lambda: run_sequential(urls)),
        ("ThreadPoolExecutor", lambda: run_threads(urls, args.workers)),
        ("ProcessPoolExecutor", lambda: run_processes(urls, args.workers)),
    ]

    print(f"URL: {len(urls)} | workers: {args.workers} | повторы: {args.repeats}")
    print()
    print(f"{'Метод':<24} {'Медиана, с':>12} {'Успешно':>10} {'Ошибки':>8}")
    print("-" * 60)

    for name, function in methods:
        median, durations, results = measure(function, args.repeats)
        successes = sum(status is not None for _, _, status, _ in results)
        errors = len(results) - successes

        print(f"{name:<24} {median:>12.3f} {successes:>10} {errors:>8}")
        print("  Повторы:", ", ".join(f"{value:.3f}" for value in durations))

        for url, size, status, error in results:
            if error:
                print(f"  Ошибка: {url}: {error}")


if __name__ == "__main__":
    main()
