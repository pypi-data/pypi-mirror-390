from typing import Tuple, Dict, Any
import pandas as pd
import requests
from brynq_sdk_functions import Functions
from .schemas.address import AddressGet, AddressUpdate
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .acerta import Acerta

class Addresses:
	"""Resource class for Employee Address endpoints"""

	def __init__(self, acerta):
		self.acerta: Acerta = acerta
		self.base_uri = "v3/employee-data-management/v3/employees"

	def get(self, from_date: str = "1900-01-01", until_date: str = "9999-12-31") -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /employee-data-management/v3/employees/{employeeId}/addresses - Employee Addresses

		Retrieve employee address history within a specified time window for all cached employees.
		Returns both official and correspondence addresses with their validity periods.

		Args:
			from_date: Start date of the time window (default: "1900-01-01")
			until_date: End date of the time window (default: "9999-12-31")

		Returns:
			Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df) after validation

		Raises:
			RuntimeError: If the retrieval fails
		"""
		params = {
			"fromDate": from_date,
			"untilDate": until_date
		}

		if not self.acerta._employee_ids:
			# Auto-warm cache by fetching agreements (populates employee IDs)
			self.acerta.agreements.get()

		all_frames = []
		for employee_id in self.acerta._employee_ids:
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/{self.base_uri}/{employee_id}/addresses",
				params=params,
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			content = response.json()
			df = pd.json_normalize(
				content,
				record_path=['addressSegments'],
				meta=['employeeId'],
				sep='.'
			)
			if 'externalReferences' in df.columns:
				df = df.drop(columns=['externalReferences'])
			all_frames.append(df)

		combined = pd.concat(all_frames, ignore_index=True) if all_frames else pd.DataFrame()

		valid_data, invalid_data = Functions.validate_data(combined, AddressGet)

		return valid_data, invalid_data

	def update(self, employee_id: str, data: Dict[str, Any]) -> requests.Response:
		"""
		PATCH /employee-data-management/v3/employees/{employeeId}/addresses - Employee Address

		Update employee address information including official address and optional
		correspondence address. Addresses are historical data with validity dates.

		Args:
			employee_id: Unique identifier of an employee
			data: Flat dictionary with address data

		Returns:
			requests.Response: Raw response object

		Raises:
			RuntimeError: If the address update fails
		"""
		# Convert flat data to nested using Functions.flat_to_nested_with_prefix
		nested_data = Functions.flat_to_nested_with_prefix(data, AddressUpdate)

		# Validate the nested data
		validated_data = AddressUpdate(**nested_data)

		# Make API request
		response = self.acerta.session.patch(
			url=f"{self.acerta.base_url}/{self.base_uri}/{employee_id}/addresses",
			json=validated_data.model_dump(by_alias=True, exclude_none=True),
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()

		return response
