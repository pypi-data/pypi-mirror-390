"""
Schemas for Employment resource

Following BrynQ SDK standards:
- Base schemas have no prefixes (reusable building blocks)
- Composite schemas use json_schema_extra={"prefix": "..."} for flat-to-nested conversion
- Uses Functions.flat_to_nested_with_prefix() in resource methods
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal


# ============================================
# BASE SCHEMAS (Reusable, No Prefixes)
# ============================================

class Name(BaseModel):
    """Reusable name schema - no prefix in field names"""
    last_name: str = Field(..., min_length=1, max_length=35, example="Janssens", description="The last name", alias="lastName")
    first_name: str = Field(..., min_length=1, max_length=35, example="Ben", description="The first name", alias="firstName")

    class Config:
        populate_by_name = True


class Birth(BaseModel):
    """Reusable birth schema - no prefix in field names"""
    date_of_birth: str = Field(..., example="2022-01-01", description="Date of birth", alias="dateOfBirth")
    place_of_birth: Optional[str] = Field(None, min_length=1, max_length=35, example="Leuven", description="Place of birth", alias="placeOfBirth")
    country_of_birth: Optional[str] = Field(None, min_length=3, max_length=3, example="150", description="NIS Code of the nationality", alias="countryOfBirth")

    class Config:
        populate_by_name = True


class Address(BaseModel):
    """Reusable address schema - no prefix in field names"""
    type: Literal["OFFICIAL", "CORRESPONDENCE"] = Field(..., example="OFFICIAL", description="Type of address", alias="type")
    street: str = Field(..., min_length=1, max_length=40, example="Bondgenotenlaan", description="Street name", alias="street")
    house_number: str = Field(..., min_length=1, max_length=9, example="2", description="House number", alias="houseNumber")
    post_box: Optional[str] = Field(None, min_length=1, max_length=4, example="A", description="Post box", alias="postBox")
    postal_code: str = Field(..., min_length=1, max_length=14, example="3000", description="Postal code", alias="postalCode")
    community: str = Field(..., min_length=1, max_length=35, example="Leuven", description="Community name", alias="community")
    country: str = Field(..., min_length=3, max_length=3, example="150", description="NIS Code of the country", alias="country")

    class Config:
        populate_by_name = True


class ContactInformation(BaseModel):
    """Reusable contact information schema - no prefix in field names"""
    contact_scope: Literal["WORK", "PERSONAL"] = Field(..., example="WORK", description="Contact scope", alias="contactScope")
    contact_method: Literal["EMAIL", "TELEPHONE", "MOBILE"] = Field(..., example="EMAIL", description="Contact method", alias="contactMethod")
    contact_value: str = Field(..., min_length=1, max_length=100, example="test@example.com", description="Contact value", alias="contactValue")

    class Config:
        populate_by_name = True


class Dependant(BaseModel):
    """Reusable dependant schema - no prefix in field names"""
    not_disabled: int = Field(..., ge=0, le=99, example=1, description="Number of not disabled dependants", alias="notDisabled")
    disabled: int = Field(..., ge=0, le=99, example=0, description="Number of disabled dependants", alias="disabled")

    class Config:
        populate_by_name = True


class Dependant65plus(BaseModel):
    """Reusable dependant 65+ schema - no prefix in field names"""
    not_disabled: int = Field(..., ge=0, le=99, example=1, description="Number of not disabled dependants over 65", alias="notDisabled")
    disabled: int = Field(..., ge=0, le=99, example=0, description="Number of disabled dependants over 65", alias="disabled")
    needing_care: int = Field(..., ge=0, le=99, example=0, description="Number of dependants over 65 needing care", alias="needingCare")

    class Config:
        populate_by_name = True


class BankAccount(BaseModel):
    """Reusable bank account schema - no prefix in field names"""
    iban: str = Field(..., min_length=5, max_length=34, example="BE11456373772248", description="IBAN", alias="iban")
    bic: Optional[str] = Field(None, min_length=8, max_length=11, example="NTSBDEB1XXX", description="BIC code", alias="bic")

    class Config:
        populate_by_name = True


class C32a(BaseModel):
    """Reusable C32a schema - no prefix in field names"""
    current_month: str = Field(..., min_length=3, max_length=13, description="Current month", alias="currentMonth")
    next_month: str = Field(..., min_length=3, max_length=13, description="Next month", alias="nextMonth")

    class Config:
        populate_by_name = True


class EmploymentPeriod(BaseModel):
    """Reusable employment period schema - no prefix in field names"""
    start_date: str = Field(..., example="2025-10-16", description="Employment start date", alias="startDate")
    end_date: Optional[str] = Field(None, example="2025-10-16", description="Employment end date", alias="endDate")

    class Config:
        populate_by_name = True


class PersonalData(BaseModel):
    """Schema for personal data - uses json_schema_extra for prefixes"""
    national_registration_number: str = Field(..., pattern=r"^\d{11}$", example="86022402508", description="National registration number", alias="nationalRegistrationNumber")
    name: Name = Field(..., description="Full name of the employee", alias="name", json_schema_extra={"prefix": "name_"})
    gender: Literal["M", "V"] = Field(..., example="M", description="Gender", alias="gender")
    nationality: str = Field(..., pattern=r"^\d{3}$", example="150", description="NIS Code of the nationality", alias="nationality")
    official_language: Optional[Literal["NL", "FR", "DE", "EN"]] = Field(None, example="NL", description="Official language", alias="officialLanguage")
    spoken_language: Optional[Literal["NL", "FR", "DE", "EN"]] = Field(None, example="NL", description="Spoken language", alias="spokenLanguage")
    birth: Birth = Field(..., description="Birth information", alias="birth", json_schema_extra={"prefix": "birth_"})
    is_disabled: Optional[bool] = Field(None, description="Disabled indicator", alias="isDisabled")

    class Config:
        populate_by_name = True


class AddressData(BaseModel):
    """Schema for address data - supports list with indexed prefixes"""
    addresses: List[Address] = Field(..., min_items=1, max_items=2, description="List of addresses", alias="addresses", json_schema_extra={"prefix": "addresses_"})

    class Config:
        populate_by_name = True


class ContactInformationData(BaseModel):
    """Schema for contact information data - supports list with indexed prefixes"""
    contact_information: List[ContactInformation] = Field(..., max_items=6, description="List of contact information", alias="contactInformation", json_schema_extra={"prefix": "contact_information_"})

    class Config:
        populate_by_name = True


class Dependants(BaseModel):
    """Schema for all dependants - uses json_schema_extra for prefixes"""
    children: Optional[Dependant] = Field(None, description="Dependent children", alias="children", json_schema_extra={"prefix": "children_"})
    sixty_five_plus: Optional[Dependant65plus] = Field(None, description="Dependent 65+", alias="65plus", json_schema_extra={"prefix": "65plus_"})
    others: Optional[Dependant] = Field(None, description="Other dependents", alias="others", json_schema_extra={"prefix": "others_"})

    class Config:
        populate_by_name = True


class PartnerInformation(BaseModel):
    """Schema for partner information - uses json_schema_extra for prefixes"""
    name: Optional[Name] = Field(None, description="Partner name", alias="name", json_schema_extra={"prefix": "name_"})
    date_of_birth: Optional[str] = Field(None, example="1956-10-30", description="Partner date of birth", alias="dateOfBirth")
    income_type: Optional[Literal["SINGLE", "DOUBLE", "NO_INCOME"]] = Field(None, example="SINGLE", description="Income type", alias="incomeType")
    is_disabled: Optional[bool] = Field(None, description="Partner disabled indicator", alias="isDisabled")

    class Config:
        populate_by_name = True


class FamilySituation(BaseModel):
    """Schema for family situation - uses json_schema_extra for prefixes"""
    marital_status: Literal["SINGLE", "MARRIED", "WIDOWED", "DIVORCED", "SEPARATED", "LEGAL_COHABITATION"] = Field(..., example="SINGLE", description="Marital status", alias="maritalStatus")
    marital_status_date: Optional[str] = Field(None, example="1984-10-30", description="Date when civil status was applied", alias="maritalStatusDate")
    date_of_marriage_or_cohabitation: Optional[str] = Field(None, example="1984-10-30", description="Date of marriage or cohabitation", alias="dateOfMarriageOrCohabitation")
    partner_information: Optional[PartnerInformation] = Field(None, description="Partner information", alias="partnerInformation", json_schema_extra={"prefix": "partner_information_"})
    dependants: Optional[Dependants] = Field(None, description="Dependants information", alias="dependants", json_schema_extra={"prefix": "dependants_"})

    class Config:
        populate_by_name = True


class EmployeeDetails(BaseModel):
    """Schema for employee details - uses json_schema_extra for prefixes"""
    personal_data: PersonalData = Field(..., description="Personal data", alias="personalData", json_schema_extra={"prefix": "personal_data_"})
    address_data: AddressData = Field(..., description="Address data", alias="addressData", json_schema_extra={"prefix": "address_data_"})
    contact_information_data: Optional[ContactInformationData] = Field(None, description="Contact information data", alias="contactInformationData", json_schema_extra={"prefix": "contact_information_data_"})
    family_situation_data: Optional[FamilySituation] = Field(None, description="Family situation data", alias="familySituationData", json_schema_extra={"prefix": "family_situation_data_"})

    class Config:
        populate_by_name = True


class EmployerDetails(BaseModel):
    """Schema for employer details - no nested prefixes needed"""
    official_joint_committee: Optional[str] = Field(None, pattern=r"^\d{6}$", example="302000", description="Official joint committee code", alias="officialJointCommittee")
    business_unit: Optional[str] = Field(None, pattern=r"^\d{10}$", example="2288734794", description="The code of the business unit", alias="businessUnit")

    class Config:
        populate_by_name = True


class EmploymentDetails(BaseModel):
    """Schema for employment details - uses json_schema_extra for prefixes"""
    employee_type: Literal["WHITE_COLLAR", "LABOURER", "BLUE_COLLAR", "STUDENT_BLUE_COLLAR", "STUDENT_WHITE_COLLAR", "FLEX_BLUE_COLLAR", "FLEX_WHITE_COLLAR"] = Field(..., description="Employee type", alias="employeeType")
    agreement_type: Optional[Literal["INTERNAL", "EXTERNAL"]] = Field(None, description="Type of the agreement", alias="agreementType")
    employment_period: EmploymentPeriod = Field(..., description="Employment period", alias="employmentPeriod", json_schema_extra={"prefix": "employment_period_"})
    in_organization_date: Optional[str] = Field(None, example="2025-10-16", description="In organization date", alias="inOrganizationDate")
    remuneration: Optional[BankAccount] = Field(None, description="Remuneration bank account", alias="remuneration", json_schema_extra={"prefix": "remuneration_"})
    c32a: Optional[C32a] = Field(None, description="C32a information", alias="c32a", json_schema_extra={"prefix": "c32a_"})
    function: Optional[str] = Field(None, min_length=1, max_length=8, description="Function code", alias="function")
    hours_per_week_full_time: Optional[float] = Field(None, ge=0, le=99, description="Hours per week full time", alias="hoursPerWeekFullTime")
    number_of_numerator_employment_fraction: Optional[float] = Field(None, description="Number of numerator employment fraction", alias="numberOfNumeratorEmploymentFraction")
    number_of_work_regime: Optional[float] = Field(None, le=7, description="Number of work regime", alias="numberOfWorkRegime")
    students_quarters: Optional[List[int]] = Field(None, min_items=1, max_items=5, example=[10], description="Students quarters", alias="studentsQuarters")
    is_disabled_for_nsso: Optional[bool] = Field(None, description="Is disabled for NSSO", alias="isDisabledForNSSO")

    class Config:
        populate_by_name = True



class EmploymentCreate(BaseModel):
    """
    Schema for POST /employers/{employerId}/employments endpoint - New employee & agreement

    Uses json_schema_extra with prefixes for flat-to-nested conversion support.
    Works with Functions.flat_to_nested_with_prefix() to convert flat dictionaries
    to properly nested structures.
    """
    employee: EmployeeDetails = Field(..., description="The details of a new employee", alias="employee", json_schema_extra={"prefix": "employee_"})
    employer: Optional[EmployerDetails] = Field(None, description="Employer details", alias="employer", json_schema_extra={"prefix": "employer_"})
    employment: EmploymentDetails = Field(..., description="Employment details", alias="employment", json_schema_extra={"prefix": "employment_"})

    class Config:
        populate_by_name = True


class EmploymentRehire(BaseModel):
    """
    Schema for POST /employers/{employerId}/employees/{employeeId}/employments endpoint - Existing employee

    This endpoint enables rehiring a previously known employee. The employee is already known
    within Connect for the employer (BOR level) and has an existing employeeId. Personal data
    is not required.

    Uses json_schema_extra with prefixes for flat-to-nested conversion support.
    Works with Functions.flat_to_nested_with_prefix() to convert flat dictionaries
    to properly nested structures.
    """
    employer: Optional[EmployerDetails] = Field(None, description="Employer details such as joint committee and business unit", alias="employer", json_schema_extra={"prefix": "employer_"})
    employment: EmploymentDetails = Field(..., description="Employment details including period, employee type, etc.", alias="employment", json_schema_extra={"prefix": "employment_"})

    class Config:
        populate_by_name = True
