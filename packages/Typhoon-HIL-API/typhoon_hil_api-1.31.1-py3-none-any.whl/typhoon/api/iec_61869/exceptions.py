#
# SV API
#
class IEC61869SVValidationException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
