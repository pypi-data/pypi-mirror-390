from typing import Tuple, Dict, Any
import requests
import pandas as pd
from brynq_sdk_functions import Functions
from .schemas.employee import AdditionalInformationGet, AdditionalInformationUpdate
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .acerta import Acerta


class EmployeesAdditionalInformation:
    """Resource class for Employee Additional Information endpoints"""

    def __init__(self, acerta):
        self.acerta: Acerta = acerta
        self.base_uri = "employee-data-management/v3/employees"

    def get(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        GET /v3/employees/{employeeId}/additional-information - Employee Additional Information

        Retrieves employee additional information including educational degree and leadership level
        for all cached employees. This data is historical (segmented by periods).

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df) after normalizing and validating
        """
        try:
            if not self.acerta._employee_ids:
                self.acerta.agreements.get()

            frames = []
            for employee_id in self.acerta._employee_ids:
                response = self.acerta.session.get(
                    url=f"{self.acerta.base_url}/{self.base_uri}/{employee_id}/additional-information",
                    timeout=self.acerta.TIMEOUT,
                )
                response.raise_for_status()
                content = response.json()
                df = pd.json_normalize(
                    content,
                    record_path=["additionalInformationSegments"],
                    meta=["employeeId"],
                    sep="."
                )
                external_ref_columns = [col for col in df.columns if "externalReferences" in col]
                if external_ref_columns:
                    df = df.drop(columns=external_ref_columns)
                frames.append(df)

            combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

            valid_df, invalid_df = Functions.validate_data(combined, AdditionalInformationGet)

            return valid_df, invalid_df

        except Exception as e:
            raise Exception(f"Failed to retrieve employee additional information: {str(e)}") from e

    def update(self, employee_id: str, data: Dict[str, Any]) -> requests.Response:
        """
        PATCH /v3/employees/{employeeId}/additional-information - Employee Additional Information

        Update employee additional information including educational degree and leadership level.
        This data is historical.

        Args:
            employee_id: Employee identifier
            data: Dictionary with additional information data (fromDate, educationalDegree, leadershipLevel)

        Returns:
            requests.Response: Raw response object
        """
        try:
            validated_data = AdditionalInformationUpdate(**data)

            response = self.acerta.session.patch(
                url=f"{self.acerta.base_url}/{self.base_uri}/{employee_id}/additional-information",
                json=validated_data.model_dump(by_alias=True, exclude_none=True),
                timeout=self.acerta.TIMEOUT,
            )
            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to update additional information: {str(e)}") from e
