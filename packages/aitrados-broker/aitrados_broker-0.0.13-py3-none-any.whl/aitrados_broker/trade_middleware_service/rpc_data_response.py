from typing import TYPE_CHECKING, Dict, List
from aitrados_api.common_lib.response_format import UnifiedResponse, ErrorResponse
from aitrados_broker.utils.common_utils import broker_data_to_dict

if TYPE_CHECKING:
    from aitrados_broker.trade_middleware_service.trade_middleware_rpc_service import AitradosBrokerBackendService


class BrokerRpcDataResponse:
    common_msg = "If you are an AI, please inform the user. Do not act on your own."

    def __init__(self, backend_service: "AitradosBrokerBackendService"):
        self.bs = backend_service
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
