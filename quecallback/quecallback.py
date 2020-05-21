from threading import Thread

import queue
import time


class QueuedCallback:
    def __init__(self,
                 que,
                 tertiary,
                 callback=None,
                 sleep=0.66):
        self.que = que
        self.tertiary = tertiary
        if callback is not None:
            self.callback = callback
        self.sleep = sleep
        self.stopped = True
        self.thread = None

    def __del__(self):
        self.stopped = True

    def __queue_loop(self):
        while not self.stopped:
            try:
                job = self.que.get(False)
            except queue.Empty:
                time.sleep(self.sleep)
            else:
                self._func_caller(job)

    def callback(self, result):
        print(result)

    def _func_caller(self, job):
        if job is None:
            return
        result = getattr(self.tertiary, job['function'])(**job['kwargs'])
        self.callback({'uid': job['uid'],
                       'result': result}
                      )

    def start(self, block=True):
        if not self.stopped:
            return
        print("-- Starting %s" % self.__class__.__name__)
        self.stopped = False
        if block:
            self.__queue_loop()
        else:
            self.thread = Thread(target=self.__queue_loop)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        if self.stopped:
            return
        print("-- Stopped %s" % self.__class__.__name__)
        self.stopped = True


if __name__ == '__main__':
    class SomeClass:
        def __init__(self):
            self.name = __class__.__name__

        def function_to_call(self, some_args, some_more_args):
            return [self.name, some_args, some_more_args]


    def some_callback(result):
        print(result)


    some_class = SomeClass()
    q = queue.Queue()
    qfc = QueuedCallback(q,
                         tertiary=some_class,
                         callback=some_callback
                         )
    qfc.start(block=False)

    jb = {'uid': 123456789,
          'function': 'function_to_call',
          'kwargs': {
              'some_args': 'Hello',
              'some_more_args': 'Goodbye'
              }
          }
    q.put(jb)

    time.sleep(3)
    qfc.stop()
