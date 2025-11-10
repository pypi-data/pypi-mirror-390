from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

# https://docs.sqlalchemy.org/en/20/intro.html
# https://habr.com/ru/companies/amvera/articles/850470/


class BaseModel(AsyncAttrs, DeclarativeBase):
    pass
