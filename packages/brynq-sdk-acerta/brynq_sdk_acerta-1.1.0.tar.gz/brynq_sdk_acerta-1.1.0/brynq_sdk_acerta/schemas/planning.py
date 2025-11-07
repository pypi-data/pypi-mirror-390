"""
Schemas for Planning resource
"""

import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel


# GET Schema for Countries
class CountryGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v1/countries endpoint"""

    description: Series[pd.StringDtype] = pa.Field(coerce=True, description="Country name", alias="description")
    nis_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="NISCode of the country", alias="NISCode")

    class _Annotation:
        primary_key = "nis_code"

    class Config:
        metadata = {"class": "Country", "dependencies": []}


# GET Schema for Belgian Cities
class BelgianCityGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v1/belgian-cities endpoint"""

    postal_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Belgian city postal code", alias="postalCode")
    name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Belgian city name", alias="name")
    nis_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Belgian city NIS code", alias="NISCode")

    class _Annotation:
        primary_key = "nis_code"

    class Config:
        metadata = {"class": "BelgianCity", "dependencies": []}
