from aitrados_api.universal_interface.trade_middleware_instance import AitradosTradeMiddlewareInstance
from aitrados_broker.run import run_broker_process

if __name__ == "__main__":
    AitradosTradeMiddlewareInstance.run_all()
    run_broker_process(is_thread=False)
