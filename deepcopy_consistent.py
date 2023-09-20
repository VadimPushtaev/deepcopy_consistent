import threading
import time
from collections import UserDict, deque
from typing import Deque, Any


def _idempotent_del(d: dict, key: Any):
    try:
        del d[key]
    except KeyError:
        pass


class ConsistentlyCopyableDict(UserDict):
    def __init__(self, *args, **kwargs):
        self._lock = threading.Lock()
        self._cv = threading.Condition()
        self._delta_idx = 0
        self._deltas: dict[int, Deque[Any]] = {}

        super().__init__(*args, **kwargs)

    def __copy__(self) -> 'ConsistentlyCopyableDict':
        delta_idx = self._deploy_delta_collector()
        copy_of_data = {k: v for k, v in list(self.data.items())}
        with self._lock:
            delta_queue = self._deltas.pop(delta_idx)

        i = 0
        while delta_queue:
            i += 1
            op = delta_queue.popleft()
            op(copy_of_data)
        print('Length of delta queue was {}'.format(i))

        return ConsistentlyCopyableDict(copy_of_data)

    def _deploy_delta_collector(self) -> int:
        with self._lock:
            delta_idx = self._delta_idx
            self._deltas[delta_idx] = deque()

            self._delta_idx += 1

            return delta_idx

    def __setitem__(self, key, value):
        with self._lock:
            for delta in self._deltas.values():
                delta.append(lambda d: d.__setitem__(key, value))

            super().__setitem__(key, value)

    def __delitem__(self, key):
        with self._lock:
            for delta in self._deltas.values():
                delta.append(lambda d: _idempotent_del(d, key))

            super().__delitem__(key)
