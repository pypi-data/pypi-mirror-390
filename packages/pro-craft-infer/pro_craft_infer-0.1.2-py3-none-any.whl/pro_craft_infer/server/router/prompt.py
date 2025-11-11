from fastapi import APIRouter, HTTPException, status, Header, Depends
from pro_craft_infer.core import AsyncIntel
from pydantic import BaseModel, Field

class PromptResponse(BaseModel):
    msg: str = Field(..., description="信息")
    content: dict| str = None


def create_router(database_url: str,
                  model_name: str,
                  logger = None):

    intels = AsyncIntel(
        database_url=database_url,
        model_name=model_name,
        logger=logger
        )

    router = APIRouter(
        tags=["log"], # 这里使用 Depends 确保每次请求都验证
    )
    @router.get("/sync_log")
    async def sync_log(log_path:str):
        try:
            result = await intels.sync_log(log_path)
            return PromptResponse(msg = "success",content="")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"{e}"
            )
    
    return router