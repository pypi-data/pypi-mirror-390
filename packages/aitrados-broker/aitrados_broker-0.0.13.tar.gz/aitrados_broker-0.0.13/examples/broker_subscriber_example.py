from aitrados_broker.trade_middleware_service.subscriber import AsyncBrokerSubscriber
from aitrados_broker.trade_middleware_service.trade_middleware_identity import broker_identity


def broker_subscriber_client_example():
    from aitrados_api.trade_middleware.subscriber import AsyncSubscriber
    #you can conbin AsyncSubscriber and AsyncBrokerSubscriber
    class MyAsyncSubscriber(AsyncBrokerSubscriber):
        """
        Asynchronous function callback
        """

        async def on_broker_tick(self, msg):
            print("on_broker_tick",msg["result"])

        async def on_broker_trade(self, msg):
            print("on_broker_trade", msg["result"])

        async def on_broker_order(self, msg):
            print("on_broker_order", msg["result"])

        async def on_broker_position(self, msg):
            print("on_broker_position", msg["result"])

        async def on_broker_account(self, msg):
            print("on_broker_account", msg["result"])

        async def on_broker_quote(self, msg):
            print("on_broker_quote", msg["result"])

        async def on_broker_contract(self, msg):
            #on_broker_contract will receive many data.so you need to remove the '#' below for watching data
            #print("on_broker_contract", msg["result"])
            pass

    subscriber = MyAsyncSubscriber()
    subscriber.run()
    subscriber.subscribe_topics(*broker_identity.channel.get_array())