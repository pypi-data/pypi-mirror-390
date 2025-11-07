from typing import Tuple, Dict, Any
import pandas as pd
import requests
from brynq_sdk_functions import Functions
from .schemas.cost_center import CostCenterGet, CostCenterCreate
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .acerta import Acerta


class CostCenters:
	"""Resource class for Cost Centers endpoints"""

	def __init__(self, acerta):
		self.acerta: Acerta = acerta
		self.base_uri = "employer-data-management/v1/employers"

	def get(self, from_date: str = "1900-01-01", until_date: str = "9999-12-31",
			size: int = 20, page: int = 0) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /v1/employers/{employerId}/cost-centers - Cost centers

		This endpoint returns the cost centers of an employer based on its employerId for a given period.
		An employer can have 0 to N cost centers. Cost centers are primarily used for reporting purposes.

		Args:
			employer_id: Unique identifier of the employer (Acerta key)
			from_date: The lower bound of the time window (default: "1900-01-01")
			until_date: The upper bound of the time window (default: "9999-12-31")
			size: Number of items to be returned on each page (default: 20)
			page: Zero-based page index (default: 0)

		Returns:
			Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df) after normalizing and validating

		Raises:
			Exception: If the retrieval fails
		"""
		all_valid_data = []
		all_invalid_data = []
		for employer_id in self.acerta._employer_ids:
			# Prepare query parameters
			params = {
				"fromDate": from_date,
				"untilDate": until_date,
				"size": size,
				"page": page
			}
			# Make API request
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/{self.base_uri}/{employer_id}/cost-centers",
				params=params,
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			cost_centers_data = response.json().get("costCenters", [])
			df = pd.json_normalize(cost_centers_data, sep='.')
			valid_data, invalid_data = Functions.validate_data(df, CostCenterGet)
			all_valid_data.append(valid_data)
			all_invalid_data.append(invalid_data)

		return pd.concat(all_valid_data, ignore_index=True), pd.concat(all_invalid_data, ignore_index=True)

	def create(self, employer_id: str, data: Dict[str, Any]) -> requests.Response:
		"""
		POST /v1/employers/{employerId}/cost-centers - Cost center

		This endpoint creates a cost center for an employer.

		Args:
			employer_id: Unique identifier of the employer (Acerta key)
			data: Flat dictionary with cost center data

		Returns:
			requests.Response: Raw response object

		Raises:
			Exception: If the creation fails
		"""
		# Convert flat data to nested using Functions.flat_to_nested_with_prefix
		nested_data = Functions.flat_to_nested_with_prefix(data, CostCenterCreate)

		# Validate the nested data
		validated_data = CostCenterCreate(**nested_data)

		# Make API request
		response = self.acerta.session.post(
			url=f"{self.acerta.base_url}/{self.base_uri}/{employer_id}/cost-centers",
			json=validated_data.model_dump(by_alias=True, exclude_none=True),
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()

		return response
