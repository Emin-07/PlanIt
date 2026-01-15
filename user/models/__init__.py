from datetime import datetime, timezone
from typing import Annotated

from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column


def get_current_utc_time():
    return datetime.now(timezone.utc).isoformat()


intpk = Annotated[int, mapped_column(Integer, primary_key=True)]
DateStr = Annotated[str, mapped_column(String, default=get_current_utc_time)]
