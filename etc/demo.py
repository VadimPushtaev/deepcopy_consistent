import threading
from copy import deepcopy

N = 2


def writer(d, reader_stopped):
    while not reader_stopped.is_set():
        d["for"] = True
        for i in range(N):
            d[i] += 1
        del d["for"]


def reader(d, reader_stopped):
    while True:
        cpy = deepcopy(d)
        prev = None
        for i in range(N):
            if prev is not None:
                if not (cpy[i] == prev or cpy[i] == prev - 1):
                    print('Error: {} was copied'.format(cpy))
                    reader_stopped.set()
                    return

            prev = cpy[i]


def main():
    d = {i: 0 for i in range(N)}
    reader_stopped = threading.Event()

    t1 = threading.Thread(target=writer, args=(d, reader_stopped))
    t2 = threading.Thread(target=reader, args=(d, reader_stopped))
    t1.start()
    t2.start()
    t1.join()
    t2.join()


if __name__ == '__main__':
    main()
