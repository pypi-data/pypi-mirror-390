from fastmcp import FastMCP


from aitrados_broker.trade_middleware_service.requests import a_broker_request
from aitrados_broker.trade_middleware_service.trade_middleware_rpc_service import AitradosBrokerBackendService

fun_cls=AitradosBrokerBackendService.IDENTITY.fun

async def get_list_result(function_name,broker_name: str=None):
    try:
        redata = await a_broker_request(function_name, broker_name=broker_name, timeout=5)
        if "result" in redata:
            return redata["result"]
        return redata["message"]
    except:
        return "Data access timed out; the broker may not be logged in. Please remind the user to log in."
def broker_list_tool(mcp:FastMCP):
    @mcp.tool
    async def get_position(broker_name: str=None):
        return ""
    @mcp.tool
    async def send_order(broker_name: str=None):
        return ""
    @mcp.tool
    async def cancel_order(broker_name: str=None):
        return ""
    @mcp.tool
    async def get_all_active_orders(broker_name: str=None,):
        return await get_list_result(fun_cls.GET_ALL_ACTIVE_ORDERS,broker_name=broker_name)
    @mcp.tool
    async def get_all_accounts(broker_name: str=None):
        return await get_list_result(fun_cls.GET_ALL_ACCOUNTS,broker_name=broker_name)
    @mcp.tool
    async def get_all_positions(broker_name: str=None,
                                full_symbol:str=None
                                ):
        return await get_list_result(fun_cls.GET_ALL_POSITIONS,broker_name=broker_name)
