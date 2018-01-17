from . import Language


class English(Language):
    def get_internal_error(self):
        return "INTERNALERROR>"
