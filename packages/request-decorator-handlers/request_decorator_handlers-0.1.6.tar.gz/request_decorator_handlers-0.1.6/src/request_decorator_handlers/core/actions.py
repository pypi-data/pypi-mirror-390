"""Common action naming helpers used across examples and loggers."""

from dataclasses import dataclass


class CaptchaActions:
    PREFIX = "CAPTCHA"

    def __init__(self, parent_prefix: str):
        self.SUB = parent_prefix.upper()

    @property
    def LOAD(self) -> str:
        return f"{self.SUB}.{self.PREFIX}.LOAD"

    @property
    def VERIFY(self) -> str:
        return f"{self.SUB}.{self.PREFIX}.VERIFY"

    @property
    def SOLVE(self) -> str:
        return f"{self.SUB}.{self.PREFIX}.SOLVE"

    @property
    def FAIL(self) -> str:
        return f"{self.SUB}.{self.PREFIX}.FAIL"


class ActionBase:
    PREFIX = ""

    @classmethod
    def custom(cls, action: str) -> str:
        return f"{cls.PREFIX}.{action.upper()}"


class ParseGroup:
    def __init__(self, prefix: str):
        self.prefix = prefix.upper()

    def __call__(self, sub_action: str) -> str:
        return f"{self.prefix}.{sub_action.upper()}"

    def custom(self, value: str) -> str:
        return self(value)


@dataclass(frozen=True)
class ParseTrains(ParseGroup):
    def __init__(self):
        super().__init__("PARSE.TICKETS.TRAINS")

    CITY: str = "PARSE.TICKETS.TRAINS.CITY"
    DATE: str = "PARSE.TICKETS.TRAINS.DATE"
    TRAIN: str = "PARSE.TICKETS.TRAINS.TRAIN"
    SEAT: str = "PARSE.TICKETS.TRAINS.SEAT"
    WAGON: str = "PARSE.TICKETS.TRAINS.WAGON"


@dataclass(frozen=True)
class ParsePlanes(ParseGroup):
    def __init__(self):
        super().__init__("PARSE.TICKETS.PLANES")

    CITY: str = "PARSE.TICKETS.PLANES.CITY"
    DATE: str = "PARSE.TICKETS.PLANES.DATE"
    FLIGHT: str = "PARSE.TICKETS.PLANES.FLIGHT"
    SEAT: str = "PARSE.TICKETS.PLANES.SEAT"
    CLASS: str = "PARSE.TICKETS.PLANES.CLASS"


@dataclass(frozen=True)
class ParseHotels(ParseGroup):
    def __init__(self):
        super().__init__("PARSE.TICKETS.HOTELS")

    CITY: str = "PARSE.TICKETS.HOTELS.CITY"
    DATE: str = "PARSE.TICKETS.HOTELS.DATE"
    ROOM: str = "PARSE.TICKETS.HOTELS.ROOM"
    PRICE: str = "PARSE.TICKETS.HOTELS.PRICE"


@dataclass(frozen=True)
class ActionREG(ActionBase):
    PREFIX = "REG"
    REGISTER: str = f"{PREFIX}.REGISTER"
    EMAIL_CONFIRM: str = f"{PREFIX}.EMAIL.CONFIRM"
    RECOVER: str = f"{PREFIX}.RECOVER"
    CAPTCHA: CaptchaActions = CaptchaActions(PREFIX)


@dataclass(frozen=True)
class ActionAUTH(ActionBase):
    PREFIX = "AUTH"
    LOGIN: str = f"{PREFIX}.LOGIN"
    REFRESH: str = f"{PREFIX}.REFRESH"
    EMAIL_CONFIRM: str = f"{PREFIX}.EMAIL.CONFIRM"
    LOGOUT: str = f"{PREFIX}.LOGOUT"
    VERIFY: str = f"{PREFIX}.VERIFY"
    CAPTCHA: CaptchaActions = CaptchaActions(PREFIX)


@dataclass(frozen=True)
class ActionFETCH(ActionBase):
    PREFIX = "FETCH"
    COOKIES: str = f"{PREFIX}.COOKIES"
    PROFILE: str = f"{PREFIX}.PROFILE"
    BALANCE: str = f"{PREFIX}.BALANCE"
    CAPTCHA: CaptchaActions = CaptchaActions(PREFIX)


