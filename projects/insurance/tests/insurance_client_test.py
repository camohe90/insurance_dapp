import algokit_utils
import algosdk
import pytest
from algokit_utils.beta.account_manager import AddressAndSigner
from algokit_utils.beta.algorand_client import (
    AlgorandClient,
    AssetCreateParams,
    AssetOptInParams,
    AssetTransferParams,
    PayParams,
)

from smart_contracts.artifacts.insurance.insurance_client import InsuranceClient


@pytest.fixture(scope="session")
def algorand() -> AlgorandClient:
    """Generate a client to interact with the app"""
    return AlgorandClient.default_local_net()


@pytest.fixture(scope="session")
def dispenser(algorand: AlgorandClient) -> AddressAndSigner:
    return algorand.account.dispenser()


@pytest.fixture(scope="session")
def creator(algorand: AlgorandClient, dispenser: AddressAndSigner) -> AddressAndSigner:
    acct = algorand.account.random()

    algorand.send.payment(
        PayParams(sender=dispenser.address, receiver=acct.address, amount=10_000_000)
    )

    return acct

@pytest.fixture(scope="session")
def insurance_client(
    algorand: AlgorandClient,
    creator: AddressAndSigner
) -> InsuranceClient:
    client = InsuranceClient(
        algod_client=algorand.client.algod,
        sender=creator.address,
        signer=creator.signer,
    )

    client.create_create()

    return client

def test_register_asset(
    insurance_client: InsuranceClient
):

    result = insurance_client.register_asset(
        asset_name="Car",
        asset_value= 1000,
        asset_type= "CAR",
        asset_description="Car 2024"
    )

    assert result.confirmed_round

def test_review_request(
    insurance_client: InsuranceClient,
    algorand: AlgorandClient,
    creator: AddressAndSigner,
):

    algorand.send.payment(
            PayParams(
                    sender = creator.address,
                    receiver= insurance_client.app_address,
                    amount=200_000,
                )
        )

    sp = algorand.client.algod.suggested_params()
    sp.fee = 1_000

    result = insurance_client.review_request(
        acceptance="approved", analyst_comments="good car",
        transaction_parameters=algokit_utils.TransactionParameters(
                sender=creator.address,
                signer=creator.signer,
                suggested_params=sp
            ),
        )

    assert result.confirmed_round

    asset_id = insurance_client.get_asset_id().return_value
    result = algorand.account.get_information(insurance_client.app_address)

    assert result["assets"][0]["amount"] == 1
    assert asset_id ==  result["assets"][0]["asset-id"]




