import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_time_space(event_log, processes, filename="time_space.png"):
    """Диаграмма времени (time-space diagram) для трёх процессов."""
    fig, ax = plt.subplots(figsize=(10, 8))

    # Точки событий
    for e in event_log:
        y = e.eid + 1
        x = e.pid
        color, marker = 'blue', 'o'
        if e.etype == 'SEND':
            color, marker = 'green', '^'
        elif e.etype == 'RECEIVE':
            color, marker = 'orange', 'v'
        ax.plot(x, y, marker=marker, color=color, markersize=9)
        ax.text(x + 0.05, y, f"E{e.eid + 1} (L={e.lamport_ts})", fontsize=8)

    # Стрелки сообщений: SEND -> соответствующий RECEIVE
    for e_send in event_log:
        if e_send.etype != 'SEND':
            continue
        for e_recv in event_log:
            if (e_recv.etype == 'RECEIVE'
                    and e_recv.pid == e_send.target
                    and e_recv.target == e_send.pid
                    and e_recv.message == e_send.message):
                ax.annotate(
                    '',
                    xy=(e_recv.pid, e_recv.eid + 1),
                    xytext=(e_send.pid, e_send.eid + 1),
                    arrowprops=dict(arrowstyle='->', color='gray', lw=1.5),
                )
                break

    ax.set_xticks(range(len(processes)))
    ax.set_xticklabels([f'P{p.pid + 1}' for p in processes])
    ax.set_ylabel('Время (порядковый номер события)')
    ax.set_title('Диаграмма времени (time-space diagram)')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close(fig)
    return filename


def plot_conflict():
    """Отдельная диаграмма с выделением конфликтующих обновлений."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axhline(1, color='blue', lw=2, label='P1: x = 0 + 1 = 1, VC=[1,0,0]')
    ax.axhline(2, color='red', lw=2, label='P2: x = 0 * 2 = 0, VC=[0,1,0]')
    ax.scatter([1], [1], color='blue', s=80, zorder=3)
    ax.scatter([1], [2], color='red', s=80, zorder=3)
    ax.text(1.05, 1, 'update x=1', va='center')
    ax.text(1.05, 2, 'update x=0 (конфликт)', va='center', color='red')
    ax.set_yticks([1, 2])
    ax.set_yticklabels(['P1', 'P2'])
    ax.set_xlim(0, 3)
    ax.set_title('Конфликтующие обновления ключа x')
    ax.legend(loc='lower right', fontsize=8)
    plt.tight_layout()
    plt.savefig('conflict.png')
    plt.close(fig)
    return 'conflict.png'