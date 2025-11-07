from typing import List, Tuple
import pandas as pd
import requests
from brynq_sdk_functions import Functions
from .schemas.planning import CountryGet, BelgianCityGet
from enum import Enum
from typing import List
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .acerta import Acerta

class CodeListAttribute(str, Enum):
		ACE_CountryNisCode = 'ACE_CountryNisCode'
		ACE_Gender = 'ACE_Gender'
		ACE_Language = 'ACE_Language'
		ACE_MaritalStatus = 'ACE_MaritalStatus'
		ACE_Nationality = 'ACE_Nationality'
		ACE_OfficialLanguageCode = 'ACE_OfficialLanguageCode'
		ACE_RelationshipContact = 'ACE_RelationshipContact'
		B10_AddressType = 'B10_AddressType'
		B10_EducationalDegree = 'B10_EducationalDegree'
		B10_LeadershipLevel = 'B10_LeadershipLevel'
		B11_JointCommittee = 'B11_JointCommittee'
		B11_PrefixNOSS = 'B11_PrefixNOSS'
		B11_Qualification = 'B11_Qualification'
		B11_PayFrequency = 'B11_PayFrequency'
		B12_ApprenticeType = 'B12_ApprenticeType'
		B12_CommunityCode = 'B12_CommunityCode'
		B12_Customized_vacation_pay = 'B12_Customized_vacation_pay'
		B12_Declaration_withholding_tax = 'B12_Declaration_withholding_tax '
		B12_DMFA_Risc_labour_accident = 'B12_DMFA_Risc_labour_accident'
		B12_Duration = 'B12_Duration'
		B12_EarlyRetirementCode = 'B12_EarlyRetirementCode'
		B12_EmployeeType = 'B12_EmployeeType'
		B12_EmployeeTypeDet = 'B12_EmployeeTypeDet'
		B12_ExemptionWorkPerformance = 'B12_ExemptionWorkPerformance'
		B12_ExemptPartTimeCreditCode = 'B12_ExemptPartTimeCreditCode'
		B12_Frequency_transport = 'B12_Frequency_transport'
		B12_Functioncode = 'B12_Functioncode'
		B12_HomeworkTransport = 'B12_HomeworkTransport'
		B12_Involuntary_parttime = 'B12_Involuntary_parttime'
		B12_Measure = 'B12_Measure'
		B12_MeasureResumptionWorkCode = 'B12_MeasureResumptionWorkCode'
		B12_Notion_NOSS = 'B12_Notion_NOSS'
		B12_NotionDebtorCode = 'B12_NotionDebtorCode'
		B12_Payment = 'B12_Payment'
		B12_Reason_end_employment = 'B12_Reason_end_employment'
		B12_Regularity = 'B12_Regularity'
		B12_Salary_calculation = 'B12_Salary_calculation'
		B12_Salary_split = 'B12_Salary_split'
		B12_SalaryScaleTypeCode = 'B12_SalaryScaleTypeCode'
		B12_Tariff_period = 'B12_Tariff_period'
		B12_TimeCredit = 'B12_TimeCredit'
		B12_TipsCode = 'B12_TipsCode'
		B12_TipsTypeCode = 'B12_TipsTypeCode'
		B12_Transport_type = 'B12_Transport_type'
		B12_Type_of_subscription = 'B12_Type_of_subscription'
		B12_Type_withholding_tax = 'B12_Type_withholding_tax'
		B12_TypeAgreement = 'B12_TypeAgreement'
		B12_WorkscheduleType = 'B12_WorkscheduleType'
		BA4_BelgianPostalCode = 'BA4_BelgianPostalCode'
		B12_MeasureNonProfit = 'B12_MeasureNonProfit'
		B12_FunctionNOSS = 'B12_FunctionNOSS'
		B12_PensionSystem = 'B12_PensionSystem'
		B12_NACE = 'B12_NACE'
		B12_Capelo_PersonnelCategory = 'B12_Capelo_PersonnelCategory'
		B12_Capelo_Function = 'B12_Capelo_Function'
		B12_Capelo_InstitutionType = 'B12_Capelo_InstitutionType'
		B12_Capelo_ServiceType = 'B12_Capelo_ServiceType'
		B12_SickLeaveReserve = 'B12_SickLeaveReserve'
		B12_Wage_system = 'B12_Wage_system'
		B12_Diploma = 'B12_Diploma'
		B12_ParticularCompetence = 'B12_ParticularCompetence'
		B12_DistinguishingLetter = 'B12_DistinguishingLetter'
		B12_ServiceActivity = 'B12_ServiceActivity'
		B12_StatusHospital = 'B12_StatusHospital'
		B12_AdditionalKwalification = 'B12_AdditionalKwalification'
		B12_Specialism = 'B12_Specialism'
		B12_StaffTypeHospital = 'B12_StaffTypeHospital'
		B12_FinancingCode = 'B12_FinancingCode'
		B12_KwalificationEmployee = 'B12_KwalificationEmployee'
		B12_OccupationalClassMWB = 'B12_OccupationalClassMWB'
		B12_KwalificationSupervisor = 'B12_KwalificationSupervisor'
		B12_IntensitySupervision = 'B12_IntensitySupervision'
		B12_StatusTargetGroup = 'B12_StatusTargetGroup'
		B12_Regional_recruitment_framework = 'B12_Regional_recruitment_framework'
		B12_Level = 'B12_Level'
		B12_ProgWorkResumpType = 'B12_ProgWorkResumpType'
		B11_VIA = 'B11_VIA'
		B12_SocialMaribel = 'B12_SocialMaribel'
		B12_Tax_Statute = 'B12_Tax_Statute'
		B12_Frontier_worker = 'B12_Frontier_worker'
		B12_AidZone = 'B12_AidZone'
		B12_Other_Social_Services = 'B12_Other_Social_Services'
		B12_Restructuring_difficulties = 'B12_Restructuring_difficulties'
		B12_Start_Job = 'B12_Start_Job'
		B12_CareerMeasure = 'B12_CareerMeasure'
		B12_Employer_recruitment_framework = 'B12_Employer_recruitment_framework'
		B12_Employee_recruitment_framework = 'B12_Employee_recruitment_framework'
		B12_IFICFunctionCode = 'B12_IFICFunctionCode'
		B12_WageCategory = 'B12_WageCategory'
		B12_RizivFrequencyCode = 'B12_RizivFrequencyCode'
		B12_RizivCode = 'B12_RizivCode'
		B12_PercentageCode = 'B12_PercentageCode'
		B12_Employee_type_2 = 'B12_Employee_type_2'
		B12_Statute = 'B12_Statute'
		B12_Employee_type = 'B12_Employee_type'
		B12_Sort = 'B12_Sort'
		ACE_YesNoUnknown = 'ACE_YesNoUnknown'


