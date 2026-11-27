def happens_before(v1, v2):
    le = all(a <= b for a, b in zip(v1.vector, v2.vector))
    lt = any(a < b for a, b in zip(v1.vector, v2.vector))
    return le and lt


def concurrent(v1, v2):
    return not happens_before(v1, v2) and not happens_before(v2, v1)


class VectorClock:

    def __init__(self, n):
        self.n = n
        self.vector = [0] * n

    def increment(self, process_id):
        self.vector[process_id] += 1
        return self.vector[process_id]

    def update(self, received_vector):
        for i in range(self.n):
            self.vector[i] = max(self.vector[i], received_vector.vector[i])

    def copy(self):
        vc = VectorClock(self.n)
        vc.vector = self.vector.copy()
        return vc

    def __repr__(self):
        return str(self.vector)

    def __eq__(self, other):
        return isinstance(other, VectorClock) and self.vector == other.vector