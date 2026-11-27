from src.event import Event
from src.lamport_clock import LamportClock
from src.vector_clock import VectorClock


class Process:
    def __init__(self, pid, n, event_log,
                 lamport_clock=None, vector_clock=None):
        self.pid = pid
        self.n = n
        self.event_log = event_log
        self.lamport = lamport_clock or LamportClock()
        self.vc = vector_clock or VectorClock(n)

    def internal_event(self, message=None):
        self.lamport.increment()
        self.vc.increment(self.pid)
        e = Event(len(self.event_log), self.pid, "INTERNAL", message=message)
        e.lamport_ts = self.lamport.value
        e.vc = self.vc.copy()
        self.event_log.append(e)
        return e

    def send_message(self, target_pid, message):
        self.lamport.increment()
        self.vc.increment(self.pid)
        e = Event(len(self.event_log), self.pid, "SEND",
                  target=target_pid, message=message)
        e.lamport_ts = self.lamport.value
        e.vc = self.vc.copy()
        self.event_log.append(e)
        return (self.lamport.value, self.vc.copy(), message)

    def receive_message(self, from_pid, lamport_recv, vc_recv, message):
        self.lamport.update(lamport_recv)
        self.vc.update(vc_recv)
        self.vc.increment(self.pid)
        e = Event(len(self.event_log), self.pid, "RECEIVE",
                  target=from_pid, message=message)
        e.lamport_ts = self.lamport.value
        e.vc = self.vc.copy()
        self.event_log.append(e)
        return e