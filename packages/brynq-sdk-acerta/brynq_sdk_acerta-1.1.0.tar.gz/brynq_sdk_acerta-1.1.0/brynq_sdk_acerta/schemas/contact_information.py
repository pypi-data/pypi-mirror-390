"""
Schema for GET /employee-data-management/v3/employees/{employeeId}/contact-information
"""

import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field
from typing import Optional
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class ContactInformationGet(BrynQPanderaDataFrameModel):
    """Schema for GET /employee-data-management/v3/employees/{employeeId}/contact-information endpoint"""

    # Employee identification
    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee identifier", alias="employeeId")

    # Personal contact information
    personal_telephone: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Personal phone number", alias="personal.telephone")
    personal_mobile: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Personal mobile number", alias="personal.mobile")
    personal_email: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Personal email", alias="personal.email")

    # Work contact information
    work_telephone: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Work phone number", alias="work.telephone")
    work_mobile: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Work mobile number", alias="work.mobile")
    work_email: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Work email", alias="work.email")

    # Primary emergency contact
    primary_emergency_relationship_code: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Primary emergency contact relationship code", alias="primaryEmergencyContact.relationship.code")
    primary_emergency_relationship_description: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Primary emergency contact relationship description", alias="primaryEmergencyContact.relationship.description")
    primary_emergency_name: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Primary emergency contact name", alias="primaryEmergencyContact.name")
    primary_emergency_number: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Primary emergency contact number", alias="primaryEmergencyContact.number")

    # Secondary emergency contact
    secondary_emergency_relationship_code: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Secondary emergency contact relationship code", alias="secondaryEmergencyContact.relationship.code")
    secondary_emergency_relationship_description: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Secondary emergency contact relationship description", alias="secondaryEmergencyContact.relationship.description")
    secondary_emergency_name: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Secondary emergency contact name", alias="secondaryEmergencyContact.name")
    secondary_emergency_number: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Secondary emergency contact number", alias="secondaryEmergencyContact.number")

    class _Annotation:
        primary_key = "employee_id"
        foreign_keys = {}

    class Config:
        metadata = {"class": "ContactInformation", "dependencies": []}




# Reusable base schemas - no prefix in field names
class Contact(BaseModel):
    """Reusable contact schema - no prefix in field names"""
    telephone: Optional[str] = Field(None, min_length=1, max_length=100, example="016588774", description="Phone number", alias="telephone")
    mobile: Optional[str] = Field(None, min_length=1, max_length=100, example="0479877458", description="Mobile number", alias="mobile")
    email: Optional[str] = Field(None, min_length=1, max_length=100, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", example="contact@example.com", description="E-mail", alias="email")

    class Config:
        populate_by_name = True


class EmergencyContact(BaseModel):
    """Reusable emergency contact schema - no prefix in field names"""
    relationship: Optional[str] = Field(None, min_length=2, max_length=2, example="10", description="Relationship with the person", alias="relationship")
    name: Optional[str] = Field(None, min_length=1, max_length=50, example="John Emergency", description="Name of the person", alias="name")
    number: Optional[str] = Field(None, min_length=1, max_length=100, example="0498778855", description="Contact phone number", alias="number")

    class Config:
        populate_by_name = True


class ContactInformationUpdate(BaseModel):
    """Schema for PATCH /employee-data-management/v3/employees/{employeeId}/contact-information - uses json_schema_extra for prefixes"""
    personal: Optional[Contact] = Field(None, description="Personal contact information", alias="personal", json_schema_extra={"prefix": "personal_"})
    work: Optional[Contact] = Field(None, description="Work contact information", alias="work", json_schema_extra={"prefix": "work_"})
    primary_emergency_contact: Optional[EmergencyContact] = Field(None, description="Primary emergency contact", alias="primaryEmergencyContact", json_schema_extra={"prefix": "primary_emergency_"})
    secondary_emergency_contact: Optional[EmergencyContact] = Field(None, description="Secondary emergency contact", alias="secondaryEmergencyContact", json_schema_extra={"prefix": "secondary_emergency_"})

    class Config:
        populate_by_name = True
