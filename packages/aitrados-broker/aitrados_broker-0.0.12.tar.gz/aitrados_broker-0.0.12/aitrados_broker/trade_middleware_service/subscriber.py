
from abc import ABC
from aitrados_api.trade_middleware.library.subscriber_mixin import AsyncSubscriberMixin
class AsyncBrokerSubscriber(AsyncSubscriberMixin,ABC):
    def __init__(self):
        super().__init__()

    async def on_broker_tick(self, msg):
        """
         implement the method in your class
        """
        #raise NotImplementedError("method not implemented")


    async def on_broker_trade(self, msg):
        """
         implement the method in your class
        """
        #raise NotImplementedError("method not implemented")


    async def on_broker_order(self, msg):
        """
         implement the method in your class
        """
        #raise NotImplementedError("method not implemented")


    async def on_broker_position(self, msg):
        """
         implement the method in your class
        """
        #raise NotImplementedError("method not implemented")


    async def on_broker_account(self, msg):
        """
         implement the method in your class
        """
        #raise NotImplementedError("method not implemented")


    async def on_broker_quote(self, msg):
        """
         implement the method in your class
        """
        # raise NotImplementedError("method not implemented")


    async def on_broker_contract(self, msg):
        """
         implement the method in your class
        """
        # raise NotImplementedError("method not implemented")
