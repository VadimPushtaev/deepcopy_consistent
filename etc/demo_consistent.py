import threading
from copy import copy

from deepcopy_consistent import ConsistentlyCopyableDict

N = 2000000


def writer(d, reader_stopped):
    while not reader_stopped.is_set():
        d["for"] = True
        for i in range(N):
            d[i] += 1
        del d["for"]


def reader(d, reader_stopped):
    while True:
        cpy = copy(d)
        prev = None
        for i in range(N):
            if prev is not None:
                if not (cpy[i] == prev or cpy[i] == prev - 1):
                    print('Error: {} was copied'.format(cpy))
                    reader_stopped.set()
                    return
            prev = cpy[i]


def main():
    d = ConsistentlyCopyableDict({i: 0 for i in range(N)})
    reader_stopped = threading.Event()

    threads = [
        threading.Thread(target=writer, args=(d, reader_stopped)),
        threading.Thread(target=reader, args=(d, reader_stopped)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()
