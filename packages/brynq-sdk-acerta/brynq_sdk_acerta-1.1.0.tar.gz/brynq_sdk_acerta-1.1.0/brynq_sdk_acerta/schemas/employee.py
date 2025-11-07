"""
Schema for GET /v2/employees/{employeeId}
"""

import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field
from typing import Optional
from brynq_sdk_functions import BrynQPanderaDataFrameModel


# class EmployeeGet(BrynQPanderaDataFrameModel):
#     """Schema for GET /v2/employees/{employeeId} endpoint (flat fields only)."""

#     # Identification
#     employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee identifier", alias="employeeId")

#     # Personal data - name and identification
#     national_registration_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Social security number", alias="personalData.nationalRegistrationNumber")
#     last_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Last name", alias="personalData.name.lastName")
#     first_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="First name", alias="personalData.name.firstName")
#     nick_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Nick name", alias="personalData.name.nickName")

#     # Personal data - gender, nationality, languages
#     gender_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Gender code", alias="personalData.gender.code")
#     gender_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Gender description", alias="personalData.gender.description")
#     nationality_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Nationality code", alias="personalData.nationality.code")
#     nationality_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Nationality description", alias="personalData.nationality.description")
#     official_language_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Official language code", alias="personalData.officialLanguage.code")
#     official_language_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Official language description", alias="personalData.officialLanguage.description")
#     spoken_language_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Spoken language code", alias="personalData.spokenLanguage.code")
#     spoken_language_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Spoken language description", alias="personalData.spokenLanguage.description")

#     # Birth data
#     date_of_birth: Series[pd.StringDtype] = pa.Field(coerce=True, description="Birth date", alias="personalData.birth.dateOfBirth")
#     place_of_birth: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Birth place", alias="personalData.birth.placeOfBirth")
#     birth_country_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Birth country name", alias="personalData.birth.countryOfBirth.name")
#     birth_country_nis_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Birth country NIS code", alias="personalData.birth.countryOfBirth.NISCode")

#     # Contact person (as single dict field)
#     contact_persons: Series[pd.StringDtype] = pa.Field(coerce=True, description="Contact persons data", alias="contactPersonData.contactPersons")

#     # Family situation (active period only)
#     family_period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="Family situation start date", alias="familySituationData.period.startDate")
#     family_period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Family situation end date", alias="familySituationData.period.endDate")
#     marital_status_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Marital status code", alias="familySituationData.maritalStatus.code")
#     marital_status_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Marital status description", alias="familySituationData.maritalStatus.description")
#     marital_status_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Date when civil status applied", alias="familySituationData.maritalStatusDate")

#     class _Annotation:
#         primary_key = "employee_id"
#         foreign_keys = {}

#     class Config:
#         metadata = {"class": "Employee", "dependencies": []}


class AdditionalInformationGet(BrynQPanderaDataFrameModel):
    """Schema for GET /employee-data-management/v3/employees/{employeeId}/additional-information endpoint."""

    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee identifier", alias="employeeId")
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="History segment start date", alias="period.startDate")
    period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="History segment end date", alias="period.endDate")
    educational_degree_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Educational degree code", alias="educationalDegree.code")
    educational_degree_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Educational degree description", alias="educationalDegree.description")
    leadership_level_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Leadership level code", alias="leadershipLevel.code")
    leadership_level_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Leadership level description", alias="leadershipLevel.description")

    class _Annotation:
        primary_key = "employee_id"
        foreign_keys = {}

    class Config:
        metadata = {"class": "AdditionalInformation", "dependencies": []}


class AdditionalInformationUpdate(BaseModel):
    """Schema for PATCH /employee-data-management/v3/employees/{employeeId}/additional-information"""
    from_date: Optional[str] = Field(None, example="2022-01-01", description="Date from which the information is valid", alias="fromDate")
    educational_degree: Optional[str] = Field(None, min_length=2, max_length=2, example="05", description="Educational degree code", alias="educationalDegree")
    leadership_level: Optional[str] = Field(None, min_length=2, max_length=2, example="02", description="Leadership level code", alias="leadershipLevel")

    class Config:
        populate_by_name = True


