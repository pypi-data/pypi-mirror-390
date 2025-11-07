from typing import Dict, Any, Tuple
import pandas as pd
import requests
from brynq_sdk_functions import Functions
from .schemas.contact_information import ContactInformationGet, ContactInformationUpdate
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .acerta import Acerta


class ContactInformation:
    """Resource class for Employee Contact Information endpoints"""

    def __init__(self, acerta):
        self.acerta: Acerta = acerta
        self.base_uri = "employee-data-management/v3/employees"

    def get(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        GET /employee-data-management/v3/employees/{employeeId}/contact-information - Employee Contact Information

        Retrieves employee contact information for all cached employees including personal contact (phone, mobile, email),
        work contact, and emergency contacts (primary and secondary).

        Args:

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df) after normalizing and validating
        """
        if not self.acerta._employee_ids:
            self.acerta.agreements.get()

        frames = []
        for employee_id in self.acerta._employee_ids:
            response = self.acerta.session.get(
                url=f"{self.acerta.base_url}/{self.base_uri}/{employee_id}/contact-information",
                timeout=self.acerta.TIMEOUT,
            )
            response.raise_for_status()
            df = pd.json_normalize(response.json())
            if 'externalReferences' in df.columns:
                df = df.drop(columns=['externalReferences'])
            frames.append(df)

        combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

        valid_df, invalid_df = Functions.validate_data(combined, ContactInformationGet)

        return valid_df, invalid_df

    def update(self, employee_id: str, data: Dict[str, Any]) -> requests.Response:
        """
        PATCH /employee-data-management/v3/employees/{employeeId}/contact-information - Employee Contact Information

        Update employee contact information including personal contact (phone, mobile, email),
        work contact, and emergency contacts (primary and secondary).

        Args:
            employee_id: Unique identifier of an employee
            data: Flat dictionary with contact information data

        Returns:
            requests.Response: Raw response object
        """
        # Convert flat data to nested using Functions.flat_to_nested_with_prefix
        nested_data = Functions.flat_to_nested_with_prefix(data, ContactInformationUpdate)

        # Validate the nested data
        validated_data = ContactInformationUpdate(**nested_data)

        # Make API request
        response = self.acerta.session.patch(
            url=f"{self.acerta.base_url}/{self.base_uri}/{employee_id}/contact-information",
            json=validated_data.model_dump(by_alias=True, exclude_none=True),
            timeout=self.acerta.TIMEOUT,
        )
        response.raise_for_status()

        return response
