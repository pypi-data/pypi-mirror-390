from fastmcp import  FastMCP


from finance_trading_ai_agents_mcp.addition_custom_mcp.addition_custom_mcp_interface import AdditionCustomMcpInterface
from finance_trading_ai_agents_mcp.parameter_validator.analysis_departments import analysis_department

from aitrados_broker.addition_custom_mcps.broker_mcp import broker_list_tool


class AdditionBrokerMcpService(AdditionCustomMcpInterface):
    def add_mcp_server_name(self)->FastMCP:
        mcp = FastMCP(analysis_department.BROKER)
        broker_list_tool(mcp)
        return mcp