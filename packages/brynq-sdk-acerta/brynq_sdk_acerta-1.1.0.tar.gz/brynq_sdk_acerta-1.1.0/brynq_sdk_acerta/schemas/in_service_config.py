import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class JointCommitteeGet(BrynQPanderaDataFrameModel):
    code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Joint committee code")
    description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Description")

    class _Annotation:
        primary_key = "code"
        foreign_keys = {}

    class Config:
        metadata = {"class": "JointCommittee", "dependencies": []}


class FunctionGet(BrynQPanderaDataFrameModel):
    code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Function code")
    description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Description")

    class _Annotation:
        primary_key = "code"
        foreign_keys = {}

    class Config:
        metadata = {"class": "Function", "dependencies": []}
