from app.repositories.interfaces.repair_repository_interface import IRepairRepository
from app.schemas.repair import RepairCreate, RepairEditData, RepairExtendedInfo


class RepairService:
    def __init__(self, user_repo: IRepairRepository):
        self.user_repo = user_repo

    @staticmethod
    def __validate_if_repair_exist(result: bool) -> None:
        if not result:
            raise ValueError("Not Found")

    def create(self, repair_data: RepairCreate):

        # data ={
        #     "repair_description": repair_data.repair_description,
        #     "notes": repair_data.notes,
        #     "vehicle_id": repair_data.vehicle_id
        # }
        result = self.user_repo.add(repair_data.dict())
        return result #repair_id

    def get(self, repair_id: int) -> RepairExtendedInfo:
        repair_object = self.user_repo.get_data_by_id(repair_id)
        if not repair_object:
            raise ValueError("Not Found")
        return repair_object

    def recently(self):
        print("GOOD")
        return self.user_repo.recently()

    def edit_data(self, repair_id: int, repair_data: RepairEditData) -> None:
        data = repair_data.dict(exclude_unset=True)
        data.update({"repair_id": repair_id})
        result = self.user_repo.edit(data)
        print(result)
        self.__validate_if_repair_exist(result)

    def delete(self, repair_id: int) -> None:
        result = self.user_repo.delete(repair_id)
        print(result)
        self.__validate_if_repair_exist(result)


