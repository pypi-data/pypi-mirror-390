"""
Schemas for Cost Centers resource
"""

import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from brynq_sdk_functions import BrynQPanderaDataFrameModel


# ============================================
# GET SCHEMA (Pandera - DataFrame)
# ============================================

class CostCenterGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v1/employers/{employerId}/cost-centers endpoint."""

    # Cost Center identification
    cost_center_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="The service receiver cost center number", alias="costCenterId")

    # Period information
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="The start date of the record", alias="period.startDate")
    period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="The end date of the record", alias="period.endDate")

    # Optional fields
    accountancy: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="The accountancy cost center linked to the service receiver cost center number", alias="accountancy")
    acknowledgement_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="The acknowledgement number linked to the service receiver cost center number", alias="acknowledgementNumber")

    # Descriptions (handled as JSON string since it's a list)
    descriptions: Series[pd.StringDtype] = pa.Field(coerce=True, description="Cost center descriptions per language (as JSON)", alias="descriptions")

    class _Annotation:
        primary_key = "cost_center_id"
        foreign_keys = {}

    class Config:
        metadata = {"class": "CostCenter", "dependencies": []}


# ============================================
# POST SCHEMAS (Pydantic - Request)
# ============================================

class CostCenterDescription(BaseModel):
    """Reusable cost center description schema - no prefix in field names"""
    language: Literal["EN", "en", "NL", "nl", "FR", "fr"] = Field(..., example="EN", description="Language of the description", alias="language")
    description: str = Field(..., min_length=1, max_length=100, example="Cost center for business line 4454-01.", description="Description of the cost center", alias="description")

    class Config:
        populate_by_name = True


class CostCenterPeriod(BaseModel):
    """Reusable cost center period schema - no prefix in field names"""
    start_date: str = Field(..., example="1984-10-30", description="The start date of the record", alias="startDate")
    end_date: Optional[str] = Field(None, example="1984-10-30", description="The end date of the record", alias="endDate")

    class Config:
        populate_by_name = True


class CostCenterCreate(BaseModel):
    """
    Schema for POST /v1/employers/{employerId}/cost-centers endpoint

    Uses json_schema_extra with prefixes for flat-to-nested conversion support.
    Works with Functions.flat_to_nested_with_prefix() to convert flat dictionaries
    to properly nested structures.
    """
    cost_center_id: str = Field(..., min_length=1, max_length=12, example="4454-01", description="The service receiver cost center number", alias="costCenterId")
    descriptions: List[CostCenterDescription] = Field(..., min_items=1, max_items=3, description="Cost center descriptions per language", alias="descriptions", json_schema_extra={"prefix": "descriptions_"})
    period: CostCenterPeriod = Field(..., description="The time span of the record for which this data is valid", alias="period", json_schema_extra={"prefix": "period_"})
    accountancy: Optional[str] = Field(None, min_length=1, max_length=12, example="ADMINISTR1", description="The accountancy cost center linked to the service receiver cost center number", alias="accountancy")
    acknowledgement_number: Optional[str] = Field(None, min_length=1, max_length=8, example="975", description="The acknowledgement number linked to the service receiver cost center number", alias="acknowledgementNumber")

    class Config:
        populate_by_name = True
