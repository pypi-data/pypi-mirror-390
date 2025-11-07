"""
Schemas for Bank Accounts resource
"""

import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field
from typing import Optional, Literal
from brynq_sdk_functions import BrynQPanderaDataFrameModel


# GET via Agreements Remuneration
class AgreementBankAccountsGet(BrynQPanderaDataFrameModel):
    """Schema for bank account fields within GET /v3/agreements/{agreementId}/remuneration."""

    agreement_id: Series[pd.StringDtype] = pa.Field(coerce=True, alias="agreementId")
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, alias="period.startDate")
    period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="period.endDate")

    payment_method_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.type.code")
    payment_method_type_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.type.description")

    employee_main_iban: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employeeBankAccounts.mainAccount.iban")
    employee_main_bic: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employeeBankAccounts.mainAccount.bic")
    employee_second_iban: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employeeBankAccounts.secondAccount.iban")
    employee_second_bic: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employeeBankAccounts.secondAccount.bic")

    employer_main_iban: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employerBankAccounts.mainAccount.iban")
    employer_main_bic: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employerBankAccounts.mainAccount.bic")
    employer_second_iban: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employerBankAccounts.secondAccount.iban")
    employer_second_bic: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employerBankAccounts.secondAccount.bic")

    class Config:
        strict = False
        metadata = {"class": "AgreementBankAccounts", "dependencies": []}

# POST/PUT Schemas (Pydantic - Request)
class OwnerName(BaseModel):
    """Reusable bank account owner name schema (no prefix)"""
    first_name: str = Field(..., min_length=1, max_length=35, example="John", description="Owner first name of the bank account", alias="firstName")
    last_name: str = Field(..., min_length=1, max_length=35, example="Doe", description="Owner last name of the bank account", alias="lastName")

    class Config:
        populate_by_name = True


class BankOwner(BaseModel):
    """Reusable bank account owner schema (no prefix)"""
    name: OwnerName = Field(..., description="Owner name of the bank account", alias="name", json_schema_extra={"prefix": "name_"})
    street: str = Field(..., min_length=1, max_length=40, example="Main Street", description="Owner street name of the bank account", alias="street")
    house_number: str = Field(..., min_length=1, max_length=9, example="123", description="Owner house number of the bank account", alias="houseNumber")
    box_number: Optional[str] = Field(None, min_length=1, max_length=4, example="A", description="Owner box number of the bank account", alias="boxNumber")
    postal_code: str = Field(..., min_length=1, max_length=14, example="1000", description="Owner zip code of the bank account", alias="postalCode")
    city: str = Field(..., min_length=1, max_length=35, example="Brussels", description="Owner city name of the bank account", alias="city")
    country: str = Field(..., min_length=3, max_length=3, example="BEL", description="Owner country code", alias="country")

    class Config:
        populate_by_name = True


class BankDetails(BaseModel):
    """Reusable bank details schema (no prefix)"""
    bic: str = Field(..., min_length=8, max_length=11, pattern=r"^([A-Z]{4}[A-Z]{2}[A-Z0-9]{2}[A-Z0-9]{3}|[A-Z]{4}[A-Z]{2}[A-Z0-9]{2})$", example="SZNBDLYL", description="BIC Number", alias="bic")
    name: Optional[str] = Field(None, min_length=1, max_length=35, example="Bank Name", description="Name of the bank account", alias="name")
    street: Optional[str] = Field(None, min_length=1, max_length=40, example="Bank Street", description="Street name of the bank account", alias="street")
    house_number: Optional[str] = Field(None, min_length=1, max_length=9, example="456", description="House number of the bank account", alias="houseNumber")
    box_number: Optional[str] = Field(None, min_length=1, max_length=4, example="B", description="Box number of the bank account", alias="boxNumber")
    postal_code: Optional[str] = Field(None, min_length=1, max_length=14, example="2000", description="Zip code of the bank account", alias="postalCode")
    city: Optional[str] = Field(None, min_length=1, max_length=35, example="Antwerp", description="City name of the bank account", alias="city")
    country: Optional[str] = Field(None, min_length=3, max_length=3, example="BEL", description="Country code", alias="country")
    costs: Literal["DEBT", "CRED", "SHAR"] = Field(..., example="DEBT", description="Costs code", alias="costs")

    class Config:
        populate_by_name = True


class BankAccountUpdate(BaseModel):
    """Schema for PUT /v1/employees/{employeeId}/bank-accounts/{bankAccountId} endpoint"""

    iban: str = Field(..., min_length=1, max_length=34, example="BE68539007547034", description="Bank account number", alias="iban")
    text: Optional[str] = Field(None, min_length=1, max_length=40, example="Notice text", description="Notice text", alias="text")
    bank_details: Optional[BankDetails] = Field(None, description="If not a Belgian account, bankDetails must be specified", alias="bankDetails", json_schema_extra={"prefix": "bank_details_"})
    owner: Optional[BankOwner] = Field(None, description="If the owner is not the owner of the bankaccount, some extra data must be provided", alias="owner", json_schema_extra={"prefix": "owner_"})

    class Config:
        populate_by_name = True
