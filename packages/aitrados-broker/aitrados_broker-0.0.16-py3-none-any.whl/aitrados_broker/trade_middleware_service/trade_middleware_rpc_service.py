import traceback
from typing import Dict

from aitrados_api.common_lib.response_format import ErrorResponse, UnifiedResponse
from aitrados_api.trade_middleware.backend_service import BackendService
from loguru import logger

from aitrados_broker.addition_custom_mcps.parameter_validator.send_order_params import SendOrderParams
from aitrados_broker.trade_middleware_service.rpc_data_response import BrokerRpcDataResponse
from aitrados_broker.utils.broker_gateway import BrokerGateway
from aitrados_broker.utils.provider_setting import TomlToBrokerSetting
from aitrados_broker.trade_middleware_service.trade_middleware_identity import broker_identity
from aitrados_broker.utils.common_utils import broker_data_to_json
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import OrderRequest, CancelRequest, SubscribeRequest


class AitradosBrokerBackendService(BackendService):

    IDENTITY = broker_identity
    def __init__(self):
        self.main_engine: MainEngine=None
        self.all_broker_setting:Dict[str,dict]= {}
        super().__init__()


    def init_main_engine(self)->MainEngine:
        if self.main_engine:
            return self.main_engine


        from vnpy.event import EventEngine
        from vnpy.trader.setting import SETTINGS
        from vnpy.trader.engine import MainEngine
        from vnpy.trader.logger import DEBUG
        """
        Running in the child process.
        """
        SETTINGS["log.active"] = True
        SETTINGS["log.level"] = DEBUG
        SETTINGS["log.console"] = True
        SETTINGS["log.file"] = False

        event_engine = EventEngine()
        self.main_engine = MainEngine(event_engine)
        # main_engine.add_gateway(OkxGateway,"ib")
        # main_engine.connect(ctp_setting, "ib")
        return self.main_engine
    def __get_gateway_name(self,broker_name=None):
        if broker_name and broker_name in self.all_broker_setting:
            return broker_name
        if not broker_name and len(self.all_broker_setting)==1:
            return list(self.all_broker_setting.keys())[0]

        return ErrorResponse(message=f"You have multiple brokers; the value of `broker_name` is selected from `{list(self.all_broker_setting.keys())}`. If you are an AI and haven't specified `broker_name`, please consult the user. Do not make this decision yourself.")

    def send_order(self, *args,**kwargs):
        params=SendOrderParams(**kwargs)
        obj=BrokerRpcDataResponse(self)
        obj.send_order(params)
        return obj.get_result()
    def subscribe(self, *args, broker_name=None,**kwargs):
        gateway_name=self.__get_gateway_name(broker_name)
        if isinstance(gateway_name,ErrorResponse):
            return gateway_name.model_dump_json()
        req: SubscribeRequest=SubscribeRequest.from_model_data(**kwargs)
        result=self.main_engine.subscribe(req,gateway_name)
        return UnifiedResponse(result=result).model_dump_json()
    def cancel_order(self, *args, full_symbol_or_broker_symbol=None,order_id=None,broker_name=None,**kwargs):

        obj=BrokerRpcDataResponse(self)
        obj.cancel_order(full_symbol_or_broker_symbol=full_symbol_or_broker_symbol,order_id=order_id,broker_name=broker_name)
        return obj.get_result()
    def send_quote(self, *args, broker_name=None,**kwargs):
        gateway_name=self.__get_gateway_name(broker_name)
        if isinstance(gateway_name,ErrorResponse):
            return gateway_name.model_dump_json()
        req: OrderRequest = OrderRequest.from_model_data(**kwargs)
        result=self.main_engine.send_order(req,gateway_name)
        return UnifiedResponse(result=result).model_dump_json()
    def cancel_quote(self, *args, broker_name=None,**kwargs):
        gateway_name=self.__get_gateway_name(broker_name)
        if isinstance(gateway_name,ErrorResponse):
            return gateway_name.model_dump_json()

        req: CancelRequest = CancelRequest.from_model_data(**kwargs)
        result=self.main_engine.cancel_quote(req,gateway_name)
        return UnifiedResponse(result=result).model_dump_json()




    def get_tick(self, *args, vt_symbol: str, **kwargs):
        return broker_data_to_json(self.main_engine.get_tick(vt_symbol))

    def get_order(self, *args, vt_orderid: str, **kwargs):
        return broker_data_to_json(self.main_engine.get_order(vt_orderid))

    def get_trade(self, *args, vt_tradeid: str, **kwargs):
        return broker_data_to_json(self.main_engine.get_trade(vt_tradeid))

    def get_position(self, *args, vt_positionid: str, **kwargs):
        return broker_data_to_json(self.main_engine.get_position(vt_positionid))

    def get_account(self, *args,vt_accountid:str, **kwargs):


        return broker_data_to_json(self.main_engine.get_account(vt_accountid))

    def get_contract(self, *args, vt_symbol: str, **kwargs):
        return broker_data_to_json(self.main_engine.get_contract(vt_symbol))

    def get_quote(self, *args, vt_quoteid: str, **kwargs):
        return broker_data_to_json(self.main_engine.get_quote(vt_quoteid))


    def get_all_ticks(self, *args, broker_name=None,**kwargs):
        return broker_data_to_json(self.main_engine.get_all_ticks())

    def get_all_orders(self, *args,broker_name=None, **kwargs):
        return broker_data_to_json(self.main_engine.get_all_orders())

    def get_all_trades(self, *args,broker_name=None, **kwargs):
        return broker_data_to_json(self.main_engine.get_all_trades())

    def get_all_positions(self, *args,broker_name=None, **kwargs):
        obj = BrokerRpcDataResponse(self)
        obj.get_all_positions(broker_name=broker_name)
        return obj.get_result()

    def get_all_accounts(self, *args,broker_name=None, **kwargs):
        obj=BrokerRpcDataResponse(self)
        obj.get_all_accounts(broker_name=broker_name)
        return obj.get_result()

    def get_all_contracts(self, *args,broker_name=None, **kwargs):
        return broker_data_to_json(self.main_engine.get_all_contracts())

    def get_all_quotes(self, *args,broker_name=None, **kwargs):
        return broker_data_to_json(self.main_engine.get_all_quotes())

    def get_all_active_orders(self, *args,broker_name=None, **kwargs):
        obj = BrokerRpcDataResponse(self)
        obj.get_all_active_orders(broker_name=broker_name)
        return obj.get_result()

    def get_all_active_quotes(self, *args,broker_name=None, **kwargs):
        return broker_data_to_json(self.main_engine.get_all_active_quotes())



    def close(self, *args, **kwargs):
        if self.main_engine:
            self.main_engine.close()
            self.main_engine=None

            self.all_broker_setting.clear()

        return UnifiedResponse(result=True).model_dump_json()
    def connect(self, *args,setting:dict,broker_name=None, **kwargs):


        if not setting:
            logger.error(f"please check config.toml  [broker.your-broker-name]")
            return ErrorResponse(message=f"please check config.toml  [broker.your-broker-name]").model_dump_json()

        #fix setting
        if not broker_name:
            broker_name=setting["provider"]


        if broker_name in self.all_broker_setting:
            return UnifiedResponse(result=f"You requested 'connect {broker_name}' before").model_dump_json()



        setting_ = TomlToBrokerSetting.get_setting(setting)
        gateway=BrokerGateway.get_gateway(setting)



        self.all_broker_setting[broker_name]=setting_
        self.init_main_engine()
        self.main_engine.add_gateway(gateway,broker_name)
        self.main_engine.connect(setting_, broker_name)



        return UnifiedResponse(result=True).model_dump_json()


    async def a_accept(self, function_name: str, *args, **kwargs):
        if function_name not in self.IDENTITY.fun.get_array():
            return ErrorResponse(
                message=F"Unknown request '{function_name}'"
                        F".[find all functions module file:aitrados_broker/trade_middleware_service/trade_middleware_rpc_service.py]").model_dump_json()

        try:
            fun=getattr(self,function_name)
            result=fun(*args, **kwargs)
            return result

        except Exception as e:
            traceback.print_exc()
            erro="ensure args/kwargs are valid. [find all functions module file:aitrados_broker/trade_middleware_service/trade_middleware_rpc_service.py]"

            return ErrorResponse(message=F"Error: {e}.\n{erro}").model_dump_json()

