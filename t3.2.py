# завдання 3.2. паттерн Producer-Consumer (queue.Queue) та виявлення дедлоків

import queue
import random
import threading
import time


class Task:
    #завдання для обробки у черщі
    def __init__(self, task_id: int, data: str, priority: int = 0):
        self.task_id = task_id
        self.data = data
        self.priority = priority
        self.created_at = time.time()

    def __repr__(self) -> str:
        return f"Task(id={self.task_id}, data='{self.data}')"


def producer(task_queue: queue.Queue, num_tasks: int, producer_id: int) -> None:
    #виробник генерує завдання та кладе їх в обмежену чергу
    for i in range(1, num_tasks + 1):
        task = Task(
            task_id=producer_id * 100 + i,
            data=f"пакет {i} від виробника {producer_id}",
            priority=random.randint(1, 5),
        )
        task_queue.put(task)
        print(f"[Виробник-{producer_id}] додано {task} (у черзі: {task_queue.qsize()})")
        time.sleep(random.uniform(0.08, 0.2))


def consumer(
    task_queue: queue.Queue,
    consumer_id: int,
    results: list,
    results_lock: threading.Lock,
) -> None:
    #споживач забирає завдання з черги та зберігає час обробки
    while True:
        try:
            task = task_queue.get(timeout=2.0)
        except queue.Empty:
            print(f"  [Споживач-{consumer_id}] черга порожня, завершення")
            break

        if task is None:
            #передаємо sentinel-сигнал завершення іншим споживачам
            task_queue.task_done()
            task_queue.put(None)
            print(f"  [Споживач-{consumer_id}] отримано сигнал завершення")
            break

        work_time = random.uniform(0.15, 0.35)
        time.sleep(work_time)
        elapsed = time.time() - task.created_at

        with results_lock:
            results.append((task.task_id, consumer_id, elapsed))

        print(f"  [Споживач-{consumer_id}] обробив task_id={task.task_id} за {work_time:.2f} сек")
        task_queue.task_done()


def producer_consumer_demo():
    task_queue = queue.Queue(maxsize=5)
    results = []
    results_lock = threading.Lock()
    num_producers = 2
    num_consumers = 3
    tasks_per_producer = 5

    producers = [
        threading.Thread(target=producer, args=(task_queue, tasks_per_producer, i))
        for i in range(1, num_producers + 1)
    ]
    consumers = [
        threading.Thread(target=consumer, args=(task_queue, i, results, results_lock))
        for i in range(1, num_consumers + 1)
    ]

    for p in producers:
        p.start()
    for c in consumers:
        c.start()

    # чекаємо завершення всіх виробників, потім відправляємо сигнал завершення None
    for p in producers:
        p.join()
    task_queue.put(None)

    for c in consumers:
        c.join()

    avg_time = sum(r[2] for r in results) / len(results) if results else 0.0
    print(f"\nоброблено задач: {len(results)} (очікувалося {num_producers * tasks_per_producer})")
    print(f"середній час життя задачі (від створення до завершення): {avg_time:.2f} сек")


def deadlock_demo():
    lock_a = threading.Lock()
    lock_b = threading.Lock()
    deadlock_detected = threading.Event()

    def worker_1():
        # захоплює A -> B
        lock_a.acquire()
        print("[Worker-1] захопив Lock A")
        time.sleep(0.1)
        if not lock_b.acquire(timeout=1.5):
            print("[Worker-1] ДЕДЛОК: не вдалося захопити Lock B за таймаутом!")
            deadlock_detected.set()
            lock_a.release()
            return
        print("[Worker-1] захопив Lock B")
        lock_b.release()
        lock_a.release()

    def worker_2():
        # захоплює B -> A (зворотний порядок спричиняє дедлок)
        lock_b.acquire()
        print("[Worker-2] захопив Lock B")
        time.sleep(0.1)
        if not lock_a.acquire(timeout=1.5):
            print("[Worker-2] ДЕДЛОК: не вдалося захопити Lock A за таймаутом!")
            deadlock_detected.set()
            lock_b.release()
            return
        print("[Worker-2] захопив Lock A")
        lock_a.release()
        lock_b.release()

    def safe_worker(name: str):
        # безпечна версія: обидва потоки завжди беруть замки в однаковому порядку A -> B
        with lock_a:
            print(f"[{name}] захопив Lock A")
            time.sleep(0.1)
            with lock_b:
                print(f"[{name}] захопив Lock B і виконав роботу")

    print("=== спроба з потенційним дедлоком ===")
    t1 = threading.Thread(target=worker_1)
    t2 = threading.Thread(target=worker_2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    if deadlock_detected.is_set():
        print(">>> дедлок виявлено через timeout, зависання попереджено.\n")
    else:
        print(">>> дедлок не виник цього разу.\n")

    print("=== безпечна версія (однаковий порядок замків A -> B) ===")
    s1 = threading.Thread(target=safe_worker, args=("SafeWorker-1",))
    s2 = threading.Thread(target=safe_worker, args=("SafeWorker-2",))
    s1.start()
    s2.start()
    s1.join()
    s2.join()
    print(">>> обидва безпечні потоки завершилися без дедлоку.")


def main():
    print("=" * 55)
    print("=== 1. паттерн Producer-Consumer (queue.Queue) ===")
    print("=" * 55)
    producer_consumer_demo()

    print(f"\n{'=' * 55}")
    print("=== 2. демонстрація та усунення дедлоку ===")
    print("=" * 55)
    deadlock_demo()


if __name__ == "__main__":
    main()