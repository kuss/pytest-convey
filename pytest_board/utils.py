from queue import Empty

def flush_q(q):
    try:
        while True:
            q.get_nowait()
    except Empty:
        pass
