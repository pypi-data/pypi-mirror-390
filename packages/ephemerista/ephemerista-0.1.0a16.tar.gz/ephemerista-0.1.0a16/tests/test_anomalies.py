import numpy as np
from pydantic import Field
from pytest import approx

from ephemerista import BaseModel
from ephemerista.coords import anomalies


def test_deserialization():
    class Model(BaseModel):
        anomaly: anomalies.AnomalyType = Field(discriminator=anomalies.DISCRIMINATOR)

    json = r'{"anomaly": {"type": "true_anomaly", "degrees": 90}}'
    model = Model.model_validate_json(json)
    assert isinstance(model, Model)


def test_radians():
    true = anomalies.TrueAnomaly.from_radians(np.pi / 2)
    assert isinstance(true, anomalies.TrueAnomaly)
    assert true.true_anomaly(0.0) == approx(np.pi / 2)
