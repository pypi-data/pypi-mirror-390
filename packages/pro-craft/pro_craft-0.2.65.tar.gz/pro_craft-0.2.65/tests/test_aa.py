from pro_craft.database import UseCase
from pro_craft.utils import create_async_session
from pro_craft import AsyncIntel

from sqlalchemy import select
import os

async def test_11():
    intels = AsyncIntel(database_url = "mysql+aiomysql://vc_agent:aihuashen%402024@rm-2ze0q808gqplb1tz72o.mysql.rds.aliyuncs.com:3306/digital-life2-test",
                        model_name="doubao-1-5-pro-32k-250115")
    async with create_async_session(intels.engine) as session:
        result = await session.execute(
              select(UseCase)
              .filter(UseCase.target=="intel-输入")
              .order_by(UseCase.timestamp.desc())
              .limit(100)
        )
        reu = result.scalars().all()

        print(reu,'reureureu')
        print(len(reu))
