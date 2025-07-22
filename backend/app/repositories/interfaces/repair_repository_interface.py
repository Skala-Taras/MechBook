from abc import ABC, abstractmethod


class IRepairRepository(ABC):

    @abstractmethod
    def add(self, data: dict):
        pass

    @abstractmethod
    def edit(self, repair_id: int, data: dict):
        pass

    @abstractmethod
    def get_data_by_id(self, repair_id: int):
        pass

    @abstractmethod
    def delete(self, repair_id: int):
        pass

    @abstractmethod
    def recently(self):
        pass