from typing import Dict, Any
import requests
from brynq_sdk_functions import Functions
from .schemas.in_service import EmploymentCreate, EmploymentRehire
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .acerta import Acerta


class InService:
	"""Unified resource for Acerta in-service (hire/rehire) requests.

	- Accepts flat snake_case input and converts it to nested payloads
	  using Functions.flat_to_nested_with_prefix and Employment* schemas
	- Posts to the correct employee-in-service-request endpoints
	- Polls the asynchronous status and returns parsed status data
	"""

	def __init__(self, acerta):
		self.acerta: Acerta = acerta

	def hire(self, employer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
		"""
		POST /employee-in-service-request/v1/employers/{employerId}/employments - New employee & agreement

		Accepts flat snake_case data (preferred) or already nested data.
		If flat, converts to nested structure, validates, posts, and polls.
		Returns the parsed status dict.
		"""
		# 1) Support both flat and nested payloads
		if isinstance(data.get("employee"), dict) and isinstance(data.get("employment"), dict):
			nested_data = data
		else:
			nested_data = Functions.flat_to_nested_with_prefix(data, EmploymentCreate)

		# 2) Validate against in_service schema
		validated = EmploymentCreate(**nested_data)

		# 3) Make API request
		response = self.acerta.session.post(
			url=f"{self.acerta.base_url}/employee-in-service-request/v1/employers/{employer_id}/employments",
			json=validated.model_dump(by_alias=True, exclude_none=True),
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()

		# 4) Poll status via Location header
		location = response.headers.get("Location")
		request_id = location.rsplit("/", 1)[-1] if location else ""
		status = self._get_in_service_status(request_id)
		return status

	def rehire(self, employer_id: str, employee_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
		"""
		POST /employee-in-service-request/v1/employers/{employerId}/employees/{employeeId}/employments - Existing employee

		Accepts flat snake_case data (preferred) or already nested data.
		If flat, converts to nested structure, validates, posts, and polls.
		Returns the parsed status dict.
		"""
		# 1) Support both flat and nested payloads
		if isinstance(data.get("employer"), dict) or isinstance(data.get("employment"), dict):
			nested_data = data
		else:
			nested_data = Functions.flat_to_nested_with_prefix(data, EmploymentRehire)

		# 2) Validate against in_service schema
		validated = EmploymentRehire(**nested_data)

		# 3) Make API request
		response = self.acerta.session.post(
			url=(
				f"{self.acerta.base_url}/employee-in-service-request/v1/employers/{employer_id}/employees/{employee_id}/employments"
			),
			json=validated.model_dump(by_alias=True, exclude_none=True),
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()

		# 4) Poll status via Location header
		location = response.headers.get("Location")
		request_id = location.rsplit("/", 1)[-1] if location else ""
		status = self._get_in_service_status(request_id)
		return status

	def _get_in_service_status(self, request_id: str) -> Dict[str, Any]:
		"""
		GET /employee-in-service-request/v1/status/{requestId} - Request status

		Returns parsed JSON status response for the asynchronous in-service request.
		"""
		endpoint = f"employee-in-service-request/v1/status/{request_id}"
		response = self.acerta.session.get(
			url=f"{self.acerta.base_url}/{endpoint}",
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()
		data = response.json()
		return data
