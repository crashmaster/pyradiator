import abc

import six


@six.add_metaclass(abc.ABCMeta)
class AskX(object):

    @abc.abstractmethod
    def __call__(self):
        return
