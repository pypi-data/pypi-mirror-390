"""
Schemas for Basic Salaries resource
"""

from typing import Optional, List, Literal
import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field
from brynq_sdk_functions import BrynQPanderaDataFrameModel


# ============================================
# GET SCHEMA (Pandera - DataFrame)
# ============================================

class BasicSalaryGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v1/agreements/{agreementId}/basic-salaries endpoint (rows per salary element)."""

    # Meta
    agreement_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Identifies the agreement and is unique for each agreement", alias="agreementId")

    # Period (from parent basicSalaries segment)
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="The start date of the record", alias="basicSalaries.period.startDate")
    period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="The end date of the record", alias="basicSalaries.period.endDate")

    # Salary element details
    salary_code_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="The identifier of the salary code", alias="salaryCode.salaryCodeId")
    salary_code_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="The description of the salary code", alias="salaryCode.description")

    unit_quantity: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, description="The number of units associated with the salary code", alias="unitQuantity")
    unit_amount: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, description="The amount per unit associated with the salary code", alias="unitAmount")
    percentage: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, description="The percentage associated with the salary code", alias="percentage")
    amount: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, description="The amount associated with the salary code", alias="amount")
    number_of_days: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, description="The number of days associated with the salary code", alias="numberOfDays")

    cost_center_id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="The service receiver unique cost center identifier", alias="costCenter.costCenterId")
    cost_center_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Description of the cost center", alias="costCenter.description")

    reason: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="The reason of the salary code", alias="reason")

    class _Annotation:
        primary_key = "agreement_id"

    class Config:
        metadata = {"class": "BasicSalary", "dependencies": []}


# ============================================
# PATCH SCHEMAS (Pydantic - Request)
# ============================================

class BasicSalaryAttributes(BaseModel):
    """Attributes for an INSERT action in a basic salary element."""
    unit_quantity: Optional[float] = Field(None, description="The number of units associated with the salary code", alias="unitQuantity")
    unit_amount: Optional[float] = Field(None, description="The amount per unit associated with the salary code", alias="unitAmount")
    percentage: Optional[float] = Field(None, description="The percentage associated with the salary code", alias="percentage")
    amount: Optional[float] = Field(None, description="The amount associated with the salary code", alias="amount")
    number_of_days: Optional[float] = Field(None, description="The number of days associated with the salary code", alias="numberOfDays")
    cost_center_id: Optional[str] = Field(None, min_length=1, max_length=12, description="The service receiver unique cost center identifier", alias="costCenterId")
    reason: Optional[str] = Field(None, min_length=1, max_length=50, description="The reason of the salary code", alias="reason")

    class Config:
        populate_by_name = True


class BasicSalaryElementUpdate(BaseModel):
    """Schema for a single basic salary element update operation."""
    action: Literal["DELETE", "INSERT"] = Field(..., description="DELETE will remove all elements with this salaryCodeId in the window; INSERT adds a new element", alias="action")
    salary_code_id: str = Field(..., min_length=1, max_length=6, description="The identifier of the salary code", alias="salaryCodeId")
    attributes: Optional[BasicSalaryAttributes] = Field(None, description="Attributes for INSERT action", alias="attributes", json_schema_extra={"prefix": "attributes_"})

    class Config:
        populate_by_name = True


class PatchBasicSalariesRequest(BaseModel):
    """Schema for PATCH /v1/agreements/{agreementId}/basic-salaries endpoint."""
    from_date: str = Field(..., description="The lower bound of the time window for which data will be altered", alias="fromDate")
    until_date: Optional[str] = Field(None, description="The upper bound of the time window for which data will be altered", alias="untilDate")
    basic_salary_elements: List[BasicSalaryElementUpdate] = Field(..., min_items=1, description="List of inserted or deleted salary elements for the given time window", alias="basicSalaryElements", json_schema_extra={"prefix": "basic_salary_elements_"})

    class Config:
        populate_by_name = True
