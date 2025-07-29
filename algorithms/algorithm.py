from tqdm.auto import tqdm
from joblib import parallel_backend
import joblib

class Algorithm:
    def __init__(self, name):
        self.name = name
        self.classifier = {}
        self.scale = None
        self.queue = {}
        self.numbers = {}

    def get_name(self):
        return self.name

    def get_queue_length(self, step):
        lst = self.queue.get(step, [])
        return len(lst)

    def add_queue(self, window, step):
        ret = True
        if step not in self.queue:
            self.queue[step] = []

        if len(lst) < 5:
            lst.append(item)
        else:
            ret = False
        return ret

    def learning(self, windows, step):
        pass

    def detection(self, window, step):
        pass

    def get_queue(self, step):
        ret = []
        if step in self.queue:
            ret = self.queue[step]
        return ret

    def get_num_item(self, step):
        ret = 0
        if step in self.queue:
            ret = len(self.queue[step])
        return ret

    def set_num_of_windows(self, is_training, num):
        if is_training:
            self.numbers["training"] = num
        else:
            self.numbers["testing"] = num

    def get_num_of_windows(self, is_training):
        ret = 0
        if is_training:
            ret = self.numbers["training"]
        else:
            ret = self.numbers["testing"]
        return ret

    def enqueue(self, step, item):
        if step not in self.queue:
            self.queue[step] = []
        self.queue[step].append(item)

    def flush(self, step):
        if step in self.queue:
            del self.queue[step]
            self.queue[step] = []

class TQDMProgressBar(joblib.parallel.Parallel):
    def __init__(self, *args, total=None, **kwargs):
        self._total = total
        self._pbar = tqdm(total=total)
        super().__init__(*args, **kwargs)

    def print_progress(self):
        completed = self.n_completed_tasks
        self._pbar.n = completed
        self._pbar.refresh()

    def __del__(self):
        self._pbar.close()
