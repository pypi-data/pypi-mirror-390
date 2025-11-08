from fastmcp import FastMCP


from aitrados_broker.trade_middleware_service.requests import a_broker_request
from aitrados_broker.trade_middleware_service.trade_middleware_rpc_service import AitradosBrokerBackendService
from finance_trading_ai_agents_mcp.utils.common_utils import show_mcp_result

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


    @mcp.tool(title="Get Trading Account Summary.",description="Obtain information on trading account, holding positions, and pending orders at once.\n"
                                                               "Prefer using this method to obtain Account all information")
    async def get_trading_account_summary(broker_name: str=None):

        account_info = await get_list_result(fun_cls.GET_ALL_ACCOUNTS, broker_name=broker_name)
        holding_positions = await get_list_result(fun_cls.GET_ALL_POSITIONS, broker_name=broker_name)
        pending_orders=await get_list_result(fun_cls.GET_ALL_ACTIVE_ORDERS, broker_name=broker_name)
        result=f"""
## Current Trading Account
{account_info}
===============
## Current holding positions
{holding_positions}
==============
## Current pending orders
{pending_orders}

        """
        show_mcp_result(mcp, result, True)
        return result
    '''
    @mcp.tool
    async def send_order(broker_name: str=None):
        return "We are developing it(send_order) and it will be completed in a few days."
    @mcp.tool
    async def cancel_order(broker_name: str=None):
        return "We are developing it(send_order) and it will be completed in a few days."
    @mcp.tool
    async def get_position(broker_name: str=None):
        return ""
    @mcp.tool
    async def get_pending_orders(broker_name: str=None,):
        result = await get_list_result(fun_cls.GET_ALL_ACTIVE_ORDERS, broker_name=broker_name)
        show_mcp_result(mcp, result, True)
        return result
    @mcp.tool
    async def get_trading_account(broker_name: str=None):
        result =  await get_list_result(fun_cls.GET_ALL_ACCOUNTS,broker_name=broker_name)
        show_mcp_result(mcp, result, True)
        return result
    @mcp.tool
    async def get_holding_positions(broker_name: str=None  ):
        result =  await get_list_result(fun_cls.GET_ALL_POSITIONS,broker_name=broker_name)
        show_mcp_result(mcp, result, True)
        return result
    '''