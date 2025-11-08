import uuid

from ephemerista.assets import _asset_id


def test_asset_id(lunar_scenario):
    expected = uuid.UUID("029b5285-d678-579c-a338-4e1de06ffb5b")
    asset = lunar_scenario["CEBR"]
    assert _asset_id(asset) == expected
    assert _asset_id(asset.asset_id) == expected
