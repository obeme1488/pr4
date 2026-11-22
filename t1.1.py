# завдання 1.1. створення та керування потоками в python

import threading
import time


def download_simulation(file_name: str, size_mb: float) -> dict:
    #імітація завантаження файлу (i/o-bound задача)
    thread_name = threading.current_thread().name
    print(f"[{thread_name}] початок завантаження '{file_name}' ({size_mb} mb)...")
    time.sleep(size_mb * 0.4)
    print(f"[{thread_name}] завершено '{file_name}'")
    return {"file": file_name, "size": size_mb, "thread": thread_name}


class MonitorThread(threading.Thread):
    #демон-потік для періодичного моніторингу активних потоків
    def __init__(self, interval: float = 0.5):
        super().__init__(name="Monitor", daemon=True)
        self.interval = interval
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            print(f"[{self.name}] активних потоків: {threading.active_count()}")
            self._stop_event.wait(self.interval)

    def stop(self):
        self._stop_event.set()


def main():
    files = [
        ("data.csv", 2.5),
        ("report.pdf", 1.0),
        ("image.png", 0.5),
        ("archive.zip", 4.0),
        ("log.txt", 0.3),
    ]

    # =====1. паралельне виконання у потоках ===
    print("=== паралельне завантаження (threading) ===")
    monitor = MonitorThread(interval=0.5)
    monitor.start()

    threads = [
        threading.Thread(
            target=download_simulation,
            args=(file_name, size_mb),
            name=f"Downloader-{i}",
        )
        for i, (file_name, size_mb) in enumerate(files, start=1)
    ]

    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    parallel_time = time.perf_counter() - start

    monitor.stop()
    monitor.join(timeout=1.0)
    print(f"\nусі файли завантажено паралельно за {parallel_time:.2f} сек")

    #====== 2. послідовне виконання для порівняння ===
    print("\n=== послідовне завантаження ===")
    start = time.perf_counter()
    for file_name, size_mb in files:
        download_simulation(file_name, size_mb)
    seq_time = time.perf_counter() - start

    print(f"\nпослідовний час: {seq_time:.2f} сек")
    print(f"паралельний час: {parallel_time:.2f} сек")
    print(f"прискорення: {seq_time / parallel_time:.2f}x")


if __name__ == "__main__":
    main()