
import time
from aitrados_api.common_lib.common import load_global_configs
from aitrados_api.common_lib.tools.toml_manager import TomlManager

from aitrados_broker.trade_middleware_service.requests import broker_request
from aitrados_broker.trade_middleware_service.trade_middleware_rpc_service import AitradosBrokerBackendService
from examples.broker_subscriber_example import broker_subscriber_client_example

load_global_configs(env_file =None, toml_file=None)
if __name__ == "__main__":


    broker_subscriber_client_example()
    broker_setting = TomlManager.get_value("broker.binance_spot_demo")
    fun_cls=AitradosBrokerBackendService.IDENTITY.fun

    print("CONNECT",broker_request(fun_cls.CONNECT,setting =broker_setting))
    time.sleep(10)
    print("GET_ALL_POSITIONS",broker_request(fun_cls.GET_ALL_POSITIONS))
    print("GET_ALL_ACCOUNTS",broker_request(fun_cls.GET_ALL_ACCOUNTS))

    #broker_request(fun_cls.CLOSE)

    exit()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("closing...")
