from tqdm.auto import tqdm
from joblib import parallel_backend
import joblib

class Metric:
    def __init__(self, name):
        self.name = name
        self.values = {}

    def get_name(self):
        return self.name

    def get_value(self, step, aname):
        ret = None
        tmp = self.values.get(step, None)
        if tmp:
            ret = tmp.get(aname, None)
        return ret

    def print(self, step, aname):
        print ("  - {}: {}{}".format(self.get_name(), self.get_value(step, aname), self.get_unit()))

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
