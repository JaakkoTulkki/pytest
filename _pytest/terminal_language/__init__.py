from abc import ABCMeta, abstractmethod


class Language(metaclass=ABCMeta):

    @abstractmethod
    def get_internal_error(self):
        raise NotImplementedError('Not implemented')

