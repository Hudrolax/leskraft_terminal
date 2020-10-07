class Nomenclature:
    def __init__(self, code, name):
        self._code = code
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if isinstance(name, str):
            self._name = name
        else:
            raise TypeError(f'Nomenclature name.setter: name must be str type, but {type(name)} got.')

    @property
    def code(self):
        return self._code

    def __str__(self):
        return f'{self.name} ({self.code})'