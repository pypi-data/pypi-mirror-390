from time import sleep

from aitrados_api.common_lib.common import load_global_configs
from aitrados_api.common_lib.tools.toml_manager import TomlManager
from aitrados_api.universal_interface.trade_middleware_instance import AitradosTradeMiddlewareInstance

from aitrados_broker import broker_request
from aitrados_broker.run import run_broker_process
from aitrados_broker.trade_middleware_service.trade_middleware_rpc_service import AitradosBrokerBackendService
load_global_configs(env_file =None, toml_file=None)
if __name__ == "__main__":
    AitradosTradeMiddlewareInstance.run_all()
    run_broker_process(is_thread=True)
    sleep(3)
    fun_cls = AitradosBrokerBackendService.IDENTITY.fun
    #broker_setting = TomlManager.get_value("broker.binance_spot_demo")
    #broker_setting = TomlManager.get_value("broker.binance_inverse_demo")
    #broker_setting = TomlManager.get_value("broker.binance_linear_demo")

    #broker_setting = TomlManager.get_value("broker.simnow_24h")
    #broker_setting = TomlManager.get_value("broker.zhongtaizhengquan")
    #broker_setting = TomlManager.get_value("broker.okx_demo")
    broker_setting = TomlManager.get_value("broker.simnow_24h")


    try:
        print("CONNECT", broker_request(fun_cls.CONNECT, setting=broker_setting))
    except Exception as e:
        pass
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass
