from typing import Dict, Any, Tuple
import warnings
import requests
import pandas as pd
from .family_members import FamilyMembers
from brynq_sdk_functions import Functions
from .schemas.employee import PersonalDetailsGet, PersonalDetailsUpdate, EmployeeCreate
from .employees_additional_information import EmployeesAdditionalInformation
from .addresses import Addresses
from .contact_information import ContactInformation
from .family_situation import FamilySituation
from .bank_accounts import BankAccounts
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .acerta import Acerta

class Employees:
	"""Resource class for Employee endpoints"""

	def __init__(self, acerta):
		self.acerta: Acerta = acerta
		self.base_uri = "employee-data-management"

		# Initialize subclass resources
		self.addresses = Addresses(acerta)
		self.contact_information = ContactInformation(acerta)
		self.family_situation = FamilySituation(acerta)
		self.bank_accounts = BankAccounts(acerta)
		self.additional_information = EmployeesAdditionalInformation(acerta)
		self.family_members = FamilyMembers(acerta)

	def get(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /v2/employees/{employeeId} - Employee

		Retrieves employee information including personal data, birth information, gender,
		nationality, languages, and family situation. Address and contact information
		are excluded (available in separate endpoints).

		Args:
			employee_id: Employee identifier

		Returns:
			Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df) after normalizing and validating
		"""
		all_dfs = []
		for employee_id in self.acerta._employee_ids:
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/{self.base_uri}/v3/employees/{employee_id}/personal-details",
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			df = pd.json_normalize(response.json())
			all_dfs.append(df)

		employees = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
		valid_employees, invalid_employees = Functions.validate_data(employees, PersonalDetailsGet)

		return valid_employees, invalid_employees

	def update(self, employee_id: str, data: Dict[str, Any]) -> requests.Response:
		"""
		PATCH /v3/employees/{employeeId}/personal-details - Employee personal details

		Update employee personal details including name, birth information, nationality,
		languages, identification numbers, and work permits.

		Args:
			employee_id: Employee identifier
			data: Flat dictionary with personal details data

		Returns:
			requests.Response: Raw response object
		"""
		# Convert flat data to nested using Functions.flat_to_nested_with_prefix
		nested_data = Functions.flat_to_nested_with_prefix(data, PersonalDetailsUpdate)

		# Validate the nested data
		validated_data = PersonalDetailsUpdate(**nested_data)

		# Make API request
		response = self.acerta.session.patch(
			url=f"{self.acerta.base_url}/{self.base_uri}/v3/employees/{employee_id}/personal-details",
			json=validated_data.model_dump(by_alias=True, exclude_none=True),
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()

		return response



	def create(self, data: Dict[str, Any]) -> requests.Response:
		"""
		POST /v3/employees - Employee

		Create an employee without an agreement. Includes personal details, addresses,
		contact information, family situation, bank accounts, and additional information.

		Args:
			data: Flat dictionary with employee data

		Returns:
			requests.Response: Raw response object with employeeId
		"""
		warnings.warn("Do not use this endpoint if you need to add a contract. There is no endpoint to create contracts separately, it's only possible on in-service requests. This endpoint is only used if you want to create an employee without a contract.")
		# Convert flat data to nested using Functions.flat_to_nested_with_prefix
		nested_data = Functions.flat_to_nested_with_prefix(data, EmployeeCreate)

		# Validate the nested data
		validated_data = EmployeeCreate(**nested_data)

		# Make API request
		response = self.acerta.session.post(
			url=f"{self.acerta.base_url}/{self.base_uri}/v3/employees",
			json=validated_data.model_dump(by_alias=True, exclude_none=True),
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()

		return response
