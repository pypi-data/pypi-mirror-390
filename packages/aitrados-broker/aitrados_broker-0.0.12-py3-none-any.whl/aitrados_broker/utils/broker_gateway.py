import importlib
import subprocess
import sys
import traceback

from aitrados_broker.utils.contant import BrokerName


from vnpy.trader.gateway import BaseGateway


class BrokerGateway:

    @classmethod
    def _ensure_module_installed(cls, provider:str,module_name: str) -> bool:
        """
        Ensure the module is installed; if not, install it dynamically.
        """
        temp_module_name = module_name
        try:

            importlib.import_module(module_name)
            return True
        except ImportError:
            print(f"Module {provider} is not installed, attempting to install...")
            try:

                if provider=="ctp":
                    temp_module_name="aitrados_ctp"


                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", temp_module_name,"--upgrade"
                ])
                '''
                if provider=="ib":
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", "nautilus_ibapi", "--upgrade"
                    ])
                '''
                # 安装成功后，清除import缓存并重新导入
                if module_name in sys.modules:
                    del sys.modules[module_name]
                importlib.import_module(module_name)
                return True
            except (subprocess.CalledProcessError, ImportError) as e:
                print(f"Module {provider} is not installed, attempting to install...")
                print(f"Please install manually. pip install {temp_module_name}")
                traceback.print_exc()
                return False



    @classmethod
    def get_gateway(cls, toml_data: dict) -> type[BaseGateway]:
        if not toml_data or 'provider' not in toml_data:
            return None
        provider=toml_data['provider']
        if provider not in BrokerName.get_array():
            raise ValueError(f"unknown broker provider '{provider}'. only support {BrokerName.get_array()}")

        broker_modules=BrokerName.get_broker_modules()


        if not cls._ensure_module_installed(provider,broker_modules[provider]):
            raise ValueError(f"Unable to install or load module: {provider}."
                             f"Please install manually.")

        match toml_data['provider']:




            case BrokerName.okx:
                from vnpy_okx import OkxGateway
                return OkxGateway
            case BrokerName.ctp:
                from vnpy_ctp import CtpGateway
                return CtpGateway
            case BrokerName.ib:
                from vnpy_ib import IbGateway
                return IbGateway
            case BrokerName.binance:
                from vnpy_binance import BinanceSpotGateway
                return BinanceSpotGateway
            case _:
                raise ValueError("unknown broker provider")
