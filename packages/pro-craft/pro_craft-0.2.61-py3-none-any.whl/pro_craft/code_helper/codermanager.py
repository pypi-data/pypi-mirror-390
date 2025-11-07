
from sqlalchemy import create_engine
import os
from typing import List
from .database import Base, CodeTemplate
from .vectorstore import VolcanoEmbedding
QDRANT_COLLECTION_NAME = "template_collection" # 你的 Qdrant collection 名称
from pro_craft.utils import create_session
from qdrant_client import QdrantClient, models
from uuid import uuid4
from .template_extract import extract_template
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct, CollectionStatus, Distance, VectorParams

class CoderTemplateManager():
    def __init__(self,
                 database_url = "mysql+pymysql://zxf_root:Zhf4233613%40@rm-2ze0793c6548pxs028o.mysql.rds.aliyuncs.com:3306/serverz",
                 model_name = "",
                 logger = None,
                ):
        database_url = database_url or os.getenv("database_url")
        assert database_url
        self.engine = create_engine(database_url, echo=False, # echo=True 仍然会打印所有执行的 SQL 语句
                                    pool_size=10,        # 连接池中保持的连接数
                                    max_overflow=20,     # 当pool_size不够时，允许临时创建的额外连接数
                                    pool_recycle=3600,   # 每小时回收一次连接
                                    pool_pre_ping=True,  # 使用前检查连接活性
                                    pool_timeout=30      # 等待连接池中连接的最长时间（秒）
                                    ) 
        self.embedding_model = VolcanoEmbedding(
            model_name = "doubao-embedding-text-240715",
            api_key = "39ad310a-c6f7-4d66-962e-1fbfa7e6edf1"
        )


        Base.metadata.create_all(self.engine)
        
        self.connection = QdrantClient(host="127.0.0.1", port=6333)

        self.connection.recreate_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=models.VectorParams(size=2560, distance=models.Distance.COSINE),
        )
        self.logger = logger
    
        # if model_name in ["gemini-2.5-flash-preview-05-20-nothinking",]:
        #     self.llm = BianXieAdapter(model_name = model_name)
        # elif model_name in ["doubao-1-5-pro-256k-250115","doubao-1-5-pro-32k-250115"]:
        #     self.llm = ArkAdapter(model_name = model_name)
        # else:
        #     raise Exception("error llm name")

    def get_embedding(self,text: str) -> List[float]:
        return self.embedding_model._get_text_embedding(text)
    
    def add_template(self,
                     use_case: str,
                     template_id: str,
                     description: str,):   
        template = extract_template(use_case)
        embedding_vector = self.get_embedding(description)
        points = [
                models.PointStruct(
                    id = str(uuid4()),
                    vector=embedding_vector,
                    payload={
                        "template_id": template_id,
                        "description": description,
                        "use_case": use_case,
                        "template": template,
                    }
                )
            ]
        self.connection.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            wait=True,
            points=points
        )
        # 数据库
        with create_session(self.engine) as session:
            new_template = CodeTemplate(
                template_id=template_id,
                version=1,
                description=description,
                template_code=template,
            )
            session.add(new_template)
            session.commit()
            session.refresh(new_template)
        return "success"


    def delete_template(self, template_id: str) -> bool:
        """
        逻辑删除指定的代码模板。
        """


        # 3. 使用属性删除点
        # 目标：删除所有 'color' 属性为 'red' 的点

        # 定义一个过滤器
        # 这个过滤器会匹配所有 payload 中 'color' 字段值为 'red' 的点
        _filter = Filter(
            must=[
                FieldCondition(
                    key="template_id",
                    match=MatchValue(value=template_id)
                )
            ]
        )
        self.connection.delete(
            collection_name=QDRANT_COLLECTION_NAME,
            points_selector=_filter,
            wait=True
        )


        with create_session(self.engine) as session:
            template = session.query(CodeTemplate).filter_by(template_id=template_id).first()
            if template:
                session.delete(template)
                session.commit()
                return True
        return False
    
        
    def search(self, text , limit , query_filter=None):
        query_vector = self.get_embedding(text)
        results = self.connection.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            query_filter=query_filter
        )
        return results

    def get_template_obj(self, template_id: str):
        # 模拟从数据库获取模板详情
        # 实际使用时，你需要根据你的数据库 setup 来实现
        with create_session(self.engine) as session:
            template = session.query(CodeTemplate).filter_by(template_id = template_id).first()
        return template