from typing import Tuple, Dict, Any, Optional
import pandas as pd
import requests
from brynq_sdk_functions import Functions
from .schemas.company_car import CompanyCarGet, CompanyCarCreate, CompanyCarUpdate
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .acerta import Acerta


class CompanyCars:
	"""Resource class for Company Cars endpoints"""

	def __init__(self, acerta):
		self.acerta: Acerta = acerta
		self.base_uri = "employer-data-management/v1/employers"

	def get(
		self,
		from_date: str = "1900-01-01",
		until_date: str = "9999-12-31",
		license_plate: Optional[str] = None,
		size: int = 20,
		page: int = 0,
	) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /v1/employers/{employerId}/company-cars - Company cars

		Retrieve company cars for all configured employer IDs within an optional time window
		and optional license plate filter. Supports basic pagination parameters.

		Args:
			from_date: The lower bound of the time window (default: "1900-01-01")
			until_date: The upper bound of the time window (default: "9999-12-31")
			license_plate: Optional license plate filter (or part of a plate)
			size: Number of items per page (default: 20)
			page: Zero-based page index (default: 0)

		Returns:
			Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df) after normalizing and validating
		"""
		all_valid_data = []
		all_invalid_data = []
		for employer_id in self.acerta._employer_ids:
			params = {
				"fromDate": from_date,
				"untilDate": until_date,
				"size": size,
				"page": page,
			}
			if license_plate:
				params["licensePlate"] = license_plate
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/{self.base_uri}/{employer_id}/company-cars",
				params=params,
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			items = response.json().get("companyCars", [])
			df = pd.json_normalize(items, sep='.')
			valid_data, invalid_data = Functions.validate_data(df, CompanyCarGet)
			all_valid_data.append(valid_data)
			all_invalid_data.append(invalid_data)

		return (
			pd.concat(all_valid_data, ignore_index=True) if all_valid_data else pd.DataFrame(),
			pd.concat(all_invalid_data, ignore_index=True) if all_invalid_data else pd.DataFrame(),
		)

	def get_by_id(self, employer_id: str, company_car_id: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /v1/employers/{employerId}/company-cars/{companyCarId} - Company car by ID

		Args:
			employer_id: Unique identifier of the employer (Acerta key)
			company_car_id: Unique identifier of the company car (6 digits)

		Returns:
			Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df)
		"""
		response = self.acerta.session.get(
			url=f"{self.acerta.base_url}/{self.base_uri}/{employer_id}/company-cars/{company_car_id}",
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()
		raw = response.json()
		if isinstance(raw, dict):
			df = pd.json_normalize(raw, sep='.')
		else:
			df = pd.json_normalize([raw], sep='.')
		return Functions.validate_data(df, CompanyCarGet)

	def create(self, employer_id: str, data: Dict[str, Any]) -> requests.Response:
		"""
		POST /v1/employers/{employerId}/company-cars - Company car

		Args:
			employer_id: Unique identifier of the employer (Acerta key)
			data: Flat dictionary with company car data

		Returns:
			requests.Response: Raw response object
		"""
		# Convert flat data to nested using Functions.flat_to_nested_with_prefix
		nested = Functions.flat_to_nested_with_prefix(data, CompanyCarCreate)
		validated = CompanyCarCreate(**nested)
		response = self.acerta.session.post(
			url=f"{self.acerta.base_url}/{self.base_uri}/{employer_id}/company-cars",
			json=validated.model_dump(by_alias=True, exclude_none=True),
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()
		return response

	def update(self, employer_id: str, company_car_id: str, data: Dict[str, Any]) -> requests.Response:
		"""
		PATCH /v1/employers/{employerId}/company-cars/{companyCarId} - Update company car

		Args:
			employer_id: Unique identifier of the employer (Acerta key)
			company_car_id: Unique identifier of the company car
			data: Flat dictionary with update fields

		Returns:
			requests.Response: Raw response object
		"""
		nested = Functions.flat_to_nested_with_prefix(data, CompanyCarUpdate)
		validated = CompanyCarUpdate(**nested)
		response = self.acerta.session.patch(
			url=f"{self.acerta.base_url}/{self.base_uri}/{employer_id}/company-cars/{company_car_id}",
			json=validated.model_dump(by_alias=True, exclude_none=True),
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()
		return response