@dataclass(frozen=True)
class ActionPROFILE(ActionBase):
    PREFIX = "PROFILE"
    FILL: str = f"{PREFIX}.FILL"
    GET: str = f"{PREFIX}.GET"


@dataclass(frozen=True)
class ActionSEND(ActionBase):
    PREFIX = "SEND"
    DATA: str = f"{PREFIX}.DATA"
    FORM: str = f"{PREFIX}.FORM"


@dataclass(frozen=True)
class ActionLOGIC(ActionBase):
    PREFIX = "LOGIC"
    BOOKING: str = f"{PREFIX}.BOOKING"
    PAYMENT: str = f"{PREFIX}.PAYMENT"
    NOTIFY: str = f"{PREFIX}.NOTIFICATION"
    SEARCH: str = f"{PREFIX}.SEARCH"


class SOCIAL:
    PREFIX = "SOCIAL"

    def __init__(self, parent_prefix: str):
        self.SUB = parent_prefix.upper()

    def __getattr__(self, item: str) -> str:
        return f"{self.SUB}.{self.PREFIX}.{item.upper()}"


class TRAINS:
    PREFIX = "TRAINS"

    def __init__(self, parent_prefix: str):
        self.SUB = parent_prefix.upper()

    @property
    def DATA(self) -> str:
        return f"{self.SUB}.{self.PREFIX}.DATA"

    @property
    def VAGON(self) -> str:
        return f"{self.SUB}.{self.PREFIX}.ВАГОН"

    @property
    def COUPE(self) -> str:
        return f"{self.SUB}.{self.PREFIX}.КУПЕ"

    @property
    def MESTO(self) -> str:
        return f"{self.SUB}.{self.PREFIX}.МЕСТО"


class AIRPLANE:
    PREFIX = "AIRPLANE"

    def __init__(self, parent_prefix: str):
        self.SUB = parent_prefix.upper()

    @property
    def DATA(self) -> str:
        return f"{self.SUB}.{self.PREFIX}.DATA"

    @property
    def CITY(self) -> str:
        return f"{self.SUB}.{self.PREFIX}.CITY"

    @property
    def MESTO(self) -> str:
        return f"{self.SUB}.{self.PREFIX}.МЕСТО"

    @property
    def COMPANY(self) -> str:
        return f"{self.SUB}.{self.PREFIX}.COMPANY"

    @property
    def CLASS_TYPE(self) -> str:
        return f"{self.SUB}.{self.PREFIX}.CLASS"

    @property
    def PRICE(self) -> str:
        return f"{self.SUB}.{self.PREFIX}.PRICE"

    @property
    def AIRPORT(self) -> str:
        return f"{self.SUB}.{self.PREFIX}.AIRPORT"


@dataclass(frozen=True)
class ActionPARSE(ActionBase):
    PREFIX = "PARSE"

    SOCIAL: SOCIAL = SOCIAL(PREFIX)
    TRAINS: TRAINS = TRAINS(PREFIX)
    AIRPLANE: AIRPLANE = AIRPLANE(PREFIX)


@dataclass(frozen=True)
class LOG_ACTION:
    REG: ActionREG = ActionREG()
    AUTH: ActionAUTH = ActionAUTH()
    PROFILE: ActionPROFILE = ActionPROFILE()
    PARSE: ActionPARSE = ActionPARSE()
    SEND: ActionSEND = ActionSEND()
    FETCH: ActionFETCH = ActionFETCH()
    LOGIC: ActionLOGIC = ActionLOGIC()


__all__ = [
    "CaptchaActions",
    "ActionBase",
    "ActionREG",
    "ActionAUTH",
    "ActionFETCH",
    "ActionPROFILE",
    "ActionPARSE",
    "ActionSEND",
    "ActionLOGIC",
    "LOG_ACTION",
    "ParseGroup",
    "ParseTrains",
    "ParsePlanes",
    "ParseHotels",
    "SOCIAL",
    "TRAINS",
    "AIRPLANE",
]
