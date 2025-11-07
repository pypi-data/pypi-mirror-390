import asyncio
from collections import defaultdict
from typing import Dict

from aitrados_broker.trade_middleware_service.subscriber import AsyncBrokerSubscriber

broker_full_symbol_contracts:Dict[str,Dict[str,dict]] = defaultdict(dict)


class BrokerAsyncSubscriber(AsyncBrokerSubscriber):
    """
    Asynchronous function callback
    """
    def __init__(self):
        self._alock=asyncio.Lock()
        super().__init__()

    async def on_broker_contract(self, msg):
        async with self._alock:

            # on_broker_contract will receive many data.so you need to remove the '#' below for watching data
            contract=msg["result"]
            full_symbol=contract["full_symbol"]
            if not full_symbol:
                return None
            gateway_name=contract["gateway_name"]

            broker_full_symbol_contracts[gateway_name][full_symbol] = contract
            #print(contract["full_symbol"] ,len(broker_full_symbol_contracts[contract["gateway_name"]]))

        pass

