import multiprocessing
import threading
from time import sleep

from aitrados_api.common_lib.common import load_global_configs
from aitrados_api.common_lib.run_utils import ExecuteCallback
from aitrados_api.trade_middleware.response import AsyncBackendResponse
from loguru import logger
from aitrados_broker.trade_middleware_service.trade_middleware_identity import broker_identity
from aitrados_broker.trade_middleware_service.trade_middleware_rpc_service import AitradosBrokerBackendService
from aitrados_broker.utils.broker_aitrados_map import BrokerAsyncSubscriber
broker_process_ran=False

async def async_service_runner():
    global broker_process_ran
    service = AsyncBackendResponse(AitradosBrokerBackendService())
    logger.info("Start Broker service subprocess...")
    broker_process_ran=True
    await service.init()


def run_broker_child() -> None:
    global broker_process_ran
    load_global_configs(env_file=None, toml_file=None)
    threading.Thread()
    ExecuteCallback.run_background(async_service_runner)

    subscriber = BrokerAsyncSubscriber()
    subscriber.run()
    subscriber.subscribe_topics(broker_identity.channel.CONTRACT)

    try:
        while True:
            sleep(0.5)
    except KeyboardInterrupt:
        broker_process_ran=False
        return

def run_broker_process(is_thread=False) -> None:
    """
    Running in the parent process.
    """
    if broker_process_ran:
        logger.warning("Broker service subprocess ran before")
    def run():
        ctx = multiprocessing.get_context("spawn")
        child_process = ctx.Process(target=run_broker_child,daemon=True)
        child_process.start()

        try:
            child_process.join()
        except KeyboardInterrupt:
            child_process.terminate()
            child_process.join(timeout=5)

            if child_process.is_alive():
                child_process.kill()
                child_process.join()



    if is_thread:
        threading.Thread(target=run, daemon=True).start()
    else:
        run()
'''
if __name__ == "__main__":
    run_broker_process()
'''