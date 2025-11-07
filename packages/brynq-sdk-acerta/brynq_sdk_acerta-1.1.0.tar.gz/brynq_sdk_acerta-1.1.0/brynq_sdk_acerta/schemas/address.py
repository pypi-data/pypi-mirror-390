"""
Schema for GET /employee-data-management/v3/employees/{employeeId}/addresses
"""

import pandas as pd
import pandera as pa
from pandera.typing import Series
from typing import Optional
from pydantic import BaseModel, Field
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class AddressGet(BrynQPanderaDataFrameModel):
    """Schema for GET /employee-data-management/v3/employees/{employeeId}/addresses endpoint."""

    # Employee identification
    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee identifier", alias="employeeId")

    # Period information
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="Address period start date", alias="period.startDate")
    period_end_date: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Address period end date", alias="period.endDate")

    # Official address
    official_street: Series[pd.StringDtype] = pa.Field(coerce=True, description="Official address street", alias="officialAddress.street")
    official_house_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Official address house number", alias="officialAddress.houseNumber")
    official_post_box: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Official address post box", alias="officialAddress.postBox")
    official_postal_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Official address postal code", alias="officialAddress.postalCode")
    official_community: Series[pd.StringDtype] = pa.Field(coerce=True, description="Official address community", alias="officialAddress.community")
    official_country_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Official address country name", alias="officialAddress.country.name")
    official_country_nis_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Official address country NIS code", alias="officialAddress.country.NISCode")

    # Correspondence address (nullable)
    correspondence_street: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Correspondence address street", alias="correspondenceAddress.street")
    correspondence_house_number: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Correspondence address house number", alias="correspondenceAddress.houseNumber")
    correspondence_post_box: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Correspondence address post box", alias="correspondenceAddress.postBox")
    correspondence_postal_code: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Correspondence address postal code", alias="correspondenceAddress.postalCode")
    correspondence_community: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Correspondence address community", alias="correspondenceAddress.community")
    correspondence_country_name: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Correspondence address country name", alias="correspondenceAddress.country.name")
    correspondence_country_nis_code: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Correspondence address country NIS code", alias="correspondenceAddress.country.NISCode")

    class _Annotation:
        primary_key = "employee_id"
        foreign_keys = {}

    class Config:
        metadata = {"class": "Address", "dependencies": []}


# Pydantic schemas for PATCH address
# Uses json_schema_extra for prefix-based field mapping

class Address(BaseModel):
    """Reusable address schema (no prefix in field names)"""
    street: str = Field(..., min_length=1, max_length=40, example="Bondgenotenlaan", description="Street name", alias="street")
    house_number: str = Field(..., min_length=1, max_length=9, example="2", description="House number", alias="houseNumber")
    post_box: Optional[str] = Field(None, min_length=1, max_length=4, example="A", description="Box number", alias="postBox")
    postal_code: str = Field(..., min_length=1, max_length=14, example="3000", description="Postal code", alias="postalCode")
    community: str = Field(..., min_length=1, max_length=35, example="Leuven", description="City name", alias="community")
    country: str = Field(..., min_length=3, max_length=3, example="150", description="NIS Code of the country", alias="country")

    class Config:
        populate_by_name = True


# Backward compatibility aliases
OfficialAddressUpdate = Address
CorrespondenceAddressUpdate = Address


class AddressUpdate(BaseModel):
    """Schema for PATCH /employee-data-management/v3/employees/{employeeId}/addresses endpoint"""
    from_date: Optional[str] = Field(None, example="2022-01-01", description="Date from which this information is valid", alias="fromDate")
    official_address: Optional[Address] = Field(None, description="Official address of the employee", alias="officialAddress", json_schema_extra={"prefix": "official_address_"})
    correspondence_address: Optional[Address] = Field(None, description="Correspondence address of the employee", alias="correspondenceAddress", json_schema_extra={"prefix": "correspondence_address_"})

    class Config:
        populate_by_name = True
