from typing import Dict, Any, Optional, Tuple
import requests
import pandas as pd
from .schemas.agreement import (
    AgreementGet,
    PatchAgreementRequest,
    AgreementBasicInformationGet,
    AgreementEmploymentsGet,
    AgreementWorkingTimeGet,
    AgreementCommutingGet,
    AgreementCustomFieldsGet,
    AgreementCostCenterAllocationGet,
)
from .schemas.in_service_config import JointCommitteeGet, FunctionGet
from brynq_sdk_functions import Functions
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .acerta import Acerta

class Agreements:
	"""Resource class for Agreement endpoints"""

	def __init__(self, acerta):
		self.acerta: Acerta = acerta
		self.base_uri = "agreement-data-management/v3/agreements"
		# We cache agreements to avoid duplicate requests. Agreements always need to be fetched in order to get employee_ids.
		# For ease of use, we do that in the background, so you can retrieve employees without having to fetch agreements first.
		# To avoid retrieving agreements twice, we cache them so we can return them if they are already cached.
		self._cached_agreements = None

	def get_joint_committees(self, employer_id: Optional[str] = None, in_service_type: Optional[str] = None, accept_language: str = "en") -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /employee-in-service-request/v1/employers/{employerId}/joint-committees
		"""
		employers = [employer_id] if employer_id else self.acerta._employer_ids
		all_rows = []
		for emp_id in employers:
			params = {"Accept-Language": accept_language}
			if in_service_type:
				params["inServiceType"] = in_service_type
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/employee-in-service-request/v1/employers/{emp_id}/joint-committees",
				params=params,
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			raw = response.json()
			items = raw.get("_embedded", {}).get("jointCommittees", [])
			if items:
				df = pd.json_normalize(items)
				df["employer_id"] = emp_id
				all_rows.append(df)
		combined = pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()
		return Functions.validate_data(combined, JointCommitteeGet)

	def get_functions(self, employer_id: Optional[str] = None, accept_language: str = "en") -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /employee-in-service-request/v1/employers/{employerId}/functions
		"""
		employers = [employer_id] if employer_id else self.acerta._employer_ids
		all_rows = []
		for emp_id in employers:
			params = {"Accept-Language": accept_language}
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/employee-in-service-request/v1/employers/{emp_id}/functions",
				params=params,
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			raw = response.json()
			items = raw.get("_embedded", {}).get("functions", [])
			if items:
				df = pd.json_normalize(items)
				df["employer_id"] = emp_id
				all_rows.append(df)
		combined = pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()
		return Functions.validate_data(combined, FunctionGet)


	def get(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /v3/agreements - Agreements

		Retrieve agreements for all configured employer IDs. Returns agreement details including
		agreement ID, employer information, legal entity, and agreement type.

		Behavior:
			- Aggregates results across `self.acerta._employer_ids`
			- Validates and splits into valid/invalid DataFrames
			- Updates `self.acerta._employee_ids` and `_agreement_ids`
			- Caches results on first call within this instance

		Returns:
			Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df)

		Raises:
			Exception: If retrieval or validation fails
		"""
		if self._cached_agreements is None:
			self._cached_agreements = self._get_agreements()
		return self._cached_agreements

	def _get_agreements(self):
		all_dfs = []
		for employer in self.acerta._employer_ids:
			page = 0
			total_pages = 1

			while page < total_pages:
				params = {k: v for k, v in {
					"employerId": employer,
					"page": page,
					"size": 200,
				}.items() if v is not None}

				response = self.acerta.session.get(
					url=f"{self.acerta.base_url}/{self.base_uri}",
					params=params,
					timeout=self.acerta.TIMEOUT,
				)
				response.raise_for_status()

				agreements_data = response.json().get("_embedded", {}).get("agreements", [])
				if agreements_data:
					df = pd.json_normalize(agreements_data, sep=".")
					all_dfs.append(df)

				page_info = response.json().get("page") or {}
				total_pages = max(total_pages, page_info.get("totalPages", total_pages))
				page += 1

		agreements = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
		valid_agreements, invalid_agreements = Functions.validate_data(agreements, AgreementGet, debug=self.acerta.debug)

		if not valid_agreements.empty:
			self.acerta._employee_ids.update(valid_agreements["employee_id"].dropna().unique())
			self.acerta._agreement_ids.update(valid_agreements["agreement_id"].dropna().unique())

		return valid_agreements, invalid_agreements

	def get_by_id(self, agreement_id: str, accept_language: str = "en") -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""GET /v3/agreements/{agreementId}"""
		headers = {"Accept-Language": accept_language} if accept_language else None
		request_headers = self.acerta.session.headers.copy()
		if headers:
			request_headers.update(headers)
		response = self.acerta.session.get(
			url=f"{self.acerta.base_url}/{self.base_uri}/{agreement_id}",
			headers=request_headers,
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()
		raw = response.json()
		if isinstance(raw, dict):
			df = pd.json_normalize(raw, sep=".")
		else:
			df = pd.json_normalize([raw], sep=".")
		return df, pd.DataFrame()

	def update(self, agreement_id: str, data: Dict[str, Any], accept_language: str = "en") -> requests.Response:
		"""PATCH /v3/agreements/{agreementId}"""
		nested_data = Functions.flat_to_nested_with_prefix(data, PatchAgreementRequest)
		validated = PatchAgreementRequest(**nested_data)
		headers = {"Accept-Language": accept_language} if accept_language else None
		request_headers = self.acerta.session.headers.copy()
		if headers:
			request_headers.update(headers)
		response = self.acerta.session.patch(
			url=f"{self.acerta.base_url}/{self.base_uri}/{agreement_id}",
			json=validated.model_dump(by_alias=True, exclude_none=True),
			headers=request_headers,
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()
		return response

	def get_basic_information(
		self,
		agreement_id: Optional[str] = None,
		from_date: Optional[str] = None,
		until_date: Optional[str] = None,
		full_segments_only: Optional[bool] = None,
		accept_language: str = "en",
	) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""GET /v3/agreements/{agreementId}/basic-information"""
		params = {k: v for k, v in {
			"fromDate": from_date,
			"untilDate": until_date,
			"fullSegmentsOnly": str(full_segments_only).lower() if isinstance(full_segments_only, bool) else full_segments_only,
		}.items() if v is not None}
		if not agreement_id and not self.acerta._agreement_ids:
			self.get()
		ids = [agreement_id] if agreement_id else self.acerta._agreement_ids
		frames = []
		headers = {"Accept-Language": accept_language} if accept_language else None
		for agr_id in ids:
			request_headers = self.acerta.session.headers.copy()
			if headers:
				request_headers.update(headers)
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/{self.base_uri}/{agr_id}/basic-information",
				params=params,
				headers=request_headers,
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			raw = response.json()
			df = pd.json_normalize(
				raw,
				record_path=["basicInformationSegments"],
				meta=["agreementId", ["agreementType", "code"], ["agreementType", "description"]],
				errors="ignore",
				sep=".",
			)
			frames.append(df)
		combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
		return Functions.validate_data(combined, AgreementBasicInformationGet, debug=self.acerta.debug)

	def get_employments(
		self,
		agreement_id: Optional[str] = None,
		from_date: Optional[str] = None,
		until_date: Optional[str] = None,
		accept_language: str = "en",
	) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""GET /v3/agreements/{agreementId}/employments"""
		params = {k: v for k, v in {
			"fromDate": from_date,
			"untilDate": until_date,
		}.items() if v is not None}
		if not agreement_id and not self.acerta._agreement_ids:
			self.get()
		ids = [agreement_id] if agreement_id else self.acerta._agreement_ids
		frames = []
		headers = {"Accept-Language": accept_language} if accept_language else None
		for agr_id in ids:
			request_headers = self.acerta.session.headers.copy()
			if headers:
				request_headers.update(headers)
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/{self.base_uri}/{agr_id}/employments",
				params=params,
				headers=request_headers,
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			raw = response.json()
			df = pd.json_normalize(
				raw,
				record_path=["employments"],
				meta=["agreementId"],
				errors="ignore",
				sep=".",
			)
			frames.append(df)
		combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
		return Functions.validate_data(combined, AgreementEmploymentsGet, debug=self.acerta.debug)

	def get_working_time(
		self,
		agreement_id: Optional[str] = None,
		from_date: Optional[str] = None,
		until_date: Optional[str] = None,
		full_segments_only: Optional[bool] = None,
		accept_language: str = "en",
	) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""GET /v3/agreements/{agreementId}/working-time"""
		params = {k: v for k, v in {
			"fromDate": from_date,
			"untilDate": until_date,
			"fullSegmentsOnly": str(full_segments_only).lower() if isinstance(full_segments_only, bool) else full_segments_only,
		}.items() if v is not None}
		if not agreement_id and not self.acerta._agreement_ids:
			self.get()
		ids = [agreement_id] if agreement_id else self.acerta._agreement_ids
		frames = []
		headers = {"Accept-Language": accept_language} if accept_language else None
		for agr_id in ids:
			request_headers = self.acerta.session.headers.copy()
			if headers:
				request_headers.update(headers)
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/{self.base_uri}/{agr_id}/working-time",
				params=params,
				headers=request_headers,
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			raw = response.json()
			df = pd.json_normalize(
				raw,
				record_path=["workingTimeSegments"],
				meta=["agreementId"],
				errors="ignore",
				sep=".",
			)
			frames.append(df)
		combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
		return Functions.validate_data(combined, AgreementWorkingTimeGet, debug=self.acerta.debug)


	def get_commuting(
		self,
		agreement_id: Optional[str] = None,
		from_date: Optional[str] = None,
		until_date: Optional[str] = None,
		full_segments_only: Optional[bool] = None,
		accept_language: str = "en",
	) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""GET /v3/agreements/{agreementId}/commuting"""
		params = {k: v for k, v in {
			"fromDate": from_date,
			"untilDate": until_date,
			"fullSegmentsOnly": str(full_segments_only).lower() if isinstance(full_segments_only, bool) else full_segments_only,
		}.items() if v is not None}
		if not agreement_id and not self.acerta._agreement_ids:
			self.get()
		ids = [agreement_id] if agreement_id else self.acerta._agreement_ids
		frames = []
		headers = {"Accept-Language": accept_language} if accept_language else None
		for agr_id in ids:
			request_headers = self.acerta.session.headers.copy()
			if headers:
				request_headers.update(headers)
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/{self.base_uri}/{agr_id}/commuting",
				params=params,
				headers=request_headers,
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			raw = response.json()
			df = pd.json_normalize(
				raw,
				record_path=["commutingSegments"],
				meta=["agreementId"],
				errors="ignore",
				sep=".",
			)
			frames.append(df)
		combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
		return Functions.validate_data(combined, AgreementCommutingGet, debug=self.acerta.debug)

	def get_custom_fields(
		self,
		agreement_id: Optional[str] = None,
		from_date: Optional[str] = None,
		until_date: Optional[str] = None,
		custom_field_names: Optional[list] = None,
		accept_language: str = "en",
	) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""GET /v3/agreements/{agreementId}/custom-fields"""
		params_dict: Dict[str, Any] = {
			"fromDate": from_date,
			"untilDate": until_date,
		}
		if custom_field_names:
			params_dict["customFieldNames"] = ",".join(str(x) for x in custom_field_names)
		params = {k: v for k, v in params_dict.items() if v is not None}
		if not agreement_id and not self.acerta._agreement_ids:
			self.get()
		ids = [agreement_id] if agreement_id else self.acerta._agreement_ids
		frames = []
		headers = {"Accept-Language": accept_language} if accept_language else None
		for agr_id in ids:
			request_headers = self.acerta.session.headers.copy()
			if headers:
				request_headers.update(headers)
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/{self.base_uri}/{agr_id}/custom-fields",
				params=params,
				headers=request_headers,
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			raw = response.json()
			df = pd.json_normalize(
				raw,
				record_path=["customFieldsSegments"],
				meta=["agreementId"],
				errors="ignore",
				sep=".",
			)
			frames.append(df)
		combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
		return Functions.validate_data(combined, AgreementCustomFieldsGet, debug=self.acerta.debug)

	def get_cost_center_allocation(
		self,
		agreement_id: Optional[str] = None,
		from_date: Optional[str] = None,
		until_date: Optional[str] = None,
		accept_language: str = "en",
	) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""GET /v3/agreements/{agreementId}/cost-center-allocation"""
		params = {k: v for k, v in {
			"fromDate": from_date,
			"untilDate": until_date,
		}.items() if v is not None}
		if not agreement_id and not self.acerta._agreement_ids:
			self.get()
		ids = [agreement_id] if agreement_id else self.acerta._agreement_ids
		frames = []
		headers = {"Accept-Language": accept_language} if accept_language else None
		for agr_id in ids:
			request_headers = self.acerta.session.headers.copy()
			if headers:
				request_headers.update(headers)
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/{self.base_uri}/{agr_id}/cost-center-allocation",
				params=params,
				headers=request_headers,
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			raw = response.json()
			df = pd.json_normalize(
				raw,
				record_path=["costCenterAllocation"],
				meta=["agreementId"],
				errors="ignore",
				sep=".",
			)
			frames.append(df)
		combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
		return Functions.validate_data(combined, AgreementCostCenterAllocationGet, debug=self.acerta.debug)
