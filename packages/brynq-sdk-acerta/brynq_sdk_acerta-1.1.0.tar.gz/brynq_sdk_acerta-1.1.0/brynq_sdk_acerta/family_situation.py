from typing import Dict, Any, Tuple
import requests
import pandas as pd
from .schemas.family import FamilyMemberGet, FamilySituationUpdate, FamilyMemberCreate, FamilySituationGet
from brynq_sdk_functions import Functions
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .acerta import Acerta

class FamilySituation:
	"""Resource class for Family endpoints"""

	def __init__(self, acerta):
		self.acerta: Acerta = acerta
		self.base_uri = "v2"

	def update(self, employee_id: str, data: Dict[str, Any]) -> requests.Response:
		"""
		PATCH /employee-data-management/v3/employees/{employeeId}/family-situation - Employee Family Situation

		Update employee family situation including civil status, partner information,
		dependants (children, over 65, others), and fiscal details.

		Args:
			employee_id: Unique identifier for an employee
			data: Flat dictionary with family situation data

		Returns:
			requests.Response: Raw response object
		"""
		# Convert flat data to nested using Functions.flat_to_nested_with_prefix
		nested_data = Functions.flat_to_nested_with_prefix(data, FamilySituationUpdate)

		# Validate the nested data
		validated_data = FamilySituationUpdate(**nested_data)

		# Make API request
		response = self.acerta.session.patch(
			url=f"{self.acerta.base_url}/employee-data-management/v3/employees/{employee_id}/family-situation",
			json=validated_data.model_dump(by_alias=True, exclude_none=True),
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()

		return response

	def get(self, employee_id: str, from_date: str = "1900-01-01", until_date: str = "9999-12-31",
					  full_segments_only: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /employee-data-management/v3/employees/{employeeId}/family-situations - Employee Family Situations

		Retrieve employee family situation history within a specified time window. Returns
		civil status, partner information, dependants, and fiscal details with their validity periods.

		Args:
			employee_id: Unique identifier for an employee
			from_date: Start date of the time window (default: "1900-01-01")
			until_date: End date of the time window (default: "9999-12-31")
			full_segments_only: If True, only return complete periods (default: False)

		Returns:
			Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df) after validation

		Raises:
			Exception: If the retrieval fails
		"""
		# Prepare query parameters
		params = {
			"fromDate": from_date,
			"untilDate": until_date,
			"fullSegmentsOnly": full_segments_only
		}

		# Make API request
		response = self.acerta.session.get(
			url=f"{self.acerta.base_url}/employee-data-management/v3/employees/{employee_id}/family-situations",
			params=params,
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()
		data = response.json()

		# Normalize family situation segments data
		df = pd.json_normalize(
			data,
			record_path=['familySituationSegments'],
			meta=['employeeId'],
			sep='.'
		)

		# Drop externalReferences columns if they exist
		external_ref_columns = [col for col in df.columns if 'externalReferences' in col]
		if external_ref_columns:
			df = df.drop(columns=external_ref_columns)

		# Validate with schema
		valid_data, invalid_data = Functions.validate_data(df, FamilySituationGet)

		return valid_data, invalid_data
