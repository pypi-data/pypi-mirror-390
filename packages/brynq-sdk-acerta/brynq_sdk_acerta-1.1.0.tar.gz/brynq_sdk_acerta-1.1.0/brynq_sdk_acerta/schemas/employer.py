"""
Schemas for Employer resource
"""

import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel


# GET Schema for Joint Committees
class JointCommitteeGet(BrynQPanderaDataFrameModel):
    """Schema for GET /employers/{employerId}/joint-committees endpoint"""

    employer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer identifier", alias="employerId")
    code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Joint committee code", alias="code")
    description: Series[pd.StringDtype] = pa.Field(coerce=True, description="Joint committee description", alias="description")
    # links_rel: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="HAL link relation", alias="_links.rel")
    # links_href: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="HAL link href", alias="_links.href")
    # links_title: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="HAL link title", alias="_links.title")
    # links_type: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="HAL link type", alias="_links.type")
    # links_templated: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, description="HAL link templated flag", alias="_links.templated")

    class _Annotation:
        primary_key = "code"

    class Config:
        metadata = {"class": "JointCommittee", "dependencies": []}


# GET Schema for Functions (per employer-data-management spec)
class FunctionGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v1/employers/{employerId}/functions endpoint"""

    # Function identification
    function_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Code of the function", alias="functionId")

    # Period information
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="The start date of the record", alias="period.startDate")
    period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="The end date of the record", alias="period.endDate")

    # Descriptions (handled as JSON string since it's a list)
    descriptions: Series[pd.StringDtype] = pa.Field(coerce=True, description="Function descriptions per language (as JSON)", alias="descriptions")

    class _Annotation:
        primary_key = "function_id"

    class Config:
        metadata = {"class": "Function", "dependencies": []}


# GET Schema for Salary Codes
class SalaryCodeGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v1/employers/{employerId}/salary-codes endpoint"""

    # Salary Code identification
    salary_code_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="The identifier of the salary code", alias="salaryCodeId")

    # Period information
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="The start date of the record", alias="period.startDate")
    period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="The end date of the record", alias="period.endDate")

    # Descriptions (handled as JSON string since it's a list)
    descriptions: Series[pd.StringDtype] = pa.Field(coerce=True, description="Salary code descriptions per language (as JSON)", alias="descriptions")

    class _Annotation:
        primary_key = "salary_code_id"
        foreign_keys = {}

    class Config:
        metadata = {"class": "SalaryCode", "dependencies": []}
