# python
class TomlToBrokerSetting:
    @classmethod
    def get_setting(cls, toml_data: dict) -> dict:
        if not toml_data or 'provider' not in toml_data:
            return {}
        method = getattr(cls, f"get_{toml_data['provider']}_setting", None)
        if method:
            return method(toml_data)
        return {}

    @classmethod
    def _get_bool_string(cls,value:bool|str|None):
        if value is None:
            return 'False'
        if isinstance(value, bool):
            return 'True' if value else 'False'
        if isinstance(value, str):
            if value.lower() in ['1', 'true', 'yes']:
                return 'True'
            else:
                return 'False'
        return 'False'

    @classmethod
    def get_okx_setting(cls, toml_data: dict):
        # [broker]
        #    provider = "okx"
        #    api_key = "xxx"
        #    secret_key = "xxx"
        #    passphrase = "xxx"
        #    server = "demo"
        #    proxy_host = "xxxx"
        #    proxy_port = xxx
        #    spread_trading = "false"
        setting = {
            "API Key": toml_data.get('api_key'),
            "Secret Key": toml_data.get('secret_key', ),
            "Passphrase": toml_data.get('passphrase', ),
            "Server": toml_data.get('server',"").upper(),
            "Proxy Host": toml_data.get('proxy_host', ""),
            "Proxy Port": int(toml_data.get('proxy_port')) if toml_data.get('proxy_port') is not None else 0,
            "Spread Trading": cls._get_bool_string(toml_data.get('spread_trading', 'False'))
        }

        return setting
    @classmethod
    def get_ctp_setting(cls, toml_data: dict):
        """
        [broker]
            provider = "ctp"
            username = "xxx"
            password = "xxxx"
            broker_id = "xxxx"
            trade_server = "xxxx"
            market_server = "xxxx"
            product_name = "xxxx"
            auth_code = "xxxx"
        """
        setting = {
            "用户名": toml_data.get('username',""),
            "密码": toml_data.get('password',"" ),
            "经纪商代码": toml_data.get('broker_id',""),
            "交易服务器": toml_data.get('trade_server',""),
            "行情服务器": toml_data.get('market_server',""),
            "产品名称":toml_data.get('product_name',""),
            "授权编码": toml_data.get('auth_code',""),
            "柜台环境":"实盘"
        }

        return setting

    # python
    @classmethod
    def get_ib_setting(cls, toml_data: dict):

        setting = {
            "TWS地址": toml_data.get('tws_host', "127.0.0.1"),
            "TWS端口": int(toml_data.get('tws_port')) if toml_data.get('port') is not None else 7497,
            "客户号": int(toml_data.get('client_id')) if toml_data.get('client_id') is not None else 1,
            "交易账户": toml_data.get('account', ""),
        }

        return setting

    @classmethod
    def __get_binance_setting(cls, toml_data: dict):
        setting = {
            "API Key": toml_data.get('api_key'),
            "API Secret": toml_data.get('secret_key', ),
            "Kline Stream": cls._get_bool_string(True),
            "Server": toml_data.get('server',"").upper(),
            "Proxy Host": toml_data.get('proxy_host', ""),
            "Proxy Port": int(toml_data.get('proxy_port')) if toml_data.get('proxy_port') is not None else 0,
        }
        return setting

    @classmethod
    def get_binance_inverse_setting(cls, toml_data: dict):
        return cls.__get_binance_setting(toml_data)
    @classmethod
    def get_binance_spot_setting(cls, toml_data: dict):
        return cls.__get_binance_setting(toml_data)
    @classmethod
    def get_binance_linear_setting(cls, toml_data: dict):
        return cls.__get_binance_setting(toml_data)



    @classmethod
    def get_xtp_setting(cls, toml_data: dict):

        trade_server=toml_data.get('trade_server',"")
        trade_host,trade_port=trade_server.split(":") if ":" in trade_server else (trade_server,"")
        market_server=toml_data.get('market_server',"")
        market_host,market_port=market_server.split(":") if ":" in market_server else (market_server,"")

        setting = {
            "账号": toml_data.get('username',""),
            "密码": toml_data.get('password',"" ),
            "客户号": toml_data.get('client_id',0),
            "授权码": toml_data.get('auth_code',""),
            "交易地址": trade_host,
            "交易端口": trade_port,
            "行情地址": market_host,
            "行情端口": market_port,
            "行情协议": "TCP",
            "日志级别": "INFO",

        }

        return setting