class BrokerName:
    ib = "ib"
    coinbase = "coinbase"
    binance = "binance"
    bitstamp = "bitstamp"
    okx = "okx"
    ctp = "ctp"
    mt5 = "mt5"
    da = "da"
    emt = "emt"
    @classmethod
    def get_array(cls):
        return [v for k, v in cls.__dict__.items() if not k.startswith('_') and isinstance(v, str)]


    @classmethod
    def get_broker_modules(cls):
        data={}
        for broker in cls.get_array():
            data[broker]=f"vnpy_{broker}"
        return data


