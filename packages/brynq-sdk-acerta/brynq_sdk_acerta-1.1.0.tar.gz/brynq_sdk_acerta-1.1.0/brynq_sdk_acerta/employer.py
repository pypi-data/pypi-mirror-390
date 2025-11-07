from typing import Tuple, Optional, Literal
import pandas as pd
from brynq_sdk_functions import Functions
from .schemas.employer import JointCommitteeGet, FunctionGet, SalaryCodeGet
from .cost_centers import CostCenters
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .acerta import Acerta

# Type aliases for employee service types
ServiceType = Literal[
	'WHITE_COLLAR',
	'LABOURER',
	'BLUE_COLLAR',
	'STUDENT_BLUE_COLLAR',
	'STUDENT_WHITE_COLLAR',
	'FLEX_BLUE_COLLAR',
	'FLEX_WHITE_COLLAR'
]


class Employer:
	"""Resource class for Employer endpoints"""

	def __init__(self, acerta):
		self.acerta: Acerta = acerta

		# Initialize subclass resources
		self.cost_centers = CostCenters(acerta)

	def get_joint_committees(self, employer_id: Optional[str] = None, in_service_type: Optional[ServiceType] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /employers/{employerId}/joint-committees - Joint Committees

		Retrieves all active joint committees for a specific employer. The output serves as input
		for the employee onboarding process. Can be filtered by employee classification.

		Args:
			employer_id: The ID for the employer for which the joint committees are requested
			in_service_type: The type of employee for which the joint committees should be active (optional)
				Options: WHITE_COLLAR, LABOURER, BLUE_COLLAR, STUDENT_BLUE_COLLAR,
						 STUDENT_WHITE_COLLAR, FLEX_BLUE_COLLAR, FLEX_WHITE_COLLAR
			accept_language: Response language (default: "EN")

		Returns:
			Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df) after validation

		Raises:
			Exception: If the retrieval fails
		"""
		employers = [employer_id] if employer_id else self.acerta._employer_ids
		all_rows = []
		for emp_id in employers:
			params = {}
			if in_service_type:
				params['inServiceType'] = in_service_type
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/employee-in-service-request/v1/employers/{emp_id}/joint-committees",
				params=params,
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			data = response.json()
			joint_committees = data.get("_embedded", {}).get("jointCommittees", [])
			rows = []
			for jc in joint_committees:
				base_data = {
					"employerId": emp_id,
					"code": jc.get("code"),
					"description": jc.get("description")
				}
				links = jc.get("_links", [])
				if links:
					for link in links:
						row = {**base_data}
						row["_links.rel"] = link.get("rel")
						row["_links.href"] = link.get("href")
						row["_links.title"] = link.get("title")
						row["_links.type"] = link.get("type")
						row["_links.templated"] = link.get("templated")
						rows.append(row)
				else:
					rows.append(base_data)
			if rows:
				all_rows.extend(rows)
		df = pd.DataFrame(all_rows)
		valid_data, invalid_data = Functions.validate_data(df, JointCommitteeGet)
		return valid_data, invalid_data

	def get_functions(self, employer_id: Optional[str] = None, from_date: str = "1900-01-01", until_date: str = "9999-12-31",
					  size: int = 20, page: int = 0) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /v1/employers/{employerId}/functions - Functions

		Returns employer specific functions based on an employerId.

		Args:
			employer_id: Unique identifier of the employer (Acerta key)
			from_date: The lower bound of the time window (default: "1900-01-01")
			until_date: The upper bound of the time window (default: "9999-12-31")
			size: Number of items to be returned on each page (default: 20)
			page: Zero-based page index (default: 0)

		Returns:
			Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df) after validation

		Raises:
			Exception: If the retrieval fails
		"""
		employers = [employer_id] if employer_id else self.acerta._employer_ids
		all_frames = []
		for emp_id in employers:
			params = {
				"fromDate": from_date,
				"untilDate": until_date,
				"size": size,
				"page": page
			}
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/employee-in-service-request/v1/employers/{emp_id}/functions",
				params=params,
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			data = response.json()
			functions = data.get("functions", [])
			if functions:
				df = pd.json_normalize(functions, sep='.')
				df["employerId"] = emp_id
				all_frames.append(df)
		combined = pd.concat(all_frames, ignore_index=True) if all_frames else pd.DataFrame()
		valid_data, invalid_data = Functions.validate_data(combined, FunctionGet)
		return valid_data, invalid_data

	def get_salary_codes(self, employer_id: Optional[str] = None, from_date: str = "1900-01-01", until_date: str = "9999-12-31",
						 size: int = 20, page: int = 0) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /v1/employers/{employerId}/salary-codes - Salary codes

		A salary code is an identifier used to categorize different types of earnings and deductions.
		It exists in the salary elements of a basic salary. This endpoint returns the employer specific
		salary codes based on an employerId.

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
		employers = [employer_id] if employer_id else self.acerta._employer_ids
		all_frames = []
		for emp_id in employers:
			params = {
				"fromDate": from_date,
				"untilDate": until_date,
				"size": size,
				"page": page
			}
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/employer-data-management/v1/employers/{emp_id}/salary-codes",
				params=params,
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			salary_codes_data = response.json().get("salaryCodes", [])
			if salary_codes_data:
				df = pd.json_normalize(salary_codes_data, sep='.')
				df["employerId"] = emp_id
				all_frames.append(df)
		combined = pd.concat(all_frames, ignore_index=True) if all_frames else pd.DataFrame()
		valid_data, invalid_data = Functions.validate_data(combined, SalaryCodeGet)
		return valid_data, invalid_data
