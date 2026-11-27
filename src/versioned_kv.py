from src.vector_clock import VectorClock, happens_before


class VersionedKV:

    def __init__(self, n):
        self.n = n
        self.store = {}          # key -> (value, VectorClock)
        self.history = []        # журнал операций

    def put(self, key, value, vc, strategy='merge'):
        if key not in self.store:
            self.store[key] = (value, vc.copy())
            self.history.append((key, value, vc.copy(), "CREATE"))
            return value, vc.copy(), "created"

        old_val, old_vc = self.store[key]

        if happens_before(vc, old_vc):
            return old_val, old_vc, "ignored (older)"
        if happens_before(old_vc, vc):
            self.store[key] = (value, vc.copy())
            self.history.append((key, value, vc.copy(), "UPDATE"))
            return value, vc.copy(), "updated"

        # Конкурентные обновления
        if strategy == 'lww':
            self.store[key] = (value, vc.copy())
            self.history.append((key, value, vc.copy(), "LWW"))
            return value, vc.copy(), "conflict resolved by LWW"

        # strategy == 'merge'
        if isinstance(old_val, (int, float)) and isinstance(value, (int, float)):
            merged_val = old_val + value
        elif isinstance(old_val, str) and isinstance(value, str):
            merged_val = old_val + "|" + value
        else:
            merged_val = value

        merged_vc = VectorClock(self.n)
        for i in range(self.n):
            merged_vc.vector[i] = max(old_vc.vector[i], vc.vector[i])
        self.store[key] = (merged_val, merged_vc)
        self.history.append((key, merged_val, merged_vc, "MERGE"))
        return merged_val, merged_vc, "conflict resolved by merge"

    def get(self, key):
        return self.store.get(key)