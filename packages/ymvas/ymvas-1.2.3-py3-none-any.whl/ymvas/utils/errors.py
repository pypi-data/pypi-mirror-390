



class YException(Exception):
    data: dict = {}

    def __init__(self, key:str , amsg = {}):
        from .messages import errors

        self._key  = key
        self._data = errors[key]
        self._msg  = self._data['msg']
        self._code = self._data['code']

        self._msg  = self._msg.format(**amsg)

        super().__init__(self._msg)

