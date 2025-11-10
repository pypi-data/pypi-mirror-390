
from pydantic import BaseModel, Field
from enum import Enum


class OrderTypeEnum(Enum):
    """Order type enumeration"""
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"


class OffsetEnum(Enum):
    """Position offset type enumeration"""
    OPEN = "OPEN"
    CLOSE = "CLOSE"


class DirectionEnum(Enum):
    """Trading direction enumeration"""
    LONG = "LONG"
    SHORT = "SHORT"


class SendOrderParams(BaseModel):
    """Order submission parameter model"""
    full_symbol_or_broker_symbol: str = Field(description="The full symbol or broker symbol of the financial instrument to be traded")
    type: OrderTypeEnum = Field(description="Order type: LIMIT (limit order), MARKET (market order), STOP (stop order)")
    volume: float = Field(gt=0, description="Order volume/quantity, must be greater than 0")
    price: float = Field(ge=0, description="Order price. For limit orders this is the limit price, for market orders this can be 0. Must be non-negative")
    offset: OffsetEnum = Field(description="Position offset flag: OPEN (open position), CLOSE (close position)")
    direction: DirectionEnum = Field(description="Trading direction: LONG (buy/long position), SHORT (sell/short position)")
    broker_name: str | None = Field(None, description="The broker name,Unless otherwise requested by the user, the default value shall be retained.")