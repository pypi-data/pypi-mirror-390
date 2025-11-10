
from aitrados_api.trade_middleware.identity_mixin import *
class RpcFunction(RpcFunctionMixin):

    # broker related functions
    SUBSCRIBE = "subscribe"
    SEND_ORDER = "send_order"
    CANCEL_ORDER = "cancel_order"
    SEND_QUOTE = "send_quote"
    CANCEL_QUOTE = "cancel_quote"
    CLOSE = "close"
    CONNECT = "connect"
    #get functions
    GET_TICK = "get_tick"
    GET_ORDER = "get_order"
    GET_TRADE = "get_trade"
    GET_POSITION = "get_position"
    GET_ACCOUNT = "get_account"
    GET_CONTRACT = "get_contract"
    GET_QUOTE = "get_quote"
    GET_ALL_TICKS = "get_all_ticks"
    GET_ALL_ORDERS = "get_all_orders"
    GET_ALL_TRADES = "get_all_trades"
    GET_ALL_POSITIONS = "get_all_positions"
    GET_ALL_ACCOUNTS = "get_all_accounts"
    GET_ALL_CONTRACTS = "get_all_contracts"
    GET_ALL_QUOTES = "get_all_quotes"
    GET_ALL_ACTIVE_ORDERS = "get_all_active_orders"
    GET_ALL_ACTIVE_QUOTES = "get_all_active_quotes"









class Channel(ChannelMixin):
    # from broker data
    TICK = b"on_broker_tick"
    TRADE = b"on_broker_trade"
    ORDER = b"on_broker_order"
    POSITION = b"on_broker_position"
    ACCOUNT = b"on_broker_account"
    QUOTE = b"on_broker_quote"
    CONTRACT = b"on_broker_contract"







class Identity(IdentityMixin):
    backend_identity = "broker"
    fun = RpcFunction
    channel = Channel

broker_identity=Identity