from abc import ABCMeta, abstractmethod


class Language(metaclass=ABCMeta):

    @abstractmethod
    def get_show_traceback_instructions(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_internal_error(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_plugin_registered(self, plugin):
        raise NotImplementedError('Not implemented')

