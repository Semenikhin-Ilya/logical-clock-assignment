"""Сценарий симуляции: 3 процесса, обмен сообщениями,
   Lamport и Vector clocks, детекция конфликтов, визуализация."""
from src.event import Event  # noqa: F401  (для наглядности)
from src.lamport_clock import LamportClock
from src.vector_clock import VectorClock, happens_before, concurrent
from src.process import Process
from src.versioned_kv import VersionedKV
from src.visualizer import plot_time_space, plot_conflict


def run_scenario():
    n = 3
    event_log = []
    p1 = Process(0, n, event_log, LamportClock(), VectorClock(n))
    p2 = Process(1, n, event_log, LamportClock(), VectorClock(n))
    p3 = Process(2, n, event_log, LamportClock(), VectorClock(n))
    processes = [p1, p2, p3]

    # --- Симуляция обмена сообщениями ---
    p1.internal_event("start")
    p2.receive_message(0, *p1.send_message(1, "Hello P2"))
    p2.internal_event("processing")
    p3.receive_message(1, *p2.send_message(2, "Hello P3"))
    p3.internal_event("work")
    p1.internal_event("more work")
    p3.receive_message(0, *p1.send_message(2, "Hi P3"))
    p1.receive_message(1, *p2.send_message(0, "Back to P1"))
    p2.receive_message(2, *p3.send_message(1, "P3 to P2"))
    p1.internal_event("finish")

    return event_log, processes


def print_lamport_table(event_log):
    print("\n=== Таблица событий с Lamport timestamps ===")
    print(f"{'№':>3} | {'Процесс':^7} | {'Тип':^8} | {'Цель':^5} | "
          f"{'Сообщение':^14} | {'Lamport ts':^10}")
    print("-" * 70)
    for e in event_log:
        target = f"P{e.target + 1}" if e.target is not None else "-"
        msg = e.message if e.message is not None else "-"
        print(f"{e.eid + 1:>3} | {f'P{e.pid + 1}':^7} | {e.etype:^8} | "
              f"{target:^5} | {msg:^14} | {e.lamport_ts:^10}")


def print_vector_table(event_log):
    print("\n=== Таблица событий с Vector clocks ===")
    print(f"{'№':>3} | {'Процесс':^7} | {'Тип':^8} | Vector Clock [P1,P2,P3]")
    print("-" * 70)
    for e in event_log:
        print(f"{e.eid + 1:>3} | {f'P{e.pid + 1}':^7} | {e.etype:^8} | {e.vc}")


def analyse_causality(event_log):
    """Список причинно-следственных пар и статистика."""
    causal, conc = [], []
    for i in range(len(event_log)):
        for j in range(i + 1, len(event_log)):
            a, b = event_log[i], event_log[j]
            if happens_before(a.vc, b.vc):
                causal.append((a.eid + 1, b.eid + 1))
            elif concurrent(a.vc, b.vc):
                conc.append((a.eid + 1, b.eid + 1))

    total = len(event_log)
    print(f"\n=== Статистика причинно-следственных связей ===")
    print(f"Всего событий            : {total}")
    print(f"Всего пар событий        : {total * (total - 1) // 2}")
    print(f"Причинно-связанных пар   : {len(causal)}")
    print(f"Конкурентных пар         : {len(conc)}")
    print(f"\nПримеры причинных пар (первые 20): {causal[:20]}")
    print(f"Примеры конкурентных пар (первые 10): {conc[:10]}")


def run_conflict_demo():
    """Детекция конфликта при одновременном обновлении ключа x."""
    n = 3
    kv = VersionedKV(n)

    base_vc = VectorClock(n)                  # [0,0,0]
    kv.put('x', 0, base_vc, strategy='merge')

    vc_p1 = VectorClock(n); vc_p1.vector = [1, 0, 0]
    vc_p2 = VectorClock(n); vc_p2.vector = [0, 1, 0]

    print("\n=== Детекция конфликтов ===")
    print("Шаг 4: P1 отправляет x = 0 + 1 = 1, VC = [1,0,0]")
    print("   put ->", kv.put('x', 1, vc_p1, strategy='merge'))

    print("Шаг 5: P2 отправляет x = 0 * 2 = 0, VC = [0,1,0]")
    print("   put ->", kv.put('x', 0, vc_p2, strategy='merge'))

    print("\nСтратегия Merge (сумма): итоговое значение x =", kv.get('x'))

    # Сравнение со стратегией LWW на свежем хранилище
    kv2 = VersionedKV(n)
    kv2.put('x', 0, base_vc, strategy='lww')
    kv2.put('x', 1, vc_p1, strategy='lww')
    kv2.put('x', 0, vc_p2, strategy='lww')
    print("Стратегия LWW          : итоговое значение x =", kv2.get('x'))


def main():
    event_log, processes = run_scenario()
    print_lamport_table(event_log)
    print_vector_table(event_log)
    analyse_causality(event_log)
    run_conflict_demo()

    plot_time_space(event_log, processes, filename='time_space.png')
    plot_conflict()
    print("\nВизуализация сохранена: time_space.png, conflict.png")


if __name__ == "__main__":
    main()