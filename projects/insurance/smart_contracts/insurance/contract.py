from algopy import ARC4Contract, String, UInt64,Account, Txn, itxn, arc4
from algopy.arc4 import abimethod


class Insurance(ARC4Contract):

    def __init__(self) -> None:

        self.analyst = Account()
        self.customer = Account()
        self.asset_name = String()
        self.asset_value = UInt64(0)
        self.asset_type = String()
        self.asset_description = String()
        self.asset_status = String()
        self.analyst_comments = String()
        self.asset_id = UInt64(0)

    @abimethod(allow_actions=["NoOp"], create="require")
    def create(self) -> None:
        self.analyst = Txn.sender
        self.asset_status = String("None")

    @abimethod()
    def register_asset(
        self,
        asset_name: String,
        asset_value: UInt64,
        asset_type: String,
        asset_description: String
    ) -> None:
        assert Txn.sender != self.analyst
        self.asset_name = asset_name
        self.asset_value = asset_value
        self.asset_type = asset_type
        self.asset_description = asset_description
        self.asset_status = String("requested")

    @abimethod()
    def review_request(
        self,
        acceptance: String,
        analyst_comments : String
    )-> None:

        assert Txn.sender == self.analyst
        assert not self.asset_status == String("accepted")
        assert not self.asset_status == String("insured")
        self.analyst_comments = analyst_comments

        if acceptance == String("approved"):
            self.asset_status = String("accepted")
            self.asset_id  = itxn.AssetConfig (
            asset_name= "Insurance",
            unit_name= "INS",
            total= 1,
            decimals= 0,
            fee=0,
            default_frozen= False,
            note= "Token for the asset"
        ).submit().created_asset.id
        else:
            self.asset_status = String("rejected")


    @abimethod
    def get_asset_id(self)-> UInt64:
        return self.asset_id

