# завдання 3.1. concurrent.futures: ThreadPoolExecutor, ProcessPoolExecutor та обробка виключень

from concurrent.futures import (
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    as_completed,
)
import hashlib
import time


def io_bound_task(url: str) -> dict:
    # імітація i/o-bound задачі (завантаження сторінки)
    time.sleep(0.5)
    return {"url": url, "status": 200, "size": len(url) * 42}


def cpu_bound_task(n: int) -> dict:
    # cpu-bound задача: обчислення хеш-суми діапазону
    hasher = hashlib.sha256()
    for i in range(n):
        hasher.update(str(i).encode())
    return {"n": n, "hash": hasher.hexdigest()[:16]}


def risky_task(value: int) -> float:
    #задача, що може згенерувати виключення
    if value == 0:
        raise ZeroDivisionError("ділення на нуль!")
    if value < 0:
        raise ValueError(f"від'ємне значення: {value}")
    return 1000.0 / value


def benchmark_io_bound():
    urls = [f"https://api.example.com/data/{i}" for i in range(20)]

    #послідовне виконання
    start = time.perf_counter()
    seq_results = [io_bound_task(u) for u in urls]
    seq_time = time.perf_counter() - start

    # паралельне виконання через ThreadPoolExecutor + submit()
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(io_bound_task, u) for u in urls]
        par_results = [f.result() for f in futures]
    par_time = time.perf_counter() - start

    print(f"оброблено url: {len(par_results)} (збіг: {len(seq_results) == len(par_results)})")
    print(f"послідовно:                {seq_time:.2f} сек")
    print(f"ThreadPoolExecutor (5):    {par_time:.2f} сек")
    print(f"прискорення:               {seq_time / par_time:.2f}x")


def benchmark_cpu_bound():
    tasks = [500_000] * 8

    # послідовне виконання
    start = time.perf_counter()
    seq_results = [cpu_bound_task(n) for n in tasks]
    seq_time = time.perf_counter() - start

    #паралельне виконання через ProcessPoolExecutor + map()
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as executor:
        par_results = list(executor.map(cpu_bound_task, tasks))
    par_time = time.perf_counter() - start

    print(f"виконано задач: {len(par_results)}, хеш: {par_results[0]['hash']}")
    print(f"послідовно:                {seq_time:.2f} сек")
    print(f"ProcessPoolExecutor (4):   {par_time:.2f} сек")
    print(f"прискорення:               {seq_time / par_time:.2f}x")


def handle_exceptions():
    values = [10, 5, 0, -3, 8, 2]

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_val = {executor.submit(risky_task, v): v for v in values}

        for future in as_completed(future_to_val):
            val = future_to_val[future]
            try:
                res = future.result()
                print(f"  [успіх]   value={val:>2} -> результат = {res:.2f}")
            except (ZeroDivisionError, ValueError) as e:
                print(f"  [помилка] value={val:>2} -> {type(e).__name__}: {e}")


def main():
    print("=" * 55)
    print("=== 1. I/O-bound: ThreadPoolExecutor ===")
    print("=" * 55)
    benchmark_io_bound()

    print(f"\n{'=' * 55}")
    print("=== 2. CPU-bound: ProcessPoolExecutor ===")
    print("=" * 55)
    benchmark_cpu_bound()

    print(f"\n{'=' * 55}")
    print("=== 3. обробка виключень у пулах (as_completed) ===")
    print("=" * 55)
    handle_exceptions()


if __name__ == "__main__":
    main()