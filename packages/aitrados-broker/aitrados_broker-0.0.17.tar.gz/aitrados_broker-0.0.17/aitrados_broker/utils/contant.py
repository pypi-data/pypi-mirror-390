class BrokerName:
    ib = "ib"
    coinbase = "coinbase"
    bitstamp = "bitstamp"
    okx = "okx"
    ctp = "ctp"
    mt5 = "mt5"
    da = "da"
    xtp = "xtp"
    binance_spot = "binance_spot"
    binance_linear = "binance_linear"
    binance_inverse = "binance_inverse"
    @classmethod
    def get_array(cls):
        return [v for k, v in cls.__dict__.items() if not k.startswith('_') and isinstance(v, str)]


    @classmethod
    def get_broker_modules(cls):
        data={}
        for broker in cls.get_array():
            if broker.startswith("binance_"):
                data[broker] = f"vnpy_binance"
            else:
                data[broker]=f"vnpy_{broker}"
        return data

    @classmethod
    def get_broker_package_names(cls):
        data={}
        for broker in cls.get_array():
            if broker in [cls.ctp,cls.xtp]:
                data[broker] = f"aitrados-{broker}"
            elif broker.startswith("binance_"):
                data[broker] = f"vnpy_binance"
            else:
                data[broker]=f"vnpy_{broker}"
        return data