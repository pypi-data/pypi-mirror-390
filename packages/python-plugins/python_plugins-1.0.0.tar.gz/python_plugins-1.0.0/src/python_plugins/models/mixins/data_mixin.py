from sqlalchemy.orm import mapped_column
from sqlalchemy.types import JSON


class DataMixin:
    data = mapped_column(type_=JSON)

    def update_data(self, data: dict):
        if self.data is None:
            new_data = {}
        else:
            new_data = dict(self.data)
        for k in data:
            new_data[k] = data[k]
        self.data = new_data
