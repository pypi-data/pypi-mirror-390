# Interoperability

To enable interoperability with other tools and libraries and enable additional deployment scenarios such as web services or GUI applications, Ephemerista makes heavy use of [Pydantic].
This mean in practice that all Ephemerista data structures inherit from a Pydantic base model and can be serialized and deserialized to and from JSON or Python dictionaries.

Pydantic also parses and validates the provided data according to validation rules defined in the data model.
This ensures correctness of the interfaces and allows downstream applications to check their inputs via [JSON Schema].

As an example, an abriged version for Ephemerista's Keplerian state model is shown below.

```python
class Keplerian(TwoBody):
    state_type: Literal["keplerian"] = Field(default="keplerian", frozen=True, repr=False, alias="type")
    shape: shapes.Shape = Field(discriminator=shapes.DISCRIMINATOR)
    inc: Inclination = Field(alias="inclination")
    node: Angle = Field(alias="ascendingNode")
    arg: Angle = Field(alias="periapsisArgument")
    anomaly: TrueAnomaly | MeanAnomaly = Field(discriminator=anomalies.DISCRIMINATOR)
```

The corresponding abriged JSON Schema is shown in the following listing.

```json
{
   "title": "Keplerian",
   "type": "object",
   "properties": {
      "time": {
         "$ref": "#/$defs/Time",
         "description": "Epoch of the state vector"
      },
      "origin": {
         "default": {
            "type": "planet",
            "name": "Earth"
         },
         "description": "Origin of the coordinate system",
         "oneOf": [
            {
               "$ref": "#/$defs/Origin"
            }
         ],
         "title": "Origin"
      },
      "satelliteName": {
         "default": "MySatellite",
         "description": "Name of the Satellite",
         "title": "Satellitename",
         "type": "string"
      },
      "type": {
         "const": "keplerian",
         "default": "keplerian",
         "enum": [
            "keplerian"
         ],
         "title": "Type",
         "type": "string"
      },
      "shape": {
         "oneOf": [
            {
               "$ref": "#/$defs/Shape"
            }
         ],
         "title": "Shape"
      },
      "inclination": {
         "$ref": "#/$defs/Inclination"
      },
      "ascendingNode": {
         "$ref": "#/$defs/Angle"
      },
      "periapsisArgument": {
         "$ref": "#/$defs/Angle"
      },
      "anomaly": {
         "discriminator": {
            "mapping": {
               "mean_anomaly": "#/$defs/MeanAnomaly",
               "true_anomaly": "#/$defs/TrueAnomaly"
            },
            "propertyName": "type"
         },
         "oneOf": [
            {
               "$ref": "#/$defs/TrueAnomaly"
            },
            {
               "$ref": "#/$defs/MeanAnomaly"
            }
         ],
         "title": "Anomaly"
      }
   },
   ...
}
```

Finally a concrete example Keplerian state encoded as JSON could look like shown below.

```json
{
  "time": {
    "scale": "TDB",
    "timestamp": {
      "time_type": "iso",
      "value": "2024-01-22T12:50:00"
    }
  },
  "origin": {
    "body_type": "planet",
    "name": "Earth"
  },
  "state_type": "keplerian",
  "shape": {
    "shape_type": "semi_major",
    "sma": 24464560.0,
    "ecc": 0.7311
  },
  "inc": {
    "degrees": 6.997991918168848
  },
  "node": {
    "degrees": 57.68596377156641
  },
  "arg": {
    "degrees": 178.00996553801497
  },
  "anomaly": {
    "degrees": 25.4218877337829,
    "anomaly_type": "true_anomaly"
  }
}
```

The [backend] of the Ephemerista Web GUI is a practical example of how this functionality can be leveraged to quickly build Ephemerista-based applications and web services.

[Pydantic]: https://docs.pydantic.dev/latest/
[JSON Schema]: https://json-schema.org/
[backend]: https://gitlab.com/librespacefoundation/ephemerista/ephemerista-web/-/tree/main/backend?ref_type=heads
