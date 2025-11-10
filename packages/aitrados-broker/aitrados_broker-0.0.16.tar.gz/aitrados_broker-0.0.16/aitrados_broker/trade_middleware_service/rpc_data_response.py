import json
from dataclasses import asdict
from typing import TYPE_CHECKING, Dict, List
from aitrados_api.common_lib.response_format import UnifiedResponse, ErrorResponse

from aitrados_broker.addition_custom_mcps.parameter_validator.send_order_params import SendOrderParams
from aitrados_broker.utils.broker_aitrados_map import get_contract_dict
from aitrados_broker.utils.common_utils import broker_data_to_dict
from vnpy.trader.constant import Exchange, Direction, OrderType, Offset
from vnpy.trader.object import OrderRequest, CancelRequest

if TYPE_CHECKING:
    from aitrados_broker.trade_middleware_service.trade_middleware_rpc_service import AitradosBrokerBackendService


class BrokerRpcDataResponse:
    common_msg = "If you are an AI, please inform the user. Do not act on your own."

    def __init__(self, backend_service: "AitradosBrokerBackendService"):
        self.bs = backend_service
        self.real_gateway_name=None
        self.success = False
        self.result = None




    def get_result(self):
        if not self.success:
            return ErrorResponse(message=self.result).model_dump_json()

        return UnifiedResponse(result=self.result).model_dump_json()



    def _get_common_list_result(self, broker_data_list):
        data_list = broker_data_to_dict(broker_data_list)
        data_dict: Dict[str, List] = {}
        for item in data_list:
            gateway_name = item["gateway_name"]
            if gateway_name in data_dict:
                data_dict[gateway_name].append(item)
            else:
                data_dict[gateway_name] = [item]
        return data_dict

    def _get_public_verify(self, broker_name=None, is_verify_broker_name=True):
        if not self.bs.main_engine:
            return f"Please log in to a trading account first. {self.common_msg}"
        if not self.bs.main_engine.get_all_accounts():
            return f"We have not detected any logged-in accounts; please check the trading account settings. {self.common_msg}"

        length = len(self.bs.all_broker_setting)
        if length == 0:
            return f"Please log in to a trading account first. {self.common_msg}"

        if is_verify_broker_name:

            if length > 1 and not broker_name:
                return f"You have multiple brokers; the value of `broker_name` is selected from `{list(self.bs.all_broker_setting.keys())}`"

            if broker_name and broker_name not in self.bs.all_broker_setting:
                return f"Please log in to the trading account '{broker_name}'. {self.common_msg}"

        if length==1:
            self.real_gateway_name=list(self.bs.all_broker_setting.keys())[0]
        else:
            self.real_gateway_name=broker_name


    def get_all_positions(self, broker_name=None):
        self.result = self._get_public_verify(broker_name)
        if self.result:
            return self.result
        data_dict = self._get_common_list_result(self.bs.main_engine.get_all_positions())
        self.success = True

        try:
            if broker_name:
                self.result = data_dict[broker_name]
                if not self.result:
                    self.result = "No positions found"
            else:
                self.result = list(data_dict.values())[0]
        except Exception:
            self.result = "No positions found"

    def get_all_active_orders(self, broker_name=None):
        self.result = self._get_public_verify(broker_name)
        if self.result:
            return self.result
        data_dict = self._get_common_list_result(self.bs.main_engine.get_all_active_orders())
        self.success = True

        try:
            if broker_name:
                self.result = data_dict[broker_name]
                if not self.result:
                    self.result = "No pending orders found"
            else:
                self.result = list(data_dict.values())[0]
        except Exception:
            self.result = "No pending orders found"

    def get_all_accounts(self, broker_name=None):
        self.result = self._get_public_verify(broker_name)
        if self.result:
            return self.result

        data_dict = self._get_common_list_result(self.bs.main_engine.get_all_accounts())
        self.success = True
        if broker_name:
            self.result = data_dict[broker_name]
        else:
            self.result = list(data_dict.values())[0]


    def _get_contract(self, full_symbol_or_broker_symbol,broker_name=None,):

        contract_dict=get_contract_dict(full_symbol_or_broker_symbol,gateway_name=broker_name)
        if not contract_dict:
            self.result= f"Contract not found. {broker_name}.{full_symbol_or_broker_symbol}"
            return
        contract_length=len(contract_dict)
        if contract_length>1:
            self.result=f"We found that {full_symbol_or_broker_symbol} contains multiple symbols! Please edit the 'full_symbol_or_broker_symbol', The value of `full_symbol_or_broker_symbol` is selected from `{list(contract_dict.keys())}`"
            return
        return list(contract_dict.values())[0]

    def send_order(self,params:SendOrderParams):



        self.result = self._get_public_verify(params.broker_name)
        if self.result:
            return self.result

        contract=self._get_contract(params.full_symbol_or_broker_symbol,params.broker_name)
        if not contract:
            return self.result
        self.success = True
        req = OrderRequest(
            symbol=contract["symbol"],
            exchange=Exchange(contract["exchange"]),
            direction=Direction(params.direction.value),
            type=OrderType(params.type.value),
            volume=params.volume,
            price=params.price,
            offset=Offset(params.offset.value),
            full_symbol=contract["full_symbol"],
        )
        self.result=self.bs.main_engine.send_order(req,self.real_gateway_name)
        #print("new order",asdict(req))
        return self.result
    def cancel_order(self,full_symbol_or_broker_symbol,order_id,broker_name):
        if not order_id and not full_symbol_or_broker_symbol:
            self.result="Please specify the order_id or the full_symbol_or_broker_symbol."
            return self.result

        self.result = self._get_public_verify(broker_name)
        if self.result:
            return self.result

        self.success = True
        active_orders=self.bs.main_engine.get_all_active_orders()
        if not active_orders:
            self.result=True
            return
        if order_id:
            for order in active_orders:
                if order.orderid==order_id:
                    req = CancelRequest(
                        symbol=order.symbol,
                        exchange=order.exchange,
                        orderid=order.orderid,
                        full_symbol=order.full_symbol,
                    )
                    self.bs.main_engine.cancel_order(req, order.gateway_name)
                    #print("cancel order",asdict(req))
            self.result = True
            return True

        contract_dict=get_contract_dict(full_symbol_or_broker_symbol,gateway_name=broker_name)
        if not contract_dict:
            self.result=True
            return


        all_full_symbol_or_broker_symbols=set()
        for symbol,contract in contract_dict.items():
            all_full_symbol_or_broker_symbols.add(contract["full_symbol"])
            all_full_symbol_or_broker_symbols.add(contract["symbol"])



        for order in active_orders:
            if self.real_gateway_name!=order.gateway_name:
                continue

            if order.symbol not  in all_full_symbol_or_broker_symbols:
                continue
            req = CancelRequest(
                symbol=order.symbol,
                exchange=order.exchange,
                orderid=order.orderid,
                full_symbol=order.full_symbol,
            )

            self.bs.main_engine.cancel_order(req,self.real_gateway_name)

        self.result = True

