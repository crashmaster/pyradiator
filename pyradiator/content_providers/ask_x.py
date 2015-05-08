import abc

import six


@six.add_metaclass(abc.ABCMeta)
class AskX(object):

    def get_instance(self):
        return self

    @abc.abstractmethod
    def __call__(self):
        return
