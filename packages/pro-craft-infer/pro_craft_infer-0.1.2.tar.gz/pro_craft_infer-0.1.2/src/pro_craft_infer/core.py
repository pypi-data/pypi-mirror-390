from datetime import datetime, timedelta
from tqdm.asyncio import tqdm
import json
import os
import inspect
from pydantic import BaseModel, ValidationError, field_validator
from json.decoder import JSONDecodeError
from sqlalchemy import select, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from utils_z.content import create_async_session
from utils_z.re import extract_
from modusched.core import BianXieAdapter, ArkAdapter
from .database import Prompt, UseCase


class IntellectRemoveFormatError(Exception):
    pass

class IntellectRemoveError(Exception):
    pass

class ModelNameError(Exception):
    pass

class AsyncIntel():
    def __init__(self,
                 database_url = "",
                 model_name = "",
                 logger = None,
                ):
        database_url = database_url or os.getenv("database_url")
        self.logger = logger
        try:
            assert database_url
            assert 'aio' in database_url
        except AssertionError as e:
            raise IntellectRemoveFormatError(f"异步服务url必须提供, 且必须是aiomysql配置") from e

        self.engine = create_async_engine(database_url, echo=False,
                                    pool_size=10,        # 连接池中保持的连接数
                                    max_overflow=20,     # 当pool_size不够时，允许临时创建的额外连接数
                                    pool_recycle=3600,   # 每小时回收一次连接
                                    pool_pre_ping=True,  # 使用前检查连接活性
                                    pool_timeout=30      # 等待连接池中连接的最长时间（秒）
                                           )

        if "gemini" in model_name:
            self.llm = BianXieAdapter(model_name = model_name)
        elif "doubao" in model_name:
            self.llm = ArkAdapter(model_name = model_name)
        else:
            raise ModelNameError("AsyncIntel init get error model_name from zxf")

    async def get_prompt(self,prompt_id,version,session):
        """
        获取指定 prompt_id 的最新版本数据，通过创建时间判断。
        """
        if version:
            stmt_ = select(Prompt).filter(
                Prompt.prompt_id == prompt_id,
                Prompt.version == version
            )
        else:  
            stmt_ = select(Prompt).filter(
                Prompt.prompt_id == prompt_id,
            )
        stmt = stmt_.order_by(
                desc(Prompt.timestamp), # 使用 sqlalchemy.desc() 来指定降序
                desc(Prompt.version)    # 使用 sqlalchemy.desc() 来指定降序
            )

        result = await session.execute(stmt)
        result = result.scalars().first()

        return result
    
    async def get_prompt_safe(self,
                             prompt_id: str,
                             version = None,
                             session = None) -> Prompt:
        """
        从sql获取提示词
        """
        prompt_obj = await self.get_prompt(prompt_id=prompt_id,version=version,session=session)
        if prompt_obj:
            return prompt_obj
        if version:
            prompt_obj = await self.get_prompt(prompt_id=prompt_id,version=None,session=session)

        if prompt_obj is None:
            raise IntellectRemoveError("不存在的prompt_id")
        return prompt_obj

    # go to 
    async def inference_format(self,
                    input_data: dict | str,
                    prompt_id: str,
                    version: str = None,
                    OutputFormat: object | None = None,
                    ExtraFormats: list[object] = [],
                    ConTent_Function = None,
                    AConTent_Function = None,
                    again = True,
                    ):
        """
        这个format 是严格校验模式, 是interllect 的增强版, 会主动校验内容,并及时抛出异常(或者伺机修正)
        ConTent_Function
        AConTent_Function
        两种方式的传入方式, 内容未通过就抛出异常

        # TODO 增加兜底版本
        """                
        base_format_prompt = """
按照一定格式输出, 以便可以通过如下校验

使用以下正则检出
"```json([\s\S]*?)```"
使用以下方式验证
"""     
        assert isinstance(input_data,(dict,str))

        input_ = json.dumps(input_data,ensure_ascii=False) if isinstance(input_data,dict) else input_data
        output_format = base_format_prompt + "\n".join([inspect.getsource(outputformat) for outputformat in ExtraFormats]) + inspect.getsource(OutputFormat) if OutputFormat else ""

        async with create_async_session(self.engine) as session:
            result_obj = await self.get_prompt_safe(prompt_id=prompt_id,version= version,
                                                    session=session)
            prompt = result_obj.prompt
            ai_result = await self.llm.aproduct(prompt + output_format + "\nuser:" +  input_)
        
        def check_json_valid(ai_result,OutputFormat):
            try:
                json_str = extract_(ai_result,r'json')
                ai_result = json.loads(json_str)
                OutputFormat(**ai_result)

            except JSONDecodeError as e:
                self.logger.error(f'{prompt_id} & {json_str} & 生成的内容为无法被Json解析')
                return 0
            except ValidationError as e:
                err_info = e.errors()[0]
                self.logger.error(f'{prompt_id} & {json_str} & {err_info["type"]}: 属性:{err_info['loc']}, 发生了如下错误: {err_info['msg']}, 格式校验失败, 当前输入为: {err_info['input']} 请检查 ')
                return 0
            except Exception as e:
                raise Exception(f"Exc Error {prompt_id} : {e}") from e
            return 1
            
        if OutputFormat:
            check_result = check_json_valid(ai_result,OutputFormat)
            if check_result ==0 and again:
                ai_result = await self.llm.aproduct(ai_result + output_format)
                check_result_ = check_json_valid(ai_result,OutputFormat)
                if check_result_ ==0:
                    raise IntellectRemoveFormatError(f"prompt_id: {prompt_id} 多次生成的内容均未通过OutputFormat校验, 当前内容为: {ai_result}")
            json_str = extract_(ai_result,r'json')
            ai_result = json.loads(json_str)
                    
        if ConTent_Function:# TODO
            ConTent_Function(ai_result,input_data)
        
        if AConTent_Function:
            await AConTent_Function(ai_result,input_data)

        self.logger and self.logger.info(f'intellect & {input_data} & {ai_result}')
        return ai_result
    
    async def inference_format_gather(self,
                    input_datas: list[dict | str],
                    prompt_id: str,
                    version: str = None,
                    OutputFormat: object | None = None,
                    ExtraFormats: list[object] = [],
                    **kwargs,
                    ):
                
        tasks = []
        for input_data in input_datas:
            tasks.append(
                self.inference_format(
                    input_data = input_data,
                    prompt_id = prompt_id,
                    version = version,
                    OutputFormat = OutputFormat,
                    ExtraFormats = ExtraFormats,
                    **kwargs,
                )
            )
        results = await tqdm.gather(*tasks,total=len(tasks))
        # results = await asyncio.gather(*tasks, return_exceptions=False)
        return results

    async def sync_log(self,log_path):
        async with create_async_session(self.engine) as session:
            await self.save_use_case(log_file = log_path,session = session)

    async def save_use_case(self,log_file,session = None):
        source_results = await session.execute(
            select(UseCase)
            .order_by(UseCase.timestamp.desc())
            .limit(1)
        )
        records_to_sync = source_results.scalars().one_or_none()
        if records_to_sync:
            last_time = records_to_sync.timestamp
            one_second = timedelta(seconds=1)
            last_time += one_second
        else:
            last_time = datetime(2025, 1, 1, 14, 30, 0)

        with open(log_file,'r') as f:
            x = f.read()

    
        def deal_log(resu):
            if len(resu) <3:
                return 
            try:
                create_time = resu[1]
                level = resu[2]
                funcname = resu[3]
                line = resu[4]
                pathname = resu[5]
                message = resu[6]

                dt_object = datetime.fromtimestamp(float(create_time.strip()))
                message_list = message.split("&")
                if len(message_list) == 3:
                    func_name, input_, output_ = message_list
                elif len(message_list) == 2:
                    input_, output_ = message_list
                    func_name = "只有两个"
                elif len(message_list) == 1:
                    input_  = message_list[0]
                    output_ = " "
                    func_name = "只有一个"

                if dt_object > last_time:
                    use_case = UseCase(
                        time = create_time.strip(),
                        level = level.strip(),
                        timestamp =dt_object.strftime('%Y-%m-%d %H:%M:%S.%f'),
                        filepath=pathname.strip(),
                        function=func_name.strip(),
                        lines=line.strip(),
                        input_data=input_.strip(),
                        output_data=output_.strip(),
                    )
                    session.add(use_case)
            except Exception as e:
                raise


        for res in x.split("||"):
            resu = res.split("$")
            deal_log(resu)

        await session.commit() # 提交事务，将数据写入数据库

