from sqlalchemy import Column, Integer, String, Text, DateTime, text, UniqueConstraint, Boolean, func, Float, Double
from sqlalchemy.orm import declarative_base

from datetime import datetime, timedelta

FileBase = declarative_base()


# template_id (PK)
#  template_name (e.g., "FastAPI Router Endpoint")
#  description (e.g., "FastAPI服务路由器中的单个API端点，包含Pydantic校验、异步调用、Try-Except错误处理和日志记录。")
#  template_code (实际的模板代码字符串)
#  suggested_naming_conventions (JSONB 或文本)
#  usage_guidance (文本)
#  language (e.g., "Python")
#  framework (e.g., "FastAPI")
#  version
#  created_by
#  created_at
#  last_updated_at


from sqlalchemy import Column, Integer, String, Text, DateTime, text, UniqueConstraint, Boolean, func, Float, Double
from sqlalchemy.orm import declarative_base

from datetime import datetime, timedelta

Base = declarative_base()

class CodeTemplate(Base):
    __tablename__ = 'code_template'
    template_id = Column(String(255), primary_key=True, nullable=False, comment="自增")
    description = Column(Text, nullable=False, comment="Detailed description of the template")
    template_code = Column(Text, nullable=False, comment="The actual code of the template")
    version = Column(Integer, nullable=True, comment="Template version")
    # UniqueConstraint('template_name', name='uq_template_name') # 如果 template_name 应该是唯一的
