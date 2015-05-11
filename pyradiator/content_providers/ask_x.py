import abc

import six


@six.add_metaclass(abc.ABCMeta)
class AskX(object):

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @abc.abstractmethod
    def __call__(self):
        return
