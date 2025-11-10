"""Basic data types."""

from datetime import date
from enum import Enum
from typing import Any, NewType, TypedDict

from msgspec import Struct

from kaiju_models import BooleanField, DateField, EmailField, IntegerField, JsonMapField, Model, StringField

__all__ = ["CustomerId", "CardId", "CardType", "Card", "Customer", "CustomerUpdate", "CustomerCreate", "SearchFilter", "LoginCode", 'CARD_TYPE_PREFIX']

CustomerId = NewType("CustomerId", int)
CardId = NewType("CardId", str)


class LoginCode(Struct):
    value: str
    expires_after: int


class CardType(Enum):
    PHYSICAL = 'PHYSICAL'
    VIRTUAL = 'VIRTUAL'
    APPLE = 'APPLE'
    GOOGLE = 'GOOGLE'
    TEMP = 'TEMP'


CARD_TYPE_PREFIX = {
    CardType.TEMP: '0',
    CardType.VIRTUAL: '1',
    CardType.APPLE: '2',
    CardType.GOOGLE: '3',
    CardType.PHYSICAL: '441',  #: for phys cards it's used only for validation
}


class Card(Struct):
    created: date = DateField()
    customer_id: CustomerId = IntegerField()
    type: CardType = StringField()
    id: CardId = StringField()
    enabled: bool = BooleanField()


class SearchFilter(TypedDict):
    """UI search filter data."""

    id: str
    kind: str
    condition: str
    value: Any


class CustomerUpdate(Model["CustomerUpdate.Fields"]):
    """Data to update customer."""

    class Fields(Model.Fields):
        blocked: bool = BooleanField()
        email: str | None = EmailField()
        email_confirmed: bool = BooleanField()
        profile: dict[str, Any] = JsonMapField()  # profile data is dynamic and determined by settings
        meta: dict[str, Any] = JsonMapField()  # meta is dynamic and determined by settings
        subscriptions: dict[str, Any] = JsonMapField()  # subs data is dynamic and determined by settings
        loyalty_enabled: bool = BooleanField()
        prioritize_sms_verification: bool = BooleanField()


class CustomerCreate(Model["CustomerCreate.Fields"]):
    """Data to create a new customer."""

    class Fields(Model.Fields):
        phone: str = StringField(pattern="7[0-9]{10}", required=True)
        source_id: str | None = StringField()
        email: str | None = EmailField()
        email_confirmed: bool = BooleanField(default=False)
        profile: dict[str, Any] = JsonMapField()  # profile data is dynamic and determined by settings
        meta: dict[str, Any] = JsonMapField()  # meta is dynamic and determined by settings
        subscriptions: dict[str, Any] = JsonMapField()  # subs data is dynamic and determined by settings
        loyalty_enabled: bool = BooleanField(default=False)
        accept_tender_offer: bool = BooleanField(default=True)
        created: date = DateField()  # TODO: remove after loading the initial db
        prioritize_sms_verification: bool = BooleanField(default=False)


class Customer(Model["Customer.Fields"]):
    """Customer data"""

    class Fields(Model.Fields):
        id: CustomerId = IntegerField()
        phone: str = StringField()
        source_id: str | None = StringField()
        email: str | None = EmailField()
        email_confirmed: bool = BooleanField()
        blocked: bool = BooleanField()
        profile: dict[str, Any] = JsonMapField()  # profile data is dynamic and determined by settings
        meta: dict[str, Any] = JsonMapField()  # meta is dynamic and determined by settings
        subscriptions: dict[str, Any] = JsonMapField()  # subs data is dynamic and determined by settings
        loyalty_enabled: bool = BooleanField()
        created: date = DateField()
        accept_tender_offer: bool = BooleanField()
        prioritize_sms_verification: bool = BooleanField()