class PersonalDetailsGet(BrynQPanderaDataFrameModel):
    """Schema for GET /employee-data-management/v3/employees/{employeeId}/personal-details endpoint."""

    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee identifier", alias="employeeId")
    last_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Last name", alias="name.lastName")
    first_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="First name", alias="name.firstName")
    middle_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Middle name", alias="name.middleName")
    nick_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Nick name", alias="name.nickName")
    date_of_birth: Series[pd.StringDtype] = pa.Field(coerce=True, description="Date of birth", alias="birth.dateOfBirth")
    place_of_birth: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Place of birth", alias="birth.placeOfBirth")
    birth_country_nis_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Birth country NIS code", alias="birth.countryOfBirth.NISCode")
    birth_country_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Birth country name", alias="birth.countryOfBirth.name")
    date_of_death: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Date of death", alias="dateOfDeath")
    gender_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Gender code", alias="gender.code")
    gender_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Gender description", alias="gender.description")
    nationality_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Nationality code", alias="nationality.code")
    nationality_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Nationality description", alias="nationality.description")
    official_language_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Official language code", alias="officialLanguage.code")
    official_language_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Official language description", alias="officialLanguage.description")
    spoken_language_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Spoken language code", alias="spokenLanguage.code")
    spoken_language_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Spoken language description", alias="spokenLanguage.description")
    national_registration_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Social Security Number", alias="nationalRegistrationNumber")
    vaph_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="VAPH number", alias="vaphNumber")
    identity_card_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Identity card number", alias="identityCardNumber")
    work_permit_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Work permit number", alias="workPermitNumber")
    work_permit_valid_until: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Work permit expiration date", alias="workPermitValidUntil")
    fiscal_id_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="FIN number", alias="fiscalIdNumber")
    press_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Press number", alias="pressNumber")

    class _Annotation:
        primary_key = "employee_id"
        foreign_keys = {}

    class Config:
        metadata = {"class": "PersonalDetails", "dependencies": []}


class EmployeeName(BaseModel):
    """Reusable name schema for PATCH endpoint - no prefix in field names"""
    last_name: str = Field(..., min_length=1, max_length=35, example="Doe", description="Last name", alias="lastName")
    first_name: str = Field(..., min_length=1, max_length=35, example="John", description="First name", alias="firstName")
    middle_name: Optional[str] = Field(None, min_length=1, max_length=75, example="Johnny", description="Middle name of the employee", alias="middleName")
    nick_name: Optional[str] = Field(None, min_length=1, max_length=16, example="Johnny", description="Nick name", alias="nickName")

    class Config:
        allow_population_by_field_name = True


class EmployeeBirth(BaseModel):
    """Reusable birth information schema - no prefix in field names"""
    date_of_birth: str = Field(..., example="2000-01-01", description="Date of birth. Must be less than current date and >= 1900-01-01", alias="dateOfBirth")
    place_of_birth: Optional[str] = Field(None, min_length=1, max_length=35, example="Leuven", description="Place of birth of the employee", alias="placeOfBirth")
    country_of_birth: Optional[str] = Field(None, min_length=3, max_length=3, example="150", description="Country of birth", alias="countryOfBirth")

    class Config:
        allow_population_by_field_name = True


class PersonalDetailsUpdate(BaseModel):
    """Schema for PATCH /employee-data-management/v3/employees/{employeeId}/personal-details"""
    name: Optional[EmployeeName] = Field(None, description="Name information", alias="name", json_schema_extra={"prefix": ""})
    birth: Optional[EmployeeBirth] = Field(None, description="Birth information", alias="birth", json_schema_extra={"prefix": ""})
    date_of_death: Optional[str] = Field(None, example="2022-01-01", description="Date of death", alias="dateOfDeath")
    gender: Optional[str] = Field(None, min_length=1, max_length=1, example="M", description="Gender code", alias="gender")
    nationality: Optional[str] = Field(None, min_length=3, max_length=3, example="150", description="Nationality code", alias="nationality")
    official_language: Optional[str] = Field(None, min_length=2, max_length=2, example="NL", description="Official language code", alias="officialLanguage")
    spoken_language: Optional[str] = Field(None, min_length=2, max_length=2, example="FR", description="Spoken language code", alias="spokenLanguage")
    national_registration_number: Optional[str] = Field(None, pattern=r"^\d{11}$", example="00000000128", description="Social Security Number", alias="nationalRegistrationNumber")
    vaph_number: Optional[str] = Field(None, min_length=1, max_length=7, example="9049167", description="VAPH number", alias="vaphNumber")
    identity_card_number: Optional[str] = Field(None, min_length=1, max_length=12, example="1548151412", description="Identity card number", alias="identityCardNumber")
    work_permit_number: Optional[str] = Field(None, min_length=1, max_length=7, example="B105005", description="Work permit number", alias="workPermitNumber")
    work_permit_valid_until: Optional[str] = Field(None, example="2022-01-01", description="Work permit expiration date", alias="workPermitValidUntil")
    fiscal_id_number: Optional[str] = Field(None, min_length=1, max_length=20, example="7602155", description="FIN number", alias="fiscalIdNumber")
    press_number: Optional[str] = Field(None, min_length=1, max_length=9, example="4512121", description="Press number", alias="pressNumber")

    class Config:
        allow_population_by_field_name = True


