import asyncio
import traceback
from collections import defaultdict
from typing import Dict

from aitrados_broker.trade_middleware_service.subscriber import AsyncBrokerSubscriber
#gateway_name.full_symbol.symbol
broker_full_symbol_contracts: Dict[str, Dict[str, Dict[str, dict]]] = defaultdict(lambda: defaultdict(dict))
broker_symbol_contracts:Dict[str, Dict[str, dict]]=defaultdict(dict)


def get_contract_dict(full_symbol_or_broker_symbol:str,gateway_name:str=None):
    broker_count=len(broker_full_symbol_contracts)
    if not broker_count:
        return None
    try:
        if broker_count==1:
            gateway_name=list(broker_full_symbol_contracts.keys())[0]

        if ":" in full_symbol_or_broker_symbol:
            contracts=broker_full_symbol_contracts[gateway_name][full_symbol_or_broker_symbol]
        else:
            contract=broker_symbol_contracts[gateway_name][full_symbol_or_broker_symbol]
            contracts={full_symbol_or_broker_symbol:contract}
        return contracts
    except Exception:
        #traceback.format_exc()
        return None







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

            gateway_name = contract["gateway_name"]
            symbol = contract["symbol"]



            full_symbol = contract["full_symbol"]

            #print(full_symbol,"  ",symbol)

            if not full_symbol:
                return None
            broker_symbol = contract["broker_symbol"]
            broker_symbol_contracts[gateway_name][broker_symbol] = contract
            #print(full_symbol,"===", broker_symbol)
            broker_full_symbol_contracts[gateway_name][full_symbol][symbol] = contract

            #print(full_symbol,contract["name"],contract["broker_symbol"])
            return None
            if len(broker_full_symbol_contracts[gateway_name][full_symbol])>0:
                a=broker_full_symbol_contracts[gateway_name][full_symbol]
                #print(full_symbol)





        pass

