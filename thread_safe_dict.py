import threading
from dataclasses import dataclass
from typing import MutableMapping, Any, Optional

TOMBSTONE = object()


@dataclass
class DictLayer:
    data: dict
    in_use: bool
    root: bool


class ThreadSafeDict(MutableMapping):
    def __len__(self) -> int:
        pass

    def __init__(self, update_from: Optional[dict] = None) -> None:
        self._lock = threading.RLock()
        self._layers = [DictLayer(data={}, in_use=True, root=True)]

        if update_from is not None:
            self.update(update_from)

    def _clean_layers(self) -> None:
        with self._lock:
            while not self._layers[-1].in_use and not self._layers[-1].root:
                to_be_merged = self._layers.pop()
                target = self._layers[-1]
                for k, v in to_be_merged.data.items():
                    if v is TOMBSTONE:
                        if target.root:
                            del target.data[k]
                        else:
                            target.data[k] = TOMBSTONE
                    else:
                        target.data[k] = v

    def __iter__(self):
        with self._lock:
            self._clean_layers()
            layers: list[DictLayer] = [layer for layer in self._layers]
            new_layer = DictLayer(data={}, in_use=True, root=False)
            self._layers.append(new_layer)

        prev_layers: list[DictLayer] = []
        for layer in reversed(layers):
            for k in layer.data:
                in_prev_layers = False
                for prev_layer in prev_layers:
                    if k in prev_layer.data:
                        in_prev_layers = True
                        break
                if not in_prev_layers:
                    yield k

            prev_layers.append(layer)

    def __setitem__(self, k, v) -> None:
        with self._lock:
            self._clean_layers()
            self._layers[-1].data[k] = v

    def __delitem__(self, k) -> None:
        with self._lock:
            self._clean_layers()
            layer = self._layers[-1]
            if layer.root:
                del layer.data[k]
            else:
                found_in_other_layer = False
                for layer in reversed(self._layers[:-1]):
                    if k in layer.data:
                        if layer.data[k] is TOMBSTONE:
                            break
                        else:
                            found_in_other_layer = True
                            break
                if not found_in_other_layer:
                    raise KeyError(k)
                layer.data[k] = TOMBSTONE

    def __getitem__(self, k) -> Any:
        for layer in reversed(self._layers):
            if k in layer.data:
                if layer.data[k] is TOMBSTONE:
                    raise KeyError(k)
                else:
                    return layer.data[k]
