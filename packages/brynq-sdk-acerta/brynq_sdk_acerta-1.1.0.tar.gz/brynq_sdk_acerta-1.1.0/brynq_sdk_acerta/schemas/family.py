"""
Schemas for Family resource
"""

import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field
from typing import Optional, Literal
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class FamilyMemberGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v2/employees/{employeeId}/family-members endpoint"""

    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="The employeeId is the unique identifier for an employee", alias="employeeId")
    external_reference_type: Series[pd.StringDtype] = pa.Field(coerce=True, description="Identifies you as a consumer and is identical for each employee of the same consumer", alias="externalReferences.externalReferenceType")
    external_reference_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Identifies the employee for this consumer and is unique for each employee of the same consumer", alias="externalReferences.externalReferenceNumber")
    company_organisation_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Identifies the company organisation (COR/BOR) this employee is linked to", alias="externalReferences.companyOrganisationNumber")
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="Start date of the family member period", alias="familyMembersSegments.period.startDate")
    period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="End date of the family member period", alias="familyMembersSegments.period.endDate")
    family_member_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="The identifier of the family member in the associated history segment", alias="familyMemberId")
    first_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="First name of the family member", alias="personalData.name.firstName")
    last_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Last name of the family member", alias="personalData.name.lastName")
    birth_day: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Birth day of the family member", alias="personalData.birthDay")
    decease_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Decease date of the family member", alias="personalData.deceaseDate")
    relationship_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Relationship code", alias="personalData.relationship.code")
    relationship_description: Series[pd.StringDtype] = pa.Field(coerce=True, description="Relationship description", alias="personalData.relationship.description")
    gender_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Gender code", alias="personalData.gender.code")
    gender_description: Series[pd.StringDtype] = pa.Field(coerce=True, description="Gender description", alias="personalData.gender.description")
    dependent_persons: Series[pd.BooleanDtype] = pa.Field(coerce=True, description="Dependant indicator", alias="dependentDisabledPersons.dependentPersons")
    disabled_person: Series[pd.BooleanDtype] = pa.Field(coerce=True, description="Disabled indicator", alias="dependentDisabledPersons.disabledPerson")
    degree_self_reliance: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Disability degree", alias="dependentDisabledPersons.degreeSelfReliance")
    in_group_insurance: Series[pd.BooleanDtype] = pa.Field(coerce=True, description="Group insurance indicator", alias="insurance.inGroupInsurance")
    in_hospital_insurance: Series[pd.BooleanDtype] = pa.Field(coerce=True, description="Hospitalisation insurance indicator", alias="insurance.inHospitalInsurance")
    comment: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Comment of the family member", alias="comment")

    class _Annotation:
        primary_key = "family_member_id"
        foreign_keys = {
            "employee_id": {"parent_schema": "EmployeeGet", "parent_column": "employee_id", "cardinality": "N:1"}
        }

    class Config:
        metadata = {"class": "FamilyMember", "dependencies": []}


class CivilStatus(BaseModel):
    """Reusable civil status schema - no prefix in field names"""
    status: str = Field(..., min_length=2, max_length=2, example="06", description="Marital status code", alias="status")
    in_effect_date: Optional[str] = Field(None, example="2022-01-01", description="Date from which the marital status is valid", alias="inEffectDate")
    date_of_marriage_or_cohabitation: Optional[str] = Field(None, example="2022-01-01", description="Date of marriage or cohabitation", alias="dateOfMarriageOrCohabitation")

    class Config:
        populate_by_name = True


class Partner(BaseModel):
    """Reusable partner schema - no prefix in field names"""
    last_name: Optional[str] = Field(None, min_length=1, max_length=35, example="Achternaam", description="Partner last name", alias="lastName")
    first_name: Optional[str] = Field(None, min_length=1, max_length=35, example="Voornaam", description="Partner first name", alias="firstName")
    birth_date: Optional[str] = Field(None, example="2022-01-01", description="Partner birth date", alias="birthDate")
    is_disabled: Optional[bool] = Field(None, description="Partner disabled indicator", alias="isDisabled")
    income: Optional[str] = Field(None, min_length=2, max_length=2, example="01", description="Partner income code", alias="income")

    class Config:
        populate_by_name = True


class DependantsChildren(BaseModel):
    """Reusable children dependants schema - no prefix in field names"""
    not_disabled: Optional[int] = Field(None, ge=0, le=99, example=1, description="Number of dependant not disabled children", alias="notDisabled")
    disabled: Optional[int] = Field(None, ge=0, le=99, example=1, description="Number of disabled dependant children", alias="disabled")

    class Config:
        populate_by_name = True


class DependantsOver65(BaseModel):
    """Reusable over 65 dependants schema - no prefix in field names"""
    not_disabled: Optional[int] = Field(None, ge=0, le=99, example=1, description="Number of not disabled dependants over 65", alias="notDisabled")
    disabled: Optional[int] = Field(None, ge=0, le=99, example=1, description="Number of disabled dependants over 65", alias="disabled")
    needing_care: Optional[int] = Field(None, ge=0, le=99, example=1, description="Number of dependants over 65 needing care", alias="needingCare")

    class Config:
        populate_by_name = True


class DependantsOthers(BaseModel):
    """Reusable other dependants schema - no prefix in field names"""
    not_disabled: Optional[int] = Field(None, ge=0, le=99, example=1, description="Number of not disabled other dependants", alias="notDisabled")
    disabled: Optional[int] = Field(None, ge=0, le=99, example=1, description="Number of other disabled dependants", alias="disabled")

    class Config:
        populate_by_name = True


class Dependants(BaseModel):
    """Dependants container schema - uses json_schema_extra for prefixes"""
    children: Optional[DependantsChildren] = Field(None, description="Number of dependent children", alias="children", json_schema_extra={"prefix": "children_"})
    over65: Optional[DependantsOver65] = Field(None, description="Number of dependent persons 65+", alias="over65", json_schema_extra={"prefix": "over65_"})
    others: Optional[DependantsOthers] = Field(None, description="Number of other dependent persons", alias="others", json_schema_extra={"prefix": "others_"})

    class Config:
        populate_by_name = True


class FiscalDetails(BaseModel):
    """Reusable fiscal details schema - no prefix in field names"""
    has_family_burden: Optional[bool] = Field(None, description="Dependent family in case of early retirement", alias="hasFamilyBurden")
    is_unmarried_with_dependant_child: Optional[bool] = Field(None, description="Not married with dependent child", alias="isUnmarriedWithDependantChild")
    is_disabled: Optional[bool] = Field(None, description="Disabled indicator", alias="isDisabled")
    merging_gross_net_calculation: Optional[str] = Field(None, min_length=2, max_length=2, example="02", description="Merging gross net calculation code", alias="mergingGrossNetCalculation")
    is_young_employee: Optional[bool] = Field(None, description="Young employee", alias="isYoungEmployee")
    tax_volunteerism_amount: Optional[float] = Field(None, description="Additional monthly payroll withholding tax amount", alias="taxVolunteerismAmount")

    class Config:
        populate_by_name = True


class FamilySituationUpdate(BaseModel):
    """Schema for PATCH /v3/employees/{employeeId}/family-situation - uses json_schema_extra for prefixes"""
    from_date: Optional[str] = Field(None, example="2022-01-01", description="Date from when this data is valid", alias="fromDate")
    civil_status: Optional[CivilStatus] = Field(None, description="Civil status of the employee", alias="civilStatus", json_schema_extra={"prefix": "civil_status_"})
    partner: Optional[Partner] = Field(None, description="Information regarding the partner", alias="partner", json_schema_extra={"prefix": "partner_"})
    dependants: Optional[Dependants] = Field(None, description="Number of dependent persons", alias="dependants", json_schema_extra={"prefix": "dependants_"})
    fiscal_details: Optional[FiscalDetails] = Field(None, description="Fiscal details", alias="fiscalDetails", json_schema_extra={"prefix": "fiscal_details_"})

    class Config:
        populate_by_name = True


# POST Schemas for Family Members
class FamilyMemberName(BaseModel):
    """Reusable family member name schema - no prefix in field names"""
    first_name: str = Field(..., min_length=1, max_length=35, example="SAL", description="First name of the family member", alias="firstName")
    last_name: str = Field(..., min_length=1, max_length=35, example="FERIT", description="Last name of the family member", alias="lastName")

    class Config:
        populate_by_name = True


class FamilyMemberPersonalia(BaseModel):
    """Reusable family member personalia schema - no prefix in field names, uses json_schema_extra for name prefix"""
    relationship: Optional[str] = Field(None, example="09", description="The relationship of this family member", alias="relationship")
    name: FamilyMemberName = Field(..., description="Name", alias="name", json_schema_extra={"prefix": "name_"})
    birth_date: Optional[str] = Field(None, example="2000-01-01", description="Birth date of the family member", alias="birthDate")
    decease_date: Optional[str] = Field(None, example="2000-01-01", description="Death date of the family member", alias="deceaseDate")
    gender: Optional[str] = Field(None, example="V", description="Gender of the family member", alias="gender")

    class Config:
        populate_by_name = True


class FamilyMemberOther(BaseModel):
    """Reusable family member other data schema - no prefix in field names"""
    dependant_persons: bool = Field(..., example=True, description="Dependant indicator", alias="dependantPersons")
    disabled_person: bool = Field(..., example=True, description="Disabled indicator", alias="disabledPerson")
    degree_self_reliance: Optional[int] = Field(None, ge=0, le=99, example=18, description="Disability degree", alias="degreeSelfReliance")
    in_group_insurance: bool = Field(..., example=True, description="Group insurance indicator", alias="inGroupInsurance")
    in_hospital_insurance: bool = Field(..., example=True, description="Hospitalisation insurance indicator", alias="inHospitalInsurance")

    class Config:
        populate_by_name = True


class FamilyMemberCreate(BaseModel):
    """Schema for POST /v1/employees/{employeeId}/family-members endpoint - uses json_schema_extra for prefixes"""
    valid_from: str = Field(..., example="2025-10-16", description="Date when the change is registered", alias="validFrom")
    history_from_date: Optional[str] = Field(None, example="2025-10-16", description="Date on which the value of the returned historical data is valid", alias="historyFromDate")
    sequence: Optional[str] = Field(None, min_length=3, max_length=3, example="001", description="Unique number per family member", alias="sequence")
    personalia: FamilyMemberPersonalia = Field(..., description="Personalia", alias="personalia", json_schema_extra={"prefix": "personalia_"})
    other: Optional[FamilyMemberOther] = Field(None, description="Other", alias="other", json_schema_extra={"prefix": "other_"})

    class Config:
        populate_by_name = True


# GET Schema for Family Situations
class FamilySituationGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v3/employees/{employeeId}/family-situations endpoint"""

    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee identifier", alias="employeeId")
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="Family situation period start date", alias="period.startDate")
    period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Family situation period end date", alias="period.endDate")
    civil_status_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Marital status code", alias="civilStatus.status.code")
    civil_status_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Marital status description", alias="civilStatus.status.description")
    civil_status_in_effect_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Date from which the marital status is valid", alias="civilStatus.inEffectDate")
    civil_status_date_of_marriage_or_cohabitation: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Date of marriage or cohabitation", alias="civilStatus.dateOfMarriageOrCohabitation")
    partner_last_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Partner last name", alias="partner.lastName")
    partner_first_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Partner first name", alias="partner.firstName")
    partner_birth_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Partner birth date", alias="partner.birthDate")
    partner_is_disabled: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, description="Partner disabled indicator", alias="partner.isDisabled")
    partner_income_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Partner income code", alias="partner.income.code")
    partner_income_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Partner income description", alias="partner.income.description")
    dependants_children_not_disabled: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Number of dependant not disabled children", alias="dependants.children.notDisabled")
    dependants_children_disabled: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Number of disabled dependant children", alias="dependants.children.disabled")
    dependants_over65_not_disabled: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Number of not disabled dependants over 65", alias="dependants.over65.notDisabled")
    dependants_over65_disabled: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Number of disabled dependants over 65", alias="dependants.over65.disabled")
    dependants_over65_needing_care: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Number of dependants over 65 needing care", alias="dependants.over65.needingCare")
    dependants_others_not_disabled: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Number of not disabled other dependants", alias="dependants.others.notDisabled")
    dependants_others_disabled: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Number of other disabled dependants", alias="dependants.others.disabled")
    fiscal_details_has_family_burden: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, description="Dependent family in case of early retirement", alias="fiscalDetails.hasFamilyBurden")
    fiscal_details_is_unmarried_with_dependant_child: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, description="Not married with dependent child", alias="fiscalDetails.isUnmarriedWithDependantChild")
    fiscal_details_is_disabled: Series[pd.BooleanDtype] = pa.Field(coerce=True, description="Disabled indicator", alias="fiscalDetails.isDisabled")
    fiscal_details_merging_gross_net_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Merging gross net calculation code", alias="fiscalDetails.mergingGrossNetCalculation.code")
    fiscal_details_merging_gross_net_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Merging gross net calculation description", alias="fiscalDetails.mergingGrossNetCalculation.description")
    fiscal_details_is_young_employee: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, description="Young employee indicator", alias="fiscalDetails.isYoungEmployee")
    fiscal_details_tax_volunteerism_amount: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, description="Tax volunteerism amount", alias="fiscalDetails.taxVolunteerismAmount")

    class _Annotation:
        primary_key = "employee_id"

    class Config:
        metadata = {"class": "FamilySituation", "dependencies": []}
