from mcp.server.fastmcp import FastMCP

from pro_craft import Intel

def create_mcp(database_url: str,
                  slave_database_url: str,
                  model_name: str):
    # region MCP Weather
    mcp = FastMCP("PromptManager")

    intels = Intel(
        database_url=database_url,
        model_name=model_name
        )

    @mcp.tool()
    def push_order(demand: str, prompt_id: str, action_type: str = "train") -> str:
        result = intels.push_action_order(
            demand=demand,
            prompt_id=prompt_id,
            action_type=action_type
        )
        return {"message": "success", "result": result}

    @mcp.tool()
    def get_latest_prompt(prompt_id: str) -> str:
        with create_session(intels.engine) as session:
            result = intels.get_prompts_from_sql(
                prompt_id=prompt_id,
                session=session
            )
        return {"message": "success", "result": result}


    @mcp.tool()
    def sync_database() -> str:
        result = intels.sync_prompt_data_to_database(slave_database_url)
        return {"message": "success","result":result}
    
    return mcp


if __name__ == "__main__":
    mcp = create_mcp()
    mcp.run(transport="streamable-http")
