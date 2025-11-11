from datetime import datetime

from pydantic import BaseModel


class GetWorkerWorkers(BaseModel):
    """Represents all data of a worker"""

    name: str
    status: str
    queues: list[str]
    jobCount: int


class GetWorkerJobqueue(BaseModel):
    """Represents all data of a jobqueue"""

    name: str
    activ: str


class GetWorkerReturningJobs(BaseModel):
    """Represents all data of a returningjob"""

    name: str
    info: str
    nextExecution: datetime


class GetWorkerJobs(BaseModel):
    """Represents all data of a job"""

    placeInQueue: int
    name: str
    queueName: str


class RemoveAddQueueToWorker(BaseModel):
    """Represents all data of a queue"""

    queue_name: str
