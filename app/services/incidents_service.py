from datetime import datetime

from app.api.models.users import IncidentData
from app.repositories.models import ColumnValue
from app.utils import UnitOfWork


class IncidentService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def add_incident(self, data: IncidentData):
        data = data.model_dump(exclude_none=True)
        async with self.uow:
            result = await self.uow.incident_model.add_one(data)
            result: IncidentData = IncidentData.model_validate(result.__dict__)
            await self.uow.commit()
        return result

    async def end_incident(self, url_id: int):
        async with self.uow:
            last_incident = await self.uow.incident_model.find_one(url_id=url_id, ended_at=None)
            incident = last_incident.__dict__
            cur_time = datetime.now()
            duration = cur_time - incident['started_at']
            await self.uow.incident_model.update_one(column_and_value=ColumnValue(column_name='id', column_value=incident["id"]),
                                                     values={'ended_at': cur_time, 'duration': duration.total_seconds()})
            await self.uow.commit()



