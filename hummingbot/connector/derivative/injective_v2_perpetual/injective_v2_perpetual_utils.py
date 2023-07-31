from decimal import Decimal
from typing import Dict, Union

from pydantic import Field
from pydantic.class_validators import validator

from hummingbot.client.config.config_data_types import BaseConnectorConfigMap, ClientFieldData
from hummingbot.connector.exchange.injective_v2.injective_v2_utils import (
    ACCOUNT_MODES,
    NETWORK_MODES,
    InjectiveDelegatedAccountMode,
    InjectiveMainnetNetworkMode,
)
from hummingbot.core.data_type.trade_fee import TradeFeeSchema

CENTRALIZED = False
EXAMPLE_PAIR = "INJ-USDT"

DEFAULT_FEES = TradeFeeSchema(
    maker_percent_fee_decimal=Decimal("0"),
    taker_percent_fee_decimal=Decimal("0"),
)


class InjectiveConfigMap(BaseConnectorConfigMap):
    connector: str = Field(default="injective_v2_perpetual", const=True, client_data=None)
    receive_connector_configuration: bool = Field(
        default=True, const=True,
        client_data=ClientFieldData(),
    )
    network: Union[tuple(NETWORK_MODES.values())] = Field(
        default=InjectiveMainnetNetworkMode(),
        client_data=ClientFieldData(
            prompt=lambda cm: f"Select the network ({'/'.join(list(NETWORK_MODES.keys()))})",
            prompt_on_new=True,
        ),
    )
    account_type: Union[tuple(ACCOUNT_MODES.values())] = Field(
        default=InjectiveDelegatedAccountMode(
            private_key="0000000000000000000000000000000000000000000000000000000000000000",  # noqa: mock
            subaccount_index=0,
            granter_address="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # noqa: mock
            granter_subaccount_index=0,
        ),
        client_data=ClientFieldData(
            prompt=lambda cm: f"Select the type of account configuration ({'/'.join(list(ACCOUNT_MODES.keys()))})",
            prompt_on_new=True,
        ),
    )

    class Config:
        title = "injective_v2_perpetual"

    @validator("network", pre=True)
    def validate_network(cls, v: Union[(str, Dict) + tuple(NETWORK_MODES.values())]):
        if isinstance(v, tuple(NETWORK_MODES.values()) + (Dict,)):
            sub_model = v
        elif v not in NETWORK_MODES:
            raise ValueError(
                f"Invalid network, please choose a value from {list(NETWORK_MODES.keys())}."
            )
        else:
            sub_model = NETWORK_MODES[v].construct()
        return sub_model

    @validator("account_type", pre=True)
    def validate_account_type(cls, v: Union[(str, Dict) + tuple(ACCOUNT_MODES.values())]):
        if isinstance(v, tuple(ACCOUNT_MODES.values()) + (Dict,)):
            sub_model = v
        elif v not in ACCOUNT_MODES:
            raise ValueError(
                f"Invalid account type, please choose a value from {list(ACCOUNT_MODES.keys())}."
            )
        else:
            sub_model = ACCOUNT_MODES[v].construct()
        return sub_model

    def create_data_source(self):
        return self.account_type.create_data_source(
            network=self.network.network(), use_secure_connection=self.network.use_secure_connection()
        )


KEYS = InjectiveConfigMap.construct()
