import json
from typing import Optional, Annotated

from fastapi import Depends
from fastmcp import FastMCP
from pydantic import Field

from aitrados_broker.addition_custom_mcps.parameter_validator.send_order_params import SendOrderParams, OrderTypeEnum, \
    OffsetEnum, DirectionEnum
from aitrados_broker.trade_middleware_service.requests import a_broker_request
from aitrados_broker.trade_middleware_service.trade_middleware_rpc_service import AitradosBrokerBackendService
from finance_trading_ai_agents_mcp.utils.common_utils import show_mcp_result


fun_cls=AitradosBrokerBackendService.IDENTITY.fun

async def get_broker_result(function_name,*args,**kwargs):
    try:
        redata = await a_broker_request(function_name, *args,**kwargs, timeout=5)
        if "result" in redata:

            return redata["result"]
        return redata["message"]
    except:
        return "Data access timed out; the broker may not be logged in. Please remind the user to log in."
def broker_list_tool(mcp:FastMCP):


    @mcp.tool(title="Get Trading Account Summary.",description="Obtain information on trading account, holding positions, and pending orders at once.\n"
                                                               "Prefer using this method to obtain Account all information."
                                                            )
    async def get_trading_account_summary(

            broker_name: Optional[str] = Field(None,description="The broker name,Unless otherwise requested by the user, the default value shall be retained."),
            #full_symbol_or_broker_symbol: Optional[str] = Field(None,description="This query retrieves the holding positions and pending orders for a specific asset. If not specified, it retrieves all assets."),

    ):

        full_symbol_or_broker_symbol=None
        account_info = await get_broker_result(fun_cls.GET_ALL_ACCOUNTS, broker_name=broker_name,full_symbol_or_broker_symbol=full_symbol_or_broker_symbol)
        holding_positions = await get_broker_result(fun_cls.GET_ALL_POSITIONS, broker_name=broker_name,full_symbol_or_broker_symbol=full_symbol_or_broker_symbol)
        pending_orders=await get_broker_result(fun_cls.GET_ALL_ACTIVE_ORDERS, broker_name=broker_name,ffull_symbol_or_broker_symbol=full_symbol_or_broker_symbol)
        if isinstance(account_info,dict|list):
            account_info=json.dumps(account_info)
        if isinstance(holding_positions,dict|list):
            holding_positions=json.dumps(holding_positions)
        if isinstance(pending_orders,dict|list):
            pending_orders=json.dumps(pending_orders)

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
        show_mcp_result(mcp, result, False)
        return result

    @mcp.tool(
        title="Send Trading Order",
        description="Submit a new trading order for any financial instrument"
    )
    async def send_order(
        full_symbol_or_broker_symbol: str = Field(description="The full symbol or broker symbol of the financial instrument to be traded"),
        type: OrderTypeEnum = Field(description="Order type: LIMIT (limit order), MARKET (market order), STOP (stop order)"),
        volume: float = Field(gt=0, description="Order volume/quantity, must be greater than 0"),
        price: float = Field(ge=0, description="Order price. For limit orders this is the limit price, for market orders this can be 0. Must be non-negative"),
        offset: OffsetEnum = Field(description="Position offset flag: OPEN (open position), CLOSE (close position)"),
        direction: DirectionEnum = Field(description="Trading direction: LONG (buy/long position), SHORT (sell/short position)"),
        broker_name: str | None = Field(None, description="The broker name,Unless otherwise requested by the user, the default value shall be retained.")
    ):


        try:

            result = await get_broker_result(
                fun_cls.SEND_ORDER,
                broker_name=broker_name,
                full_symbol_or_broker_symbol=full_symbol_or_broker_symbol,
                type=type.value,
                volume=volume,
                price=price,
                offset=offset.value,
                direction=direction.value
            )
            show_mcp_result(mcp, result, False)
            return result

        except Exception as e:
            error_msg = f"Parameter validation failed: {str(e)}"
            show_mcp_result(mcp, error_msg, True)
            return error_msg

    @mcp.tool(
        title="Cancel Trading Order",
        description="Cancel an existing pending trading order"
    )
    async def cancel_order(
            full_symbol_or_broker_symbol: Optional[str] = Field(None,description="The full symbol or broker symbol of the asset to cancel."),
            order_id: Optional[str] = Field(None, description="The order ID to cancel."),
            broker_name: Optional[str] = Field(None, description="The broker name,Unless otherwise requested by the user, the default value shall be retained.")
        ):
        if not order_id and not full_symbol_or_broker_symbol:
            show_mcp_result(mcp, "Please specify the order_id or the full_symbol_or_broker_symbol.", True)
            return "Please specify the order_id or the full_symbol_or_broker_symbol."

        result = await get_broker_result(fun_cls.CANCEL_ORDER, broker_name=broker_name,
                                               full_symbol_or_broker_symbol=full_symbol_or_broker_symbol,
                                         order_id=order_id)
        show_mcp_result(mcp, result, False)
        return result
