class DocumentTable:
    def __init__(self, doc):
        self.doc = doc
        self.nomenclature = None
        self.amount = 0
        self.status = None


class Document:
    DATE_FORMAT = '%d.%m.%Y %H:%M:%S'

    def __init__(self, num, date, type, storage, status):
        if num.isdigit():
         self._num = int(num)
        else:
            raise TypeError('Document: document number is not digit')
        try:
            self.date = datetime.strptime(date, self.DATE_FORMAT)
        except ValueError:
            raise ValueError(f'Document: неверный формат даты. Получена дата формата {date}, тогда как ожидается {self.DATE_FORMAT}')
        self.type = type
        self.storage = storage
        self.status = status

    @property
    def num(self):
        return self._num

    def __str__(self):
        return f'Задание {self._num} от {self.date.strftime(self.DATE_FORMAT)}'