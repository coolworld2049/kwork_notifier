import pathlib

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

DEFAULT = "default"

sqlite_dir = pathlib.Path(__file__).parent.joinpath("sqlite")
sqlite_dir.mkdir(exist_ok=True)

jobstores = {
    DEFAULT: SQLAlchemyJobStore(f"sqlite:///{sqlite_dir.__str__()}/jobstore.sqlite")
}
executors = {DEFAULT: AsyncIOExecutor()}
job_defaults = {"coalesce": False, "max_instances": 3, "misfire_grace_time": 3600}

scheduler = AsyncIOScheduler(
    jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc
)
