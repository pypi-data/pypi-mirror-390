from typing import Dict, Any, Optional, Tuple
import requests
import pandas as pd
from brynq_sdk_functions import Functions
from .schemas.agreement import AgreementRemunerationBankAccountUpdate
from .schemas.bank_account import AgreementBankAccountsGet
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .acerta import Acerta

class BankAccounts:
	"""Resource class for Employee Bank Accounts (HAL links)."""

	def __init__(self, acerta):
		self.acerta: Acerta = acerta
		self.base_uri = "v1"

	def get(self, agreement_id: Optional[str] = None, from_date: Optional[str] = None, until_date: Optional[str] = None, full_segments_only: Optional[bool] = None, accept_language: str = "en") -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /v3/agreements/{agreementId}/remuneration - derive bank accounts

		Fetches remuneration segments for agreements and returns only the bank account related fields
		(via methodOfPayment.employeeBankAccounts/employerBankAccounts).
		"""
		# Ensure we have agreement ids
		if not agreement_id and not self.acerta._agreement_ids:
			self.acerta.agreements.get()
		agreement_ids = [agreement_id] if agreement_id else self.acerta._agreement_ids

		params = {k: v for k, v in {
			"fromDate": from_date,
			"untilDate": until_date,
			"fullSegmentsOnly": str(full_segments_only).lower() if isinstance(full_segments_only, bool) else full_segments_only,
		}.items() if v is not None}

		frames = []
		headers = {"Accept-Language": accept_language} if accept_language else None
		for agr_id in agreement_ids:
			request_headers = self.acerta.session.headers.copy()
			if headers:
				request_headers.update(headers)
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/agreement-data-management/v3/agreements/{agr_id}/remuneration",
				params=params,
				headers=request_headers,
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			raw = response.json()
			df = pd.json_normalize(
				raw,
				record_path=["remunerationSegments"],
				meta=["agreementId"],
				errors="ignore",
				sep=".",
			)
			frames.append(df)

		combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
		return Functions.validate_data(combined, AgreementBankAccountsGet, debug=self.acerta.debug)

	def update(self, agreement_id: str, data: Dict[str, Any]) -> requests.Response:
		"""
		PUT /employee-data-management/v3/employees/agreement/{agreementId}/remuneration-bank-account - Agreement Remuneration Bank Account

		Set the bank account for the employee and agreement. This endpoint updates the remuneration
		bank account associated with a specific agreement.

		Args:
			agreement_id: Unique identifier of an agreement
			data: Dictionary with bank account data (iban, bic)

		Returns:
			requests.Response: Raw response object

		Raises:
			Exception: If the update fails
		"""
		# Validate the data (no nesting required for this simple schema)
		validated_data = AgreementRemunerationBankAccountUpdate(**data)

		# Make API request
		response = self.acerta.session.put(
			url=f"{self.acerta.base_url}/employee-data-management/v3/employees/agreement/{agreement_id}/remuneration-bank-account",
			json=validated_data.model_dump(by_alias=True, exclude_none=True),
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()

		return response
