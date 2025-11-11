

from fastapi import APIRouter
from pro_craft import Intel,AsyncIntel
from pro_craft.utils import create_session



# # 模拟获取当前用户的依赖项
# async def get_current_user(x_token: str = Header(...)):
#     if x_token != "valid-secret-token":
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid X-Token header")
#     return {"username": "admin", "roles": ["user", "admin"]}

# # 模拟一个管理员权限检查的依赖项
# async def verify_admin_role(user: dict = Depends(get_current_user)):
#     if "admin" not in user.get("roles", []):
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
#     return user


# router = APIRouter(
#     tags=["Admin"],
#     dependencies=[Depends(get_current_user), Depends(verify_admin_role)] # 统一的依赖项列表
# )


# # 模拟获取当前用户的依赖项
# async def get_current_user(x_token: str = Header(...)):
#     if x_token not in ["1234",
#                        "5678"]:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid X-Token header")
#     return {"username": "admin", "roles": ["user", "admin"]}


# router = APIRouter(
#     tags=["users"],
#     dependencies=[Depends(get_current_user)] # 统一的依赖项列表
# )


# @router.get("/dashboard")
# async def get_user(user_info :dict =  Depends(get_current_user)):
#     pass
#     return {"message": "Welcome to the admin dashboard!"}


def create_router(database_url: str,
                  slave_database_url: str,
                  model_name: str,
                  logger = None):
    """
    # TODO 整理改为异步
    创建一个包含 ProCraft 路由的 FastAPI APIRouter 实例。

    Args:
        database_url (str): 数据库连接字符串。
        model_name (str): 用于 Intel 实例的模型名称。
        api_key_secret (str, optional): 用于验证 API Key 的秘密字符串。
                                        如果提供，它将覆盖环境变量 PRO_CRAFT_API_KEY。
                                        如果都不提供，会使用硬编码的 'your_default_secret_key'。
    Returns:
        APIRouter: 配置好的 FastAPI APIRouter 实例。
    """

    intels = AsyncIntel(
        database_url=database_url,
        model_name=model_name,
        logger=logger
        )

    router = APIRouter(
        tags=["prompt"] # 这里使用 Depends 确保每次请求都验证
    )

    @router.get("/push_order",
                description="可选 train,inference,summary,finetune,patch",)
    async def push_order(demand: str, prompt_id: str, action_type: str = "train"):
        result = await intels.push_action_order(
            demand=demand,
            prompt_id=prompt_id,
            action_type=action_type
        )
        return {"message": "success", "result": result}

    @router.get("/get_latest_prompt")
    async def get_latest_prompt(prompt_id: str):
        with create_session(intels.engine) as session:
            result = await intels.get_prompts_from_sql(
                prompt_id=prompt_id,
                session=session
            )
        return {"message": "success", "result": result}

    @router.get("/sync_database")
    async def sync_database():
        result = await intels.sync_prompt_data_to_database(slave_database_url)
        return {"message": "success","result":result}
    

    @router.get("/roll_back")
    async def roll_back(prompt_id:str,version:str):
        with create_session(intels.engine) as session:
            result = await intels.get_prompts_from_sql(
                prompt_id=prompt_id,
                version = version,
                session=session
            )
            assert result.version == version
            await intels.save_prompt_increment_version(
                            prompt_id = prompt_id,
                            new_prompt = result.prompt,
                            use_case = result.use_case,
                            action_type = "inference",
                            demand = "",
                            score = 61,
                            session = session)
        return {"message": "success"}
    
    return router

