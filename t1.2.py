# завдання 1.2. паралельне обчислення простих чисел із multiprocessing

import multiprocessing
import os
import time


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def sum_primes_in_range(start: int, end: int) -> tuple[int, int, int]:
    #обчислюємо суму, кількість простих чисел та pid робочого процесу
    pid = os.getpid()
    total_sum = 0
    count = 0
    for num in range(start, end):
        if is_prime(num):
            total_sum += num
            count += 1
    return total_sum, count, pid


def main():
    total_range = 1_000_000
    num_workers = 4

    #розбиваємо діапазон [2, total_range) на 4 частини
    chunk_size = total_range // num_workers
    ranges = []
    for i in range(num_workers):
        start = i * chunk_size if i > 0 else 2
        end = (i + 1) * chunk_size if i < num_workers - 1 else total_range
        ranges.append((start, end))

    # ==== 1. послідовне виконання ====
    print("=== послідовне виконання ===")
    start_time = time.perf_counter()
    seq_results = [sum_primes_in_range(s, e) for s, e in ranges]
    seq_time = time.perf_counter() - start_time

    seq_sum = sum(r[0] for r in seq_results)
    seq_count = sum(r[1] for r in seq_results)
    print(f"головний процес pid={os.getpid()}: знайдено {seq_count} простих, сума = {seq_sum}")

    # ==== 2 паралельне виконання з multiprocessing.Pool ===
    print(f"\n=== паралельне виконання ({num_workers} процеси) ===")
    start_time = time.perf_counter()
    with multiprocessing.Pool(processes=num_workers) as pool:
        par_results = pool.starmap(sum_primes_in_range, ranges)
    par_time = time.perf_counter() - start_time

    for (s, e), (part_sum, part_count, pid) in zip(ranges, par_results):
        print(f"  процес pid={pid}: діапазон [{s}, {e}) -> простих: {part_count}, сума: {part_sum}")

    par_sum = sum(r[0] for r in par_results)
    par_count = sum(r[1] for r in par_results)

    print(f"\nперевірка збігу результатів: {seq_sum == par_sum and seq_count == par_count}")
    print(f"послідовно: {seq_time:.3f} сек")
    print(f"паралельно ({num_workers} процеси): {par_time:.3f} сек")
    print(f"прискорення: {seq_time / par_time:.2f}x")


if __name__ == "__main__":
    main()