class Event:
    def __init__(self, eid, pid, etype, target=None, message=None):
        self.eid = eid
        self.pid = pid
        self.etype = etype      # INTERNAL, SEND, RECEIVE
        self.target = target
        self.message = message
        self.lamport_ts = None
        self.vc = None