class CodeLists:
	"""Resource class for Code Lists endpoints"""

	def __init__(self, acerta):
		self.acerta: Acerta = acerta
		self.base_uri = "v1"
		self.attributes = CodeListAttribute

	def get_countries(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /v1/countries - Countries

		Retrieves the list of all countries with their NIS codes and descriptions.

		Returns:
			Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df) after validation

		Raises:
			Exception: If the retrieval fails
		"""
		# Make API request
		response = self.acerta.session.get(
			url=f"{self.acerta.base_url}/employee-data-management/v1/countries",
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()
		data = response.json()

		# Normalize data
		if isinstance(data, list):
			df = pd.json_normalize(data)
		else:
			df = pd.DataFrame([data])

		# Validate with schema
		valid_data, invalid_data = Functions.validate_data(df, CountryGet)

		return valid_data, invalid_data

	def get_belgian_cities(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
		"""
		GET /v1/belgian-cities - Belgian Cities

		Retrieves the list of all Belgian cities with their postal codes, names, and NIS codes.

		Returns:
			Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df) after validation

		Raises:
			Exception: If the retrieval fails
		"""
		# Make API request
		response = self.acerta.session.get(
			url=f"{self.acerta.base_url}/employee-data-management/v1/belgian-cities",
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()
		data = response.json()

		# Normalize data
		if isinstance(data, list):
			df = pd.json_normalize(data)
		else:
			df = pd.DataFrame([data])

		# Validate with schema
		valid_data, invalid_data = Functions.validate_data(df, BelgianCityGet)

		return valid_data, invalid_data

	def get_application_translations(self, app_id: str, lang: str, _format: str = "json"):
		"""
		GET /labelcms/v1/applications/{app_id}/translations - Application labels

		Retrieves application labels/translations for specified languages.

		Args:
			app_id: Application ID
			lang: Comma separated list of languages (e.g., "EN,NL,FR")
			_format: Request format (default: "json")

		Returns:
			Raw JSON response from API

		Raises:
			Exception: If the retrieval fails
		"""
		params = {
			"lang": lang,
			"_format": _format
		}
		response = self.acerta.session.get(
			url=f"{self.acerta.base_url}/labelcms/v1/applications/{app_id}/translations",
			params=params,
			timeout=self.acerta.TIMEOUT,
		)
		response.raise_for_status()
		return response.json()


	def get_cod_lists(
		self,
		attributes: List[CodeListAttribute],
		lang: str = 'en,nl'
	):
		"""
		GET /labelcms/v1/translations - Attributes collection (COD lists)

		Retrieves generic COD lists applicable within Acerta (country codes, gender, fuel types, etc.).
		These lists are mainly used to facilitate updates and creations of resources (Employee, Agreement, etc.).

		Args:
			attributes: List of COD list enum values or names (e.g., [CodListAttribute.B11_Fuel, CodListAttribute.B11_Gender]).
			lang: Comma separated list of languages (e.g., "en,nl,fr,de")
			_format: Request format (default: "json")

		Returns:
			Raw JSON response from API containing possible values for specified attributes and languages

		Raises:
			Exception: If the retrieval fails

		Example:
			response = acerta.planning.get_cod_lists(
				attributes=[CodListAttribute.B11_Fuel, CodListAttribute.B11_Gender],
				lang="en,nl"
			)
		"""
		# Accept string literals as fallback but enforce they match enum
		valid_values = set(item.value for item in attributes)
		attribute_strings = []
		for attribute in attributes:
			if isinstance(attribute, CodeListAttribute):
				attribute_strings.append(attribute.value)
			elif isinstance(attribute, str) and attribute in valid_values:
				attribute_strings.append(attribute)
			else:
				raise ValueError(
					f"Invalid attribute: {attribute}. Possible values: {[a.value for a in attributes]}"
				)

		attribute_string = ",".join(attribute_strings)
		params = {
			"lang": lang,
			"attributes": attribute_string,
			"_format": "json"
		}
		response = requests.get(
			url=f"https://labelcms.acerta.be/en/v1/translations",
			params=params
		)
		response.raise_for_status()
		return response.json()
