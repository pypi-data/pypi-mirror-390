from typing import Dict, Any, Tuple
import pandas as pd
import requests
from brynq_sdk_functions import Functions
from .schemas.salaries import BasicSalaryGet, PatchBasicSalariesRequest
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .acerta import Acerta


class Salaries:
	"""Resource class for Agreement Basic Salaries endpoints"""

	def __init__(self, acerta):
		self.acerta: Acerta = acerta
		self.base_uri = "agreement-data-management/v1/agreements"

	def get(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /agreement-data-management/v1/agreements/{agreementId}/basic-salaries - Basic Salaries

		Retrieves basic salary history segments and their salary elements for all cached agreements.

		Args:

		Returns:
			Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df) after normalizing and validating
		"""
		if not self.acerta._agreement_ids:
			self.acerta.agreements.get()

		frames = []
		for agreement_id in self.acerta._agreement_ids:
			response = self.acerta.session.get(
				url=f"{self.acerta.base_url}/{self.base_uri}/{agreement_id}/basic-salaries",
				timeout=self.acerta.TIMEOUT,
			)
			response.raise_for_status()
			raw = response.json()
			df = pd.json_normalize(
				raw,
				record_path=["basicSalaries", "basicSalaryElements"],
				meta=["agreementId", ["basicSalaries", "period", "startDate"], ["basicSalaries", "period", "endDate"]],
				errors="ignore",
				sep=".",
			)
			frames.append(df)

		combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

		valid_df, invalid_df = Functions.validate_data(combined, BasicSalaryGet)

		return valid_df, invalid_df

	def update(self, agreement_id: str, data: Dict[str, Any]) -> requests.Response:
		"""
		PATCH /agreement-data-management/v1/agreements/{agreementId}/basic-salaries - Basic Salaries

		Update basic salary elements for a given agreement in a time window.
		"""
		nested_data = Functions.flat_to_nested_with_prefix(data, PatchBasicSalariesRequest)

		# Validate the nested data
		validated_data = PatchBasicSalariesRequest(**nested_data)

		# Make API request
		response = self.acerta.session.patch(
			url=f"{self.acerta.base_url}/{self.base_uri}/{agreement_id}/basic-salaries",
			json=validated_data.model_dump(by_alias=True, exclude_none=True),
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()

		return response
