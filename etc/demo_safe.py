import threading

from thread_safe_dict import ThreadSafeDict

N = 2


def copy_naive(d: dict) -> dict:
    result = {}
    for key in d.keys():
        result[key] = d[key]

    return result


def writer(d, reader_stopped):
    while not reader_stopped.is_set():
        for i in range(N):
            d[i] += 1


def reader(d, reader_stopped):
    while True:
        cpy = copy_naive(d)
        print(cpy)
        prev = None
        for i in range(N):
            if prev is not None:
                if not (cpy[i] == prev or cpy[i] == prev - 1):
                    print('Error: {} was copied'.format(cpy))
                    reader_stopped.set()
                    return
            prev = cpy[i]


def main():
    d = ThreadSafeDict({i: 0 for i in range(N)})
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