# POST Employee Schemas - /v3/employees
class EmployeePersonalDetails(BaseModel):
    """Personal details for POST employee request - uses json_schema_extra for birth"""
    last_name: str = Field(..., min_length=1, max_length=35, example="Doe", description="Last name of the employee", alias="lastName")
    first_name: str = Field(..., min_length=1, max_length=35, example="John", description="First name of the employee", alias="firstName")
    middle_name: Optional[str] = Field(None, min_length=1, max_length=35, example="Johnny", description="Middle name of the employee", alias="middleName")
    nick_name: Optional[str] = Field(None, min_length=1, max_length=35, example="Johnny", description="Nick name of the employee", alias="nickName")
    birth: EmployeeBirth = Field(..., description="Birth information of the employee", alias="birth", json_schema_extra={"prefix": "birth_"})
    date_of_death: Optional[str] = Field(None, example="2022-01-01", description="Date of death. Must be less than current date and >= 1900-01-01", alias="dateOfDeath")
    gender: str = Field(..., min_length=1, max_length=1, example="M", description="Gender of the employee", alias="gender")
    nationality: str = Field(..., min_length=3, max_length=3, example="150", description="Nationality of the employee", alias="nationality")
    official_language: str = Field(..., min_length=2, max_length=2, example="NL", description="Official language of the employee", alias="officialLanguage")
    spoken_language: str = Field(..., min_length=2, max_length=2, example="FR", description="Spoken language of the employee", alias="spokenLanguage")
    national_registration_number: str = Field(..., pattern=r"^\d{11}$", example="00000000128", description="Social Security Number of the employee", alias="nationalRegistrationNumber")
    vaph_number: Optional[str] = Field(None, min_length=1, max_length=7, example="9049167", description="VAPH number of the employee", alias="vaphNumber")
    identity_card_number: Optional[str] = Field(None, min_length=1, max_length=12, example="1548151412", description="Identity card number of the employee", alias="identityCardNumber")
    work_permit_number: Optional[str] = Field(None, min_length=1, max_length=7, example="B105005", description="Work permit number of the employee", alias="workPermitNumber")
    work_permit_valid_until: Optional[str] = Field(None, example="2022-01-01", description="Work permit expiration date", alias="workPermitValidUntil")
    fiscal_id_number: Optional[str] = Field(None, min_length=1, max_length=20, example="7602155", description="FIN number of the employee", alias="fiscalIdNumber")
    press_number: Optional[str] = Field(None, min_length=1, max_length=9, example="4512121", description="Press number of the employee", alias="pressNumber")

    class Config:
        allow_population_by_field_name = True


class AddressBase(BaseModel):
    """Reusable base address schema - no prefix in field names"""
    street: str = Field(..., min_length=1, max_length=40, example="Bondgenotenlaan", description="Street name", alias="street")
    house_number: str = Field(..., min_length=1, max_length=9, example="2", description="House number", alias="houseNumber")
    post_box: Optional[str] = Field(None, min_length=1, max_length=4, example="A", description="Box number", alias="postBox")
    postal_code: str = Field(..., min_length=1, max_length=14, example="3000", description="Postal code", alias="postalCode")
    community: str = Field(..., min_length=1, max_length=35, example="Leuven", description="City name", alias="community")
    country: str = Field(..., min_length=3, max_length=3, example="150", description="NIS Code of the country", alias="country")

    class Config:
        allow_population_by_field_name = True


class EmployeeAddressDetails(BaseModel):
    """Address details for POST employee request - uses AddressBase with prefixes in json_schema_extra"""
    official_address: AddressBase = Field(..., description="Official address of the employee. Cannot be emptied", alias="officialAddress", json_schema_extra={"prefix": "official_address_"})
    correspondence_address: Optional[AddressBase] = Field(None, description="Correspondence address of the employee. Can be emptied", alias="correspondenceAddress", json_schema_extra={"prefix": "correspondence_address_"})

    class Config:
        allow_population_by_field_name = True


