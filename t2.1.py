# завдання 2.1. демонстрація race condition та захист через threading.Lock

import random
import threading
import time


class BankAccount:
    #банківський рахунок без синхронізації (схильний до race condition)
    def __init__(self, balance: float = 0.0):
        self.balance = balance
        self.transaction_count = 0

    def deposit(self, amount: float) -> None:
        current = self.balance
        time.sleep(random.uniform(0.0001, 0.001))
        self.balance = current + amount
        self.transaction_count += 1

    def withdraw(self, amount: float) -> bool:
        current = self.balance
        time.sleep(random.uniform(0.0001, 0.001))
        if current >= amount:
            self.balance = current - amount
            self.transaction_count += 1
            return True
        return False


class SafeBankAccount:
    #банківський рахунок із синхронізацією через Lock
    def __init__(self, balance: float = 0.0):
        self.balance = balance
        self.transaction_count = 0
        self._lock = threading.Lock()

    def deposit(self, amount: float) -> None:
        with self._lock:
            current = self.balance
            time.sleep(random.uniform(0.0001, 0.001))
            self.balance = current + amount
            self.transaction_count += 1

    def withdraw(self, amount: float) -> bool:
        with self._lock:
            current = self.balance
            time.sleep(random.uniform(0.0001, 0.001))
            if current >= amount:
                self.balance = current - amount
                self.transaction_count += 1
                return True
            return False


def run_transactions(account, deposit_threads: int, withdraw_threads: int, ops_per_thread: int, amount: float):
    #запускаємо 20 потоків (10 на поповнення, 10 на зняття)
    def do_deposits():
        for _ in range(ops_per_thread):
            account.deposit(amount)

    def do_withdrawals():
        for _ in range(ops_per_thread):
            account.withdraw(amount)

    threads = []
    for _ in range(deposit_threads):
        threads.append(threading.Thread(target=do_deposits))
    for _ in range(withdraw_threads):
        threads.append(threading.Thread(target=do_withdrawals))

    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    initial_balance = 10000.0
    deposit_threads = 10
    withdraw_threads = 10
    ops_per_thread = 10
    amount = 50.0

    total_ops = (deposit_threads + withdraw_threads) * ops_per_thread
    expected_balance = initial_balance + (deposit_threads - withdraw_threads) * ops_per_thread * amount

    # === тест 1: без синхронізації ===
    print("=== тест без синхронізації (BankAccount) ===")
    unsafe_account = BankAccount(initial_balance)
    run_transactions(unsafe_account, deposit_threads, withdraw_threads, ops_per_thread, amount)
    print(f"очікуваний баланс:   {expected_balance:.2f}")
    print(f"фактичний баланс:    {unsafe_account.balance:.2f}")
    print(f"збігається:          {unsafe_account.balance == expected_balance}")
    print(f"виконано транзакцій: {unsafe_account.transaction_count} (очікувалося {total_ops})")

    # === тест 2: із синхронізацією (Lock) ===
    print("\n=== тест із синхронізацією (SafeBankAccount + Lock) ===")
    safe_account = SafeBankAccount(initial_balance)
    run_transactions(safe_account, deposit_threads, withdraw_threads, ops_per_thread, amount)
    print(f"очікуваний баланс:   {expected_balance:.2f}")
    print(f"фактичний баланс:    {safe_account.balance:.2f}")
    print(f"збігається:          {safe_account.balance == expected_balance}")
    print(f"виконано транзакцій: {safe_account.transaction_count} (очікувалося {total_ops})")


if __name__ == "__main__":
    main()