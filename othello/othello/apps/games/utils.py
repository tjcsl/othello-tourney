import threading
from queue import Queue


def enqueue_stream_helper(stream, q, event):
    """
    Continuously reads from stream and puts any results into
    the queue `q`
    """
    for line in iter(stream.readline, b''):
        if event.is_set():
            break
        q.put(line)
    stream.close()


def get_stream_queue(stream, event):
    """
    Takes in a stream, and returns a Queue that will return the output from that stream. Starts a background thread as a side effect.
    """
    threading.Thread(target=enqueue_stream_helper, args=(stream, q := Queue(), event), daemon=True).start()
    return q
