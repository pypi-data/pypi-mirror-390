import re

from vnpy.trader.constant import Exchange
from vnpy.trader.object import ContractData


class FullSymbolGenerator:
    @classmethod
    def crypto(cls, broker_original_symbol:str, provider=None)->str|None:
        full_symbol = "CRYPTO:GLOBAL:"
        arr = str.split(broker_original_symbol, "_")
        symbol = arr[0]
        symbol = symbol.replace("-", "")
        symbol = symbol.upper()
        #USDT,USDC replace USD
        if symbol.endswith("USDT") or symbol.endswith("USDC"):
            symbol = symbol[:-4] + "USD"
        return full_symbol+symbol

    @classmethod
    def ctp(cls, contract:ContractData)->str|None:
        symbol = contract.symbol.replace("-", "")
        symbol = symbol.replace("_", "")
        symbol = symbol.upper()
        #

        if contract.option_underlying:

            full_symbol = "OPTION:CN:"
        else:
            full_symbol = "FUTURE:CN:"

        if contract.exchange == Exchange.CZCE:
            symbol = cls._fix_czce_code(symbol)

        return full_symbol+symbol

    @classmethod
    def _fix_czce_code(cls, symbol: str) -> str:
        """
        Fix missing year digits in CZCE contract codes

        Rules:
        - AP601 -> AP2601 (January 2026)
        - TA601C4350 -> TA2601C4350 (January 2026 call option)

        CZCE contract encoding rule: commodity code + year/month + option info
        When there are only 3 digits, usually missing the tens digit of year, default add 2
        """
        # Match pattern: letters + 3 digits + optional option part
        match = re.match(r'^([A-Z]+)(\d{3})(.*)', symbol)
        if not match:
            return symbol

        commodity_code = match.group(1)  # Commodity code: AP, TA, etc.
        three_digits = match.group(2)  # 3 digits: 601
        option_part = match.group(3)  # Option part: C4350 or empty

        # Check if correction is needed (first digit > 2 indicates possible missing year tens digit)
        first_digit = int(three_digits[0])

        if first_digit >= 3:  # 6 in 601 indicates year 26, missing tens digit 2
            # Add 2 before the 3 digits
            fixed_code = commodity_code + "2" + three_digits + option_part
        else:
            # Digits are reasonable, no correction needed
            fixed_code = symbol

        return fixed_code
