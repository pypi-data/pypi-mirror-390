"""
Schemas for Company Cars resource
"""

from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field
from brynq_sdk_functions import BrynQPanderaDataFrameModel


# ============================================
# GET SCHEMA (Pandera - DataFrame)
# ============================================

class CompanyCarGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v1/employers/{employerId}/company-cars endpoints."""

    # Period
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="The start date of the record", alias="period.startDate")
    period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="The end date of the record", alias="period.endDate")

    # Identification
    company_car_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique identifier of the company car", alias="companyCarId")
    license_plate: Series[pd.StringDtype] = pa.Field(coerce=True, description="License plate of the car", alias="licensePlate")

    # Vehicle details
    brand: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Brand of the car", alias="brand")
    type: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Type/model of the car", alias="type")
    co2: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="CO2 value of the car", alias="co2")
    fuel_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Fuel type code of the car", alias="fuel.code")
    fuel_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Fuel type description", alias="fuel.description")
    catalogue_value: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, description="Catalogue value of the car", alias="catalogueValue")
    fiscal_hp: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Fiscal horsepower of the car", alias="fiscalHp")
    is_light_cargo: Series[pd.BooleanDtype] = pa.Field(coerce=True, description="Is the car Light commercial only used for commuting?", alias="isLightCargo")
    first_subscription_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="First subscription date of the car", alias="firstSubscriptionDate")
    acquire_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Date of acquisition of the car", alias="acquireDate")
    is_hybrid: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, description="Is it a hybrid car?", alias="isHybrid")
    is_fake_hybrid: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, description="Is the car a fake hybrid?", alias="isFakeHybrid")
    co2_fake_hybrid: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="CO2 of the fake hybrid car", alias="co2FakeHybrid")
    is_pool_car: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, description="Whether the company car is a poolcar", alias="isPoolCar")

    class _Annotation:
        primary_key = "company_car_id"
        foreign_keys = {}

    class Config:
        metadata = {"class": "CompanyCar", "dependencies": []}


# ============================================
# POST/PATCH SCHEMAS (Pydantic - Request)
# ============================================

class CompanyCarPeriod(BaseModel):
    """Reusable company car period schema - no prefix in field names"""
    start_date: str = Field(..., example="1984-10-30", description="The start date of the record", alias="startDate")
    end_date: Optional[str] = Field(None, example="1984-10-30", description="The end date of the record", alias="endDate")

    class Config:
        populate_by_name = True


class CompanyCarCreate(BaseModel):
    """
    Schema for POST /v1/employers/{employerId}/company-cars endpoint
    """
    period: CompanyCarPeriod = Field(..., description="The time span of the record for which this data is valid", alias="period", json_schema_extra={"prefix": "period_"})
    license_plate: str = Field(..., min_length=1, max_length=10, example="2-DCR-765", description="License plate of the car", alias="licensePlate")
    brand: Optional[str] = Field(None, min_length=1, max_length=35, example="Renault", description="Brand of the car", alias="brand")
    type: Optional[str] = Field(None, min_length=1, max_length=50, example="megane", description="Type/model of the car", alias="type")
    co2: int = Field(..., ge=0, le=99999, example=110, description="CO2 value of the car", alias="co2")
    fuel: str = Field(..., min_length=2, max_length=2, example="02", description="Fuel type of the car (COD: B11_Fuel)", alias="fuel")
    catalogue_value: Optional[float] = Field(None, ge=0, le=999999999.99, multiple_of=0.01, example=49649.99, description="Catalogue value of the car", alias="catalogueValue")
    fiscal_hp: Optional[int] = Field(None, ge=0, le=99, example=8, description="Fiscal horsepower of the car", alias="fiscalHp")
    is_light_cargo: bool = Field(..., description="Is the car Light commercial only used for commuting?", alias="isLightCargo")
    first_subscription_date: Optional[str] = Field(None, example="2020-09-08", description="Date of first subscription of the car", alias="firstSubscriptionDate")
    acquire_date: Optional[str] = Field(None, example="2020-09-08", description="Date of acquisition of the car", alias="acquireDate")
    is_hybrid: Optional[bool] = Field(None, description="Is it a hybrid car?", alias="isHybrid")
    is_fake_hybrid: Optional[bool] = Field(None, description="Is the car a fake hybrid?", alias="isFakeHybrid")
    co2_fake_hybrid: Optional[int] = Field(None, ge=0, le=99999, example=50, description="CO2 of the fake hybrid car", alias="co2FakeHybrid")
    is_pool_car: Optional[bool] = Field(None, description="Is the car a pool car?", alias="isPoolCar")

    class Config:
        populate_by_name = True


class CompanyCarPeriodPatch(BaseModel):
    """Period for PATCH - start date required, end date optional"""
    start_date: str = Field(..., example="1984-10-30", description="The start date of the record", alias="startDate")
    end_date: Optional[str] = Field(None, example="1984-10-30", description="The end date of the record", alias="endDate")

    class Config:
        populate_by_name = True


class CompanyCarUpdate(BaseModel):
    """Schema for PATCH /v1/employers/{employerId}/company-cars/{companyCarId}"""
    period: Optional[CompanyCarPeriodPatch] = Field(None, description="The time span of the record for which this data is valid", alias="period", json_schema_extra={"prefix": "period_"})
    license_plate: Optional[str] = Field(None, min_length=1, max_length=10, example="2-DCR-765", description="License plate of the car", alias="licensePlate")
    brand: Optional[str] = Field(None, min_length=1, max_length=35, example="Renault", description="Brand of the car", alias="brand")
    type: Optional[str] = Field(None, min_length=1, max_length=50, example="megane", description="Type/model of the car", alias="type")
    co2: Optional[int] = Field(None, ge=0, le=99999, example=110, description="CO2 value of the car", alias="co2")
    fuel: Optional[str] = Field(None, min_length=2, max_length=2, example="02", description="Fuel type of the car (COD: B11_Fuel)", alias="fuel")
    catalogue_value: Optional[float] = Field(None, ge=0, le=999999999.99, multiple_of=0.01, example=49649.99, description="Catalogue value of the car", alias="catalogueValue")
    fiscal_hp: Optional[int] = Field(None, ge=0, le=99, example=8, description="Fiscal horsepower of the car", alias="fiscalHp")
    is_light_cargo: Optional[bool] = Field(None, description="Is the car Light commercial only used for commuting?", alias="isLightCargo")
    first_subscription_date: Optional[str] = Field(None, example="2020-09-08", description="Date of first subscription of the car", alias="firstSubscriptionDate")
    acquire_date: Optional[str] = Field(None, example="2020-09-08", description="Date of acquisition of the car", alias="acquireDate")
    is_hybrid: Optional[bool] = Field(None, description="Is it a hybrid car?", alias="isHybrid")
    is_fake_hybrid: Optional[bool] = Field(None, description="Is the car a fake hybrid?", alias="isFakeHybrid")
    co2_fake_hybrid: Optional[int] = Field(None, ge=0, le=99999, example=50, description="CO2 of the fake hybrid car", alias="co2FakeHybrid")
    is_pool_car: Optional[bool] = Field(None, description="Whether the company car is a poolcar", alias="isPoolCar")

    class Config:
        populate_by_name = True
