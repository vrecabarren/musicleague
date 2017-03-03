
class EntrySortKey:
    def __init__(self, obj, **args):
        self.obj = obj

    def __lt__(self, other):
        return self._ordered_cmp(other.obj) < 0

    def __gt__(self, other):
        return self._ordered_cmp(other.obj) > 0

    def __eq__(self, other):
        return self._ordered_cmp(other.obj) == 0

    def __le__(self, other):
        return self._ordered_cmp(other.obj) <= 0

    def __ge__(self, other):
        return self._ordered_cmp(other.obj) >= 0

    def __ne__(self, other):
        return self._ordered_cmp(other.obj) != 0

    def _ordered_cmp(self, other):
        raise Exception("_ordered_cmp needs to be implemented!")
