#
# MMS Server API
#
class MMSValidationException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
