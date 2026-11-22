# завдання 2.2. семафори (Semaphore) та Event для обмеження конкурентного доступу

import random
import threading
import time


class ConnectionPool:
    #пул з'єднань з обмеженням одночасного доступу через Semaphore
    def __init__(self, max_connections: int = 3):
        self._semaphore = threading.Semaphore(max_connections)
        self._lock = threading.Lock()
        self.max_connections = max_connections
        self.active_connections = 0
        self.total_served = 0
        self.peak_connections = 0

    def acquire_connection(self, client_name: str) -> int:
        print(f"[{client_name}] запит на з'єднання...")
        self._semaphore.acquire()
        with self._lock:
            self.active_connections += 1
            if self.active_connections > self.peak_connections:
                self.peak_connections = self.active_connections
            current_active = self.active_connections
        print(f"  [{client_name}] отримав з'єднання (активних: {current_active}/{self.max_connections})")
        return current_active

    def release_connection(self, client_name: str) -> None:
        with self._lock:
            self.active_connections -= 1
            self.total_served += 1
            current_active = self.active_connections
        print(f"  [{client_name}] звільнив з'єднання (активних: {current_active}/{self.max_connections})")
        self._semaphore.release()

    def get_stats(self) -> dict:
        with self._lock:
            return {
                "max": self.max_connections,
                "active": self.active_connections,
                "total_served": self.total_served,
                "peak": self.peak_connections,
            }


def client_task(pool: ConnectionPool, client_name: str, ready_event: threading.Event) -> None:
    #клієнт чекає сигналу готовності сервера, потім працює зі з'єднанням
    ready_event.wait()

    pool.acquire_connection(client_name)
    try:
        work_time = random.uniform(0.4, 1.2)
        print(f"    [{client_name}] працює {work_time:.1f} сек")
        time.sleep(work_time)
    finally:
        pool.release_connection(client_name)


def main():
    pool = ConnectionPool(max_connections=3)
    ready_event = threading.Event()
    num_clients = 10

    threads = []
    for i in range(1, num_clients + 1):
        t = threading.Thread(
            target=client_task,
            args=(pool, f"Client-{i:02d}", ready_event),
        )
        threads.append(t)
        t.start()

    time.sleep(0.3)
    print(">>> сервер готовий! усі клієнти починають роботу.\n")
    ready_event.set()

    for t in threads:
        t.join()

    stats = pool.get_stats()
    print("\n=== статистика пулу ===")
    print(f"макс. з'єднань:       {stats['max']}")
    print(f"активних зараз:       {stats['active']}")
    print(f"обслуговано клієнтів: {stats['total_served']}")
    print(f"пікове навантаження:  {stats['peak']}")
    print(f"ліміт не перевищено:  {stats['peak'] <= stats['max']}")


if __name__ == "__main__":
    main()