class EmployeeAdditionalInformation(BaseModel):
    """Additional information for POST employee request"""
    educational_degree: Optional[str] = Field(None, min_length=2, max_length=2, example="04", description="Educational degree", alias="educationalDegree")
    leadership_level: Optional[str] = Field(None, min_length=2, max_length=2, example="02", description="Leadership level", alias="leadershipLevel")

    class Config:
        allow_population_by_field_name = True


class ContactBase(BaseModel):
    """Reusable base contact schema - no prefix in field names"""
    telephone: Optional[str] = Field(None, min_length=1, max_length=100, example="016588774", description="Phone number", alias="telephone")
    mobile: Optional[str] = Field(None, min_length=1, max_length=100, example="0479877458", description="Mobile number", alias="mobile")
    email: Optional[str] = Field(None, min_length=1, max_length=100, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", example="contact@acerta.be", description="E-mail", alias="email")

    class Config:
        allow_population_by_field_name = True


class EmergencyContactBase(BaseModel):
    """Reusable base emergency contact schema - no prefix in field names"""
    relationship: Optional[str] = Field(None, min_length=2, max_length=2, example="10", description="Relationship with the person who to call in case of emergency", alias="relationship")
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Name of the person in case of emergency", alias="name")
    number: Optional[str] = Field(None, min_length=1, max_length=100, example="0498778855", description="Contact phone number", alias="number")

    class Config:
        allow_population_by_field_name = True


class EmployeeContactInformation(BaseModel):
    """Contact information for POST employee request - uses base schemas with prefixes in json_schema_extra"""
    personal: Optional[ContactBase] = Field(None, description="Private contact information", alias="personal", json_schema_extra={"prefix": "personal_"})
    work: Optional[ContactBase] = Field(None, description="Work related contact information", alias="work", json_schema_extra={"prefix": "work_"})
    primary_emergency_contact: Optional[EmergencyContactBase] = Field(None, description="Contact person in case of emergency (primary)", alias="primaryEmergencyContact", json_schema_extra={"prefix": "primary_emergency_contact_"})
    secondary_emergency_contact: Optional[EmergencyContactBase] = Field(None, description="Contact person in case of emergency (secondary)", alias="secondaryEmergencyContact", json_schema_extra={"prefix": "secondary_emergency_contact_"})

    class Config:
        allow_population_by_field_name = True


class EmployeeCivilStatus(BaseModel):
    """Civil status for POST employee request - no prefix in field names"""
    status: str = Field(..., min_length=2, max_length=2, example="06", description="Marital status code", alias="status")
    in_effect_date: Optional[str] = Field(None, example="2022-01-01", description="Date from which the marital status is valid. Mandatory when value differs from 01 (single)", alias="inEffectDate")
    date_of_marriage_or_cohabitation: Optional[str] = Field(None, example="2022-01-01", description="May only and must be present when Married (02), Legally cohabiting (07) or factually separated (04)", alias="dateOfMarriageOrCohabitation")

    class Config:
        allow_population_by_field_name = True


class EmployeePartner(BaseModel):
    """Partner information for POST employee request - no prefix in field names"""
    last_name: Optional[str] = Field(None, min_length=1, max_length=35, example="Achternaam", description="Partner last name", alias="lastName")
    first_name: Optional[str] = Field(None, min_length=1, max_length=35, example="Voornaam", description="Partner first name", alias="firstName")
    birth_date: Optional[str] = Field(None, example="2022-01-01", description="Partner birth date. Must be >= 1800-01-01", alias="birthDate")
    is_disabled: bool = Field(..., description="Partner disabled indicator", alias="isDisabled")
    income: str = Field(..., min_length=2, max_length=2, example="01", description="Partner income code", alias="income")

    class Config:
        allow_population_by_field_name = True


class EmployeeDependantsChildren(BaseModel):
    """Dependent children for POST employee request - no prefix in field names"""
    not_disabled: int = Field(..., ge=0, le=99, example=1, description="Number of dependant not disabled children", alias="notDisabled")
    disabled: int = Field(..., ge=0, le=99, example=1, description="Number of disabled dependant children", alias="disabled")

    class Config:
        allow_population_by_field_name = True


class EmployeeDependantsOver65(BaseModel):
    """Dependent persons 65+ for POST employee request - no prefix in field names"""
    not_disabled: int = Field(..., ge=0, le=99, example=1, description="Number of not disabled dependants over 65", alias="notDisabled")
    disabled: int = Field(..., ge=0, le=99, example=1, description="Number of disabled dependants over 65", alias="disabled")
    needing_care: int = Field(..., ge=0, le=99, example=1, description="Number of dependants over 65 needing care", alias="needingCare")

    class Config:
        allow_population_by_field_name = True


class EmployeeDependantsOthers(BaseModel):
    """Other dependent persons for POST employee request - no prefix in field names"""
    not_disabled: int = Field(..., ge=0, le=99, example=1, description="Number of not disabled other dependants", alias="notDisabled")
    disabled: int = Field(..., ge=0, le=99, example=1, description="Number of other disabled dependants", alias="disabled")

    class Config:
        allow_population_by_field_name = True


class EmployeeDependants(BaseModel):
    """Dependants information for POST employee request - uses sub-schemas with prefixes in json_schema_extra"""
    children: EmployeeDependantsChildren = Field(..., description="Number of dependant children", alias="children", json_schema_extra={"prefix": "children_"})
    over65: EmployeeDependantsOver65 = Field(..., description="Number of dependent persons 65+", alias="over65", json_schema_extra={"prefix": "over65_"})
    others: Optional[EmployeeDependantsOthers] = Field(None, description="Number of other dependent persons", alias="others", json_schema_extra={"prefix": "others_"})

    class Config:
        allow_population_by_field_name = True


class EmployeeFiscalDetails(BaseModel):
    """Fiscal details for POST employee request - no prefix in field names"""
    has_family_burden: Optional[bool] = Field(None, description="Dependent family in case of early retirement", alias="hasFamilyBurden")
    is_unmarried_with_dependant_child: Optional[bool] = Field(None, description="Not married with dependent child", alias="isUnmarriedWithDependantChild")
    is_disabled: bool = Field(..., description="Disabled indicator", alias="isDisabled")
    merging_gross_net_calculation: str = Field(..., min_length=2, max_length=2, example="02", description="Merging gross net calculation code", alias="mergingGrossNetCalculation")
    is_young_employee: Optional[bool] = Field(None, description="Young employee. Only visible for EverESSt-clients", alias="isYoungEmployee")
    tax_volunteerism_amount: Optional[float] = Field(None, example=27530.12, description="Additional monthly payroll withholding tax amount", alias="taxVolunteerismAmount")

    class Config:
        allow_population_by_field_name = True


class EmployeeFamilySituation(BaseModel):
    """Family situation for POST employee request - uses sub-schemas with prefixes in json_schema_extra"""
    civil_status: EmployeeCivilStatus = Field(..., description="Civil status of the employee", alias="civilStatus", json_schema_extra={"prefix": "civil_status_"})
    partner: Optional[EmployeePartner] = Field(None, description="Information regarding the partner. May only and must be present when Married (02), Legally cohabiting (07) or Factually separated (04)", alias="partner", json_schema_extra={"prefix": "partner_"})
    dependants: EmployeeDependants = Field(..., description="Number of dependent persons", alias="dependants", json_schema_extra={"prefix": "dependants_"})
    fiscal_details: EmployeeFiscalDetails = Field(..., description="Fiscal details", alias="fiscalDetails", json_schema_extra={"prefix": "fiscal_details_"})

    class Config:
        allow_population_by_field_name = True


class EmployeeBankDetails(BaseModel):
    """Bank details for POST employee request - no prefix in field names"""
    name_of_bank: Optional[str] = Field(None, min_length=1, max_length=35, example="Access Bank Group", description="Name of bank", alias="nameOfBank")
    street: Optional[str] = Field(None, min_length=1, max_length=40, example="Oniru Road", description="Street name", alias="street")
    house_number: Optional[str] = Field(None, min_length=1, max_length=19, example="14", description="Number", alias="houseNumber")
    post_box: Optional[str] = Field(None, min_length=1, max_length=4, example="A", description="Box", alias="postBox")
    postal_code: Optional[str] = Field(None, min_length=1, max_length=14, example="101241", description="Postcode", alias="postalCode")
    community: Optional[str] = Field(None, min_length=1, max_length=35, example="Victoria Island", description="Community", alias="community")
    country: Optional[str] = Field(None, min_length=3, max_length=3, example="234", description="Country NIS code", alias="country")

    class Config:
        allow_population_by_field_name = True


class EmployeeForeignBankAccount(BaseModel):
    """Foreign bank account for POST employee request - no prefix in field names, uses json_schema_extra for sub-schema"""
    bic: str = Field(..., min_length=1, max_length=11, pattern=r"^([A-Z]{4}[A-Z]{2}[A-Z0-9]{2}[A-Z0-9]{3}|[A-Z]{4}[A-Z]{2}[A-Z0-9]{2})$", example="HBUKGB4B", description="BIC (Bank Identifier Code)", alias="bic")
    costs: str = Field(..., min_length=4, max_length=4, example="CRED", description="Costs code", alias="costs")
    bank_details: Optional[EmployeeBankDetails] = Field(None, description="Details of the foreign bank", alias="bankDetails", json_schema_extra={"prefix": "foreign_bank_account_bank_details_"})

    class Config:
        allow_population_by_field_name = True


class EmployeeBankAccountOwner(BaseModel):
    """Bank account owner for POST employee request - no prefix in field names"""
    last_name: Optional[str] = Field(None, min_length=1, max_length=35, example="Achternaam", description="Owner last name of the bank account", alias="lastName")
    first_name: Optional[str] = Field(None, min_length=1, max_length=35, example="Voornaam", description="Owner first name of the bank account", alias="firstName")
    street: Optional[str] = Field(None, min_length=1, max_length=40, example="Gemeentestraat", description="Owner street name of the bank account", alias="street")
    house_number: Optional[str] = Field(None, min_length=1, max_length=14, example="61", description="Owner house number of the bank account", alias="houseNumber")
    post_box: Optional[str] = Field(None, min_length=1, max_length=4, example="A", description="Owner box number of the bank account", alias="postBox")
    postal_code: Optional[str] = Field(None, min_length=1, max_length=14, example="3210", description="Owner zip code of the bank account", alias="postalCode")
    community: Optional[str] = Field(None, min_length=1, max_length=35, example="Linden", description="Owner city name of the bank account", alias="community")
    country: Optional[str] = Field(None, min_length=3, max_length=3, example="150", description="Country NIS code", alias="country")

    class Config:
        allow_population_by_field_name = True


class EmployeeBankAccount(BaseModel):
    """Bank account for POST employee request - uses json_schema_extra for nested schemas"""
    iban: str = Field(..., min_length=1, max_length=34, example="BE68539007547034", description="Bank account number", alias="iban")
    text: Optional[str] = Field(None, min_length=1, max_length=40, example="Dit is een tekst", description="Notice text", alias="text")
    foreign_bank_account: Optional[EmployeeForeignBankAccount] = Field(None, description="If it concerns a foreign bank account", alias="foreignBankAccount", json_schema_extra={"prefix": "foreign_bank_account_"})
    bank_account_owner: Optional[EmployeeBankAccountOwner] = Field(None, description="If the employee is not the owner of the bankaccount", alias="bankAccountOwner", json_schema_extra={"prefix": "bank_account_owner_"})

    class Config:
        allow_population_by_field_name = True


class EmployeeCreate(BaseModel):
    """Schema for POST /v3/employees endpoint"""
    employer_id: str = Field(..., min_length=11, max_length=11, example="01458741541", description="Acerta internal reference for an employer", alias="employerId")
    external_reference: Optional[str] = Field(None, min_length=1, max_length=40, example="ext-ref-0225742-AD-00027", description="External reference during creation", alias="externalReference")
    personal_details: EmployeePersonalDetails = Field(..., description="Employee details such as name, nationality, date of birth, etc.", alias="personalDetails", json_schema_extra={"prefix": ""})
    addresses: EmployeeAddressDetails = Field(..., description="Address details of the employee", alias="addresses")
    additional_information: Optional[EmployeeAdditionalInformation] = Field(None, description="Educational degree and leadership level", alias="additionalInformation")
    contact_information: Optional[EmployeeContactInformation] = Field(None, description="Contact information of the employee", alias="contactInformation")
    family_situation: EmployeeFamilySituation = Field(..., description="Marital status information, partner details, dependents", alias="familySituation")
    bank_accounts: Optional[EmployeeBankAccount] = Field(None, description="Bank account information", alias="bankAccounts")

    class Config:
        allow_population_by_field_name = True
