from typing import Dict, Any, Tuple
import requests
import pandas as pd
from .schemas.family import FamilyMemberGet, FamilySituationUpdate, FamilyMemberCreate, FamilySituationGet
from brynq_sdk_functions import Functions
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .acerta import Acerta

class FamilyMembers:
	"""Resource class for Family endpoints"""
	# According to Acerta this is hardly ever used, is not relevant for payroll.

	def __init__(self, acerta):
		self.acerta: Acerta = acerta
		self.base_uri = "employee-data-management/v2/employees"

	def get(self, employee_id: str, from_date: str = "1900-01-01", until_date: str = "9999-12-31",
				   full_segments_only: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /v2/employees/{employeeId}/family-members - Employee Family Members

		Retrieves family member information including relationship, personalia (name, birth, gender),
		and other details (dependant status, disability, insurance). Data is segmented by periods.

		Args:
			employee_id: Unique identifier for an employee
			from_date: Lower bound of the time window (default: "1900-01-01")
			until_date: Upper bound of the time window (default: "9999-12-31")
			full_segments_only: If True, only return complete periods (default: False)

		Returns:
			Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df) after normalizing and validating
		"""
		# Prepare query parameters
		params = {
			"fromDate": from_date,
			"untilDate": until_date,
			"fullSegmentsOnly": full_segments_only
		}

		# Make API request
		response = self.acerta.session.get(
			url=f"{self.acerta.base_url}/{self.base_uri}/{employee_id}/family-members",
			params=params,
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()
		data = response.json()

		# Extract and normalize data using pd.json_normalize
		df = pd.json_normalize(
			data,
			record_path=['familyMembersSegments', 'familyMembers'],
			meta=[
				'employeeId',
				['familyMembersSegments', 'period', 'startDate'],
				['familyMembersSegments', 'period', 'endDate'],
				['externalReferences', 0, 'externalReferenceType'],
				['externalReferences', 0, 'externalReferenceNumber'],
				['externalReferences', 0, 'companyOrganisationNumber']
			],
			sep='.'
		)

		# Validate with schema
		valid_data, invalid_data = Functions.validate_data(df, FamilyMemberGet)

		return valid_data, invalid_data

	def create(self, employee_id: str, data: Dict[str, Any]) -> requests.Response:
		"""
		POST /v1/employees/{employeeId}/family-members - Employee Family Members

		Create a new family member for an employee including relationship, personalia
		(name, birth, gender), and other information (dependant status, disability, insurance).

		Args:
			employee_id: Unique identifier of an employee
			data: Flat dictionary with family member data

		Returns:
			requests.Response: Raw response object
		"""
		# Convert flat data to nested using Functions.flat_to_nested_with_prefix
		nested_data = Functions.flat_to_nested_with_prefix(data, FamilyMemberCreate)

		# Validate the nested data
		validated_data = FamilyMemberCreate(**nested_data)

		# Make API request
		response = self.acerta.session.post(
			url=f"{self.acerta.base_url}/{self.base_uri}/{employee_id}/family-members",
			json=validated_data.model_dump(by_alias=True, exclude_none=True),
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()

		return response
