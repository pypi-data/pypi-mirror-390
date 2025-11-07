"""
Schemas for Agreements resource
"""

import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from brynq_sdk_functions import BrynQPanderaDataFrameModel

# GET Schema (Pandera - DataFrame)
class AgreementGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v3/agreements endpoint"""

    agreement_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Identifies the agreement and is unique for each agreement", alias="agreementId")
    external_reference: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="External reference for the agreement", alias="externalReference")
    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="The employeeId is the unique identifier for an employee", alias="employeeId")
    employer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="The employerId is the unique identifier for an employer", alias="employerId")
    legal_entity: Series[pd.StringDtype] = pa.Field(coerce=True, description="Legal entity identifier", alias="legalEntity")
    agreement_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Agreement type code", alias="agreementType.code")
    agreement_type_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Agreement type description", alias="agreementType.description")

    class _Annotation:
        primary_key = "agreement_id"
        foreign_keys = {
            "employee_id": {"parent_schema": "EmployeeGet", "parent_column": "employee_id", "cardinality": "N:1"}
        }

    class Config:
        strict = False
        metadata = {"class": "Agreement", "dependencies": []}

# POST Schema (Pydantic - Request)
class AgreementRemunerationBankAccountCreate(BaseModel):
    """Schema for POST /v1/agreements/{agreementId}/remuneration-bank-account endpoint"""

    iban: str = Field(..., min_length=1, max_length=34, example="BE68539007547034", description="Bank account number", alias="iban")
    bic: Optional[str] = Field(None, min_length=8, max_length=11, example="GEBABEBB", description="Bank identification code", alias="bic")

    class Config:
        populate_by_name = True


# ==============================
# GET Schemas (Pandera - Frames)
# ==============================

class AgreementBasicInformationGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v3/agreements/{agreementId}/basic-information (segments)."""

    agreement_id: Series[pd.StringDtype] = pa.Field(coerce=True, alias="agreementId")
    agreement_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, alias="agreementType.code")
    agreement_type_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="agreementType.description")
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, alias="period.startDate")
    period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="period.endDate")
    c32_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="c32Code.code")
    c32_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="c32Code.description")

    # officialEmployerData
    oem_official_joint_committee_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployerData.officialJointCommittee.code")
    oem_official_joint_committee_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployerData.officialJointCommittee.description")
    oem_nsso_prefix_code: Series[pd.StringDtype] = pa.Field(coerce=True, alias="officialEmployerData.nssoPrefix.code")
    oem_nsso_prefix_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployerData.nssoPrefix.description")
    oem_indexation_joint_committee_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployerData.indexationJointCommittee.code")
    oem_indexation_joint_committee_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployerData.indexationJointCommittee.description")
    oem_business_unit: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployerData.businessUnit")
    oem_point_of_operation: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployerData.pointOfOperation")
    oem_multiple_points_of_operations: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployerData.multiplePointsOfOperations")
    oem_replacement_agreement_id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployerData.replacementAgreementId")

    # officialEmployeeData
    oee_employee_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.employeeType.code")
    oee_employee_type_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.employeeType.description")
    oee_employee_type_detail_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.employeeTypeDetail.code")
    oee_employee_type_detail_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.employeeTypeDetail.description")
    oee_duration_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.duration.code")
    oee_duration_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.duration.description")
    oee_agreement_details_sort_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.agreementDetails.sort.code")
    oee_agreement_details_sort_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.agreementDetails.sort.description")
    oee_agreement_details_nsso_category_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.agreementDetails.nssoCategory.code")
    oee_agreement_details_nsso_category_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.agreementDetails.nssoCategory.description")
    oee_agreement_details_statute_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.agreementDetails.statute.code")
    oee_agreement_details_statute_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.agreementDetails.statute.description")
    oee_agreement_details_nsso_exemption_category_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.agreementDetails.nssoExemptionCategory.code")
    oee_agreement_details_nsso_exemption_category_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.agreementDetails.nssoExemptionCategory.description")
    oee_withholding_tax_tax_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.withHoldingTax.taxType.code")
    oee_withholding_tax_tax_type_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.withHoldingTax.taxType.description")
    oee_withholding_tax_declaration_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.withHoldingTax.declaration.code")
    oee_withholding_tax_declaration_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.withHoldingTax.declaration.description")
    oee_withholding_tax_cross_border_worker_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.withHoldingTax.crossBorderWorker.code")
    oee_withholding_tax_cross_border_worker_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.withHoldingTax.crossBorderWorker.description")
    oee_withholding_tax_gross_net_contraction: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.withHoldingTax.grossNetContraction")
    oee_nsso_work_place_accident_risk_category_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.nsso.workPlaceAccidentRiskCategory.code")
    oee_nsso_work_place_accident_risk_category_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.nsso.workPlaceAccidentRiskCategory.description")
    oee_nsso_nsso_notion_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.nsso.nssoNotion.code")
    oee_nsso_nsso_notion_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.nsso.nssoNotion.description")
    oee_nsso_disabled_for_nsso: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.nsso.disabledForNsso")
    oee_transport_costs_fully_taxed: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, alias="officialEmployeeData.transportCostsFullyTaxed")

    # apprentice
    apprentice_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="apprentice.type.code")
    apprentice_type_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="apprentice.type.description")
    apprentice_community_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="apprentice.community.code")
    apprentice_community_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="apprentice.community.description")
    apprentice_contract_term: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="apprentice.contractTerm")
    apprentice_contract_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="apprentice.contractNumber")
    apprentice_starting_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="apprentice.apprenticeStartingDate")

    # earlyRetirement
    early_retirement_contribution_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="earlyRetirement.earlyRetirementContribution.code")
    early_retirement_contribution_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="earlyRetirement.earlyRetirementContribution.description")
    early_retirement_counter_fraction_dmfa: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="earlyRetirement.counterFractionDmfa")
    early_retirement_pension_category_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="earlyRetirement.pensionCategory.code")
    early_retirement_pension_category_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="earlyRetirement.pensionCategory.description")
    early_retirement_contribution_to_supplementary_payment_resumption_of_work_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="earlyRetirement.contributionToSupplementaryPayment.resumptionOfWork.code")
    early_retirement_contribution_to_supplementary_payment_resumption_of_work_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="earlyRetirement.contributionToSupplementaryPayment.resumptionOfWork.description")
    early_retirement_contribution_to_supplementary_payment_first_allocation_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="earlyRetirement.contributionToSupplementaryPayment.firstAllocationDate")
    early_retirement_contribution_to_supplementary_payment_last_allocation_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="earlyRetirement.contributionToSupplementaryPayment.lastAllocationDate")
    early_retirement_contribution_to_supplementary_payment_notion_debtor_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="earlyRetirement.contributionToSupplementaryPayment.notionDebtor.code")
    early_retirement_contribution_to_supplementary_payment_notion_debtor_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="earlyRetirement.contributionToSupplementaryPayment.notionDebtor.description")
    early_retirement_contribution_to_supplementary_payment_work_exemption_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="earlyRetirement.contributionToSupplementaryPayment.workExemption.code")
    early_retirement_contribution_to_supplementary_payment_work_exemption_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="earlyRetirement.contributionToSupplementaryPayment.workExemption.description")
    early_retirement_social_security_replacement_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="earlyRetirement.socialSecurityReplacementNumber")

    # retirement
    retirement_nihdi_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="retirement.nihdiCode.code")
    retirement_nihdi_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="retirement.nihdiCode.description")
    retirement_nihdi_frequency_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="retirement.nihdiFrequency.code")
    retirement_nihdi_frequency_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="retirement.nihdiFrequency.description")

    # construction
    construction_c32a_current_month_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="construction.c32aCurrentMonthNumber")
    construction_c32a_next_month_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="construction.c32aNextMonthNumber")

    class Config:
        strict = False
        metadata = {"class": "AgreementBasicInformation", "dependencies": []}


class AgreementEmploymentsGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v3/agreements/{agreementId}/employments (segments)."""

    agreement_id: Series[pd.StringDtype] = pa.Field(coerce=True, alias="agreementId")
    employment_period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, alias="employmentPeriod.startDate")
    employment_period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="employmentPeriod.endDate")
    interim_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="interimStartDate")
    in_organisation_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="inOrganisationDate")
    trial_period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="trialPeriodEndDate")
    contractual_period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="contractualPeriodEndDate")
    ignore_seniority_in_case_of_illness: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, alias="ignoreSeniorityInCaseOfIllness")
    reason_termination_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reasonTermination.code")
    reason_termination_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reasonTermination.description")
    notice_date_notice_served: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="notice.dateNoticeServed")
    notice_letter_sent_on: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="notice.noticeLetterSentOn")
    notice_period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="notice.noticePeriod.startDate")
    notice_period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="notice.noticePeriod.endDate")
    notice_end_disruption_period: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="notice.endDisruptionPeriod")
    leaving_date_end_mutual_remuneration: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="leavingEmployment.dateEndMutualRemuneration")
    leaving_date_end_goodwill_indemnity: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="leavingEmployment.dateEndGoodwillIndemnity")
    leaving_date_end_integration_compensation: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="leavingEmployment.dateEndIntegrationCompensation")
    leaving_date_end_non_competition_remuneration: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="leavingEmployment.dateEndNonCompetitionRemuneration")
    leaving_date_end_medical_force_majeure: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="leavingEmployment.dateEndMedicalForceMajeure")
    students_quarters_days_q1: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="studentsQuarters.daysOfStudentWorkFirstQuarterNumber")
    students_quarters_days_q2: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="studentsQuarters.daysOfStudentWorkSecondQuarterNumber")
    students_quarters_days_q3: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="studentsQuarters.daysOfStudentWorkThirdQuarterNumber")
    students_quarters_days_q4: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="studentsQuarters.daysOfStudentWorkFourthQuarterNumber")
    students_quarters_days_q5: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="studentsQuarters.daysOfStudentWorkFifthQuarterNumber")

    class Config:
        strict = False
        metadata = {"class": "AgreementEmployments", "dependencies": []}


class AgreementWorkingTimeGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v3/agreements/{agreementId}/working-time (segments)."""

    agreement_id: Series[pd.StringDtype] = pa.Field(coerce=True, alias="agreementId")
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, alias="period.startDate")
    period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="period.endDate")
    working_time_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, alias="workingTimeType.code")
    working_time_type_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="workingTimeType.description")
    work_schedule: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="workSchedule")
    work_regime: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="workRegime")
    hours_week_full_time: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="hoursWeekFullTime")
    pay_on_annual_basis: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payOnAnnualBasis")
    employment_fraction_numerator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="employmentFraction.numerator")
    employment_fraction_denominator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="employmentFraction.denominator")
    original_employment_fraction_numerator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="originalEmploymentFraction.numerator")
    original_employment_fraction_denominator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="originalEmploymentFraction.denominator")
    effective_employment_fraction_numerator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="effectiveEmploymentFraction.numerator")
    effective_employment_fraction_denominator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="effectiveEmploymentFraction.denominator")
    time_credits_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="timeCredits.code")
    time_credits_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="timeCredits.description")
    reduced_working_hours_regularity_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.regularity.code")
    reduced_working_hours_regularity_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.regularity.description")
    reduced_working_hours_measure_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.measure.code")
    reduced_working_hours_measure_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.measure.description")
    reduced_working_hours_involuntary_part_time_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.involuntaryPartTime.code")
    reduced_working_hours_involuntary_part_time_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.involuntaryPartTime.description")
    reduced_working_hours_refusal_of_employment_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.refusalOfEmploymentDate")
    reduced_working_hours_has_progressive_work_resumption: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.hasProgressiveWorkResumption")
    reduced_working_hours_illness_other_employer_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.illnessOtherEmployerStartDate")
    reduced_working_hours_progressive_work_resumption_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.progressiveWorkResumptionType.code")
    reduced_working_hours_progressive_work_resumption_type_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.progressiveWorkResumptionType.description")
    reduced_working_hours_adjusted_work_regime: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.adjustedWorkRegime")
    reduced_working_hours_adjusted_work_fraction_numerator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.adjustedWorkFraction.numerator")
    reduced_working_hours_adjusted_work_fraction_denominator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.adjustedWorkFraction.denominator")
    reduced_working_hours_measure1_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.measure1.code")
    reduced_working_hours_measure1_percentage: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.measure1.percentage")
    reduced_working_hours_measure2_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.measure2.code")
    reduced_working_hours_measure2_percentage: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.measure2.percentage")
    reduced_working_hours_full_time_absence: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, alias="reducedWorkingHours.fullTimeAbsence")
    exemption_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="exemptionOfWorkObligations.exemptionType.code")
    exemption_type_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="exemptionOfWorkObligations.exemptionType.description")
    art54bis_or_ter: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, alias="exemptionOfWorkObligations.art54bisOrTer")

    class Config:
        strict = False
        metadata = {"class": "AgreementWorkingTime", "dependencies": []}


class AgreementRemunerationGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v3/agreements/{agreementId}/remuneration (segments)."""

    agreement_id: Series[pd.StringDtype] = pa.Field(coerce=True, alias="agreementId")
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, alias="period.startDate")
    period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="period.endDate")
    steering_group_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="generalRemuneration.steeringGroup.code")
    steering_group_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="generalRemuneration.steeringGroup.description")
    accounting_organisation_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="generalRemuneration.accountingOrganisation.code")
    accounting_organisation_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="generalRemuneration.accountingOrganisation.description")
    function_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="generalRemuneration.function.code")
    function_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="generalRemuneration.function.description")
    function_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="generalRemuneration.functionStartDate")
    organisation: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="generalRemuneration.organisation")
    cost_centre: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="generalRemuneration.costCentre")
    cost_centre_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="generalRemuneration.costCentreDescription")
    standard_accounting_profile_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="generalRemuneration.standardAccountingProfile.code")
    standard_accounting_profile_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="generalRemuneration.standardAccountingProfile.description")
    pay_frequency_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="generalRemuneration.frequency.code")
    pay_frequency_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="generalRemuneration.frequency.description")
    calculation_method_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payCalculation.calculationMethod.code")
    salary_split_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payCalculation.salarySplit.code")
    salary_qualification_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payCalculation.salaryQualification.code")
    payment_scheme_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payCalculation.paymentScheme.code")
    remuneration_fraction_numerator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payCalculation.remunerationFraction.numerator")
    remuneration_fraction_denominator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payCalculation.remunerationFraction.denominator")
    tip_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payCalculation.tip.type.code")
    tip_type_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payCalculation.tip.type.description")
    tip_professional_role_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payCalculation.tip.professionalRole.code")
    tip_professional_role_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payCalculation.tip.professionalRole.description")
    method_of_payment_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.type.code")
    method_of_payment_type_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.type.description")
    employee_main_account_iban: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employeeBankAccounts.mainAccount.iban")
    employee_main_account_bic: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employeeBankAccounts.mainAccount.bic")
    employee_second_account_iban: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employeeBankAccounts.secondAccount.iban")
    employee_second_account_bic: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employeeBankAccounts.secondAccount.bic")
    employer_main_account_iban: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employerBankAccounts.mainAccount.iban")
    employer_main_account_bic: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employerBankAccounts.mainAccount.bic")
    employer_second_account_iban: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employerBankAccounts.secondAccount.iban")
    employer_second_account_bic: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfPayment.employerBankAccounts.secondAccount.bic")
    has_group_insurance: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, alias="insuranceDetails.hasGroupInsurance")
    has_hospital_insurance: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, alias="insuranceDetails.hasHospitalInsurance")
    has_hospital_insurance_for_spouse: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, alias="insuranceDetails.hasHospitalInsuranceForSpouse")
    work_accident_insurance_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="insuranceDetails.workAccidentInsuranceNumber")
    work_accident_insurance_policy_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="insuranceDetails.workAccidentInsurancePolicyNumber")
    group_insurance_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="insuranceDetails.groupInsuranceNumber")
    group_insurance_policy_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="insuranceDetails.groupInsurancePolicyNumber")
    other_insurance_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="insuranceDetails.otherInsuranceNumber")
    other_insurance_policy_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="insuranceDetails.otherInsurancePolicyNumber")
    contribution_second_retirement_pillar_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payCalculation.contributionSecondRetirementPillar.code")
    contribution_second_retirement_pillar_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payCalculation.contributionSecondRetirementPillar.description")
    wage_category_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payCalculation.wageCategory.code")
    wage_category_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payCalculation.wageCategory.description")

    # Pay scale
    pay_scale_use: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.usePayScale")
    pay_scale_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.type.code")
    pay_scale_type_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.type.description")
    pay_scale_selection_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.payScaleSelection.code")
    pay_scale_selection_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.payScaleSelection.description")
    pay_scale_experience: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.experience")
    pay_scale_pay_grade: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.payGrade")
    pay_scale_level_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.level.code")
    pay_scale_level_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.level.description")

    # IFIC (within payScale)
    pay_scale_ific_use: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.useIFIC")
    pay_scale_ific_use_scale: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.useScale")
    pay_scale_ific_seniority_year_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.seniority.yearNumber")
    pay_scale_ific_seniority_month_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.seniority.monthNumber")
    pay_scale_ific_salary_scale_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.salaryScale.code")
    pay_scale_ific_salary_scale_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.salaryScale.description")
    pay_scale_ific_remuneration_fraction_numerator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.remunerationFraction.numerator")
    pay_scale_ific_remuneration_fraction_denominator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.remunerationFraction.denominator")
    pay_scale_ific_function_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.function.code")
    pay_scale_ific_function_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.function.description")

    # IFIC hybrid functions
    pay_scale_ific_hybrid1_function_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_1.function.code")
    pay_scale_ific_hybrid1_function_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_1.function.description")
    pay_scale_ific_hybrid1_salary_scale_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_1.salaryScale.code")
    pay_scale_ific_hybrid1_salary_scale_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_1.salaryScale.description")
    pay_scale_ific_hybrid1_fraction_numerator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_1.fraction.numerator")
    pay_scale_ific_hybrid1_fraction_denominator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_1.fraction.denominator")

    pay_scale_ific_hybrid2_function_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_2.function.code")
    pay_scale_ific_hybrid2_function_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_2.function.description")
    pay_scale_ific_hybrid2_salary_scale_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_2.salaryScale.code")
    pay_scale_ific_hybrid2_salary_scale_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_2.salaryScale.description")
    pay_scale_ific_hybrid2_fraction_numerator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_2.fraction.numerator")
    pay_scale_ific_hybrid2_fraction_denominator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_2.fraction.denominator")

    pay_scale_ific_hybrid3_function_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_3.function.code")
    pay_scale_ific_hybrid3_function_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_3.function.description")
    pay_scale_ific_hybrid3_salary_scale_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_3.salaryScale.code")
    pay_scale_ific_hybrid3_salary_scale_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_3.salaryScale.description")
    pay_scale_ific_hybrid3_fraction_numerator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_3.fraction.numerator")
    pay_scale_ific_hybrid3_fraction_denominator: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payScale.ific.hybridFunction_3.fraction.denominator")

    class Config:
        strict = False
        metadata = {"class": "AgreementRemuneration", "dependencies": []}


class AgreementCommutingGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v3/agreements/{agreementId}/commuting (segments)."""

    agreement_id: Series[pd.StringDtype] = pa.Field(coerce=True, alias="agreementId")
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, alias="period.startDate")
    period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="period.endDate")
    commuting_id: Series[pd.StringDtype] = pa.Field(coerce=True, alias="commutingId")
    pay_commuting_code: Series[pd.StringDtype] = pa.Field(coerce=True, alias="payCommuting.code")
    pay_commuting_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="payCommuting.description")
    method_of_transport_code: Series[pd.StringDtype] = pa.Field(coerce=True, alias="methodOfTransport.code")
    method_of_transport_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="methodOfTransport.description")
    distance: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, alias="distance")
    payment_percentage: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, alias="paymentPercentage")
    frequency_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="frequency.code")
    frequency_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="frequency.description")
    subscription_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="subscriptionType.code")
    subscription_type_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="subscriptionType.description")
    tariff_period_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="tariffPeriod.code")
    tariff_period_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="tariffPeriod.description")
    vehicle_is_effectively_used: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, alias="vehicleIsEffectivelyUsed")

    class Config:
        strict = False
        metadata = {"class": "AgreementCommuting", "dependencies": []}


class AgreementCustomFieldsGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v3/agreements/{agreementId}/custom-fields (segments)."""

    agreement_id: Series[pd.StringDtype] = pa.Field(coerce=True, alias="agreementId")
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, alias="period.startDate")
    period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="period.endDate")
    type: Series[pd.StringDtype] = pa.Field(coerce=True, alias="type")
    value_field_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="value.fieldName")
    value_field_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="value.fieldDescription")
    value_field_value: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="value.fieldValue")
    value_list_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="value.listDescription")

    class Config:
        strict = False
        metadata = {"class": "AgreementCustomFields", "dependencies": []}


class AgreementCostCenterAllocationGet(BrynQPanderaDataFrameModel):
    """Schema for GET /v3/agreements/{agreementId}/cost-center-allocation (items)."""

    agreement_id: Series[pd.StringDtype] = pa.Field(coerce=True, alias="agreementId")
    period_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, alias="period.startDate")
    period_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="period.endDate")
    cost_center_code: Series[pd.StringDtype] = pa.Field(coerce=True, alias="costCenterCode")
    cost_center_description: Series[pd.StringDtype] = pa.Field(coerce=True, alias="costCenterDescription")
    cost_center_accountancy: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="costCenterAccountancy")
    allocation_percentage: Series[pd.Float64Dtype] = pa.Field(coerce=True, alias="allocationPercentage")
    sequence_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, alias="sequenceNumber")
    category_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="category.code")
    category_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="category.description")
    staff_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="staffType.code")
    staff_type_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="staffType.description")
    grade_and_function_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="gradeAndFunction.code")
    grade_and_function_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="gradeAndFunction.description")
    service_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="service.code")
    service_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="service.description")
    financing_category_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="financingCategory.code")
    financing_category_description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, alias="financingCategory.description")

    class Config:
        strict = False
        metadata = {"class": "AgreementCostCenterAllocation", "dependencies": []}


# PUT Schema (Pydantic - Request)
class AgreementRemunerationBankAccountUpdate(BaseModel):
    """Schema for PUT /employee-data-management/v3/employees/agreement/{agreementId}/remuneration-bank-account endpoint"""

    iban: str = Field(..., min_length=1, max_length=34, example="BE68539007547034", description="Bank account number", alias="iban")
    bic: Optional[str] = Field(None, min_length=8, max_length=11, example="GEBABEBB", description="Bank identification code", alias="bic")

    class Config:
        populate_by_name = True


class PatchPeriodStartNotNullable(BaseModel):
    start_date: str = Field(..., alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")

    class Config:
        populate_by_name = True


class PatchPeriodNullable(BaseModel):
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")

    class Config:
        populate_by_name = True


# =========================
# Basic Information section
# =========================

class PatchOfficialEmployerDataRequest(BaseModel):
    official_joint_committee: Optional[str] = Field(None, min_length=1, max_length=7, alias="officialJointCommittee")
    nsso_prefix: Optional[str] = Field(None, min_length=1, max_length=3, alias="nssoPrefix")
    indexation_joint_committee: Optional[str] = Field(None, min_length=1, max_length=7, alias="indexationJointCommittee")
    business_unit: Optional[str] = Field(None, pattern=r"^\d{10}$", alias="businessUnit")
    point_of_operation: Optional[str] = Field(None, min_length=1, max_length=4, alias="pointOfOperation")
    multiple_points_of_operations: Optional[bool] = Field(None, alias="multiplePointsOfOperations")
    replacement_agreement_id: Optional[str] = Field(None, pattern=r"^\d{11}$", alias="replacementAgreementId")

    class Config:
        populate_by_name = True


class PatchOfficialEmployeeDataRequest(BaseModel):
    employee_type: Optional[str] = Field(None, pattern=r"^\d{2}$", alias="employeeType")
    employee_type_detail: Optional[str] = Field(None, pattern=r"^\d{2}$", alias="employeeTypeDetail")
    duration: Optional[str] = Field(None, pattern=r"^\d{2}$", alias="duration")

    class AgreementDetails(BaseModel):
        sort: Optional[str] = Field(None, pattern=r"^\d{2}$", alias="sort")
        nsso_category: Optional[str] = Field(None, pattern=r"^\d{2}$", alias="nssoCategory")
        statute: Optional[str] = Field(None, pattern=r"^\d{2}$", alias="statute")
        nsso_exemption_category: Optional[str] = Field(None, pattern=r"^\d{2}$", alias="nssoExemptionCategory")

        class Config:
            populate_by_name = True

    agreement_details: Optional[AgreementDetails] = Field(None, alias="agreementDetails", json_schema_extra={"prefix": "agreement_details_"})

    class Config:
        populate_by_name = True


class PatchOfficialApprenticeDataRequest(BaseModel):
    type: Optional[str] = Field(None, min_length=1, max_length=1, alias="type")
    community: Optional[str] = Field(None, min_length=1, max_length=1, alias="community")
    contract_term: Optional[str] = Field(None, min_length=1, max_length=2, alias="contractTerm")
    contract_number: Optional[str] = Field(None, min_length=1, max_length=15, alias="contractNumber")
    apprentice_starting_date: Optional[str] = Field(None, alias="apprenticeStartingDate")

    class Config:
        populate_by_name = True


class ContributionToSupplementaryPaymentRequest(BaseModel):
    resumption_of_work: Optional[str] = Field(None, min_length=1, max_length=1, alias="resumptionOfWork")
    first_allocation_date: Optional[str] = Field(None, alias="firstAllocationDate")
    last_allocation_date: Optional[str] = Field(None, alias="lastAllocationDate")
    notion_debtor: Optional[str] = Field(None, min_length=1, max_length=1, alias="notionDebtor")
    work_exemption: Optional[str] = Field(None, min_length=2, max_length=2, alias="workExemption")
    social_security_replacement_number: Optional[str] = Field(None, pattern=r"^\d{11}$", alias="socialSecurityReplacementNumber")

    class Config:
        populate_by_name = True


class PatchOfficialEarlyRetirementDataRequest(BaseModel):
    type: Optional[str] = Field(None, min_length=2, max_length=2, alias="type")
    early_retirement_contribution: Optional[str] = Field(None, min_length=1, max_length=1, alias="earlyRetirementContribution")
    counter_fraction_dmfa: Optional[str] = Field(None, pattern=r"^\d{1,3}(\.\d{3})?$", alias="counterFractionDmfa")
    contribution_to_supplementary_payment: Optional[ContributionToSupplementaryPaymentRequest] = Field(None, alias="contributionToSupplementaryPayment", json_schema_extra={"prefix": "contribution_to_supplementary_payment_"})

    class Config:
        populate_by_name = True


class PatchOfficialRetirementDataRequest(BaseModel):
    nihdi_code: Optional[str] = Field(None, min_length=1, max_length=1, alias="nihdiCode")
    nihdi_frequency: Optional[str] = Field(None, min_length=1, max_length=1, alias="nihdiFrequency")

    class Config:
        populate_by_name = True


class PatchAgreementRequestBasicInformation(BaseModel):
    official_employer_data: Optional[PatchOfficialEmployerDataRequest] = Field(None, alias="officialEmployerData", json_schema_extra={"prefix": "official_employer_data_"})
    official_employee_data: Optional[PatchOfficialEmployeeDataRequest] = Field(None, alias="officialEmployeeData", json_schema_extra={"prefix": "official_employee_data_"})
    apprentice: Optional[PatchOfficialApprenticeDataRequest] = Field(None, alias="apprentice", json_schema_extra={"prefix": "apprentice_"})
    early_retirement: Optional[PatchOfficialEarlyRetirementDataRequest] = Field(None, alias="earlyRetirement", json_schema_extra={"prefix": "early_retirement_"})
    retirement: Optional[PatchOfficialRetirementDataRequest] = Field(None, alias="retirement", json_schema_extra={"prefix": "retirement_"})
    c32_code: Optional[str] = Field(None, min_length=1, max_length=1, alias="c32Code")

    class Construction(BaseModel):
        c32a_current_month_number: Optional[str] = Field(None, min_length=1, max_length=13, alias="c32aCurrentMonthNumber")
        c32a_next_month_number: Optional[str] = Field(None, min_length=1, max_length=13, alias="c32aNextMonthNumber")

        class Config:
            populate_by_name = True

    construction: Optional[Construction] = Field(None, alias="construction", json_schema_extra={"prefix": "construction_"})

    class Config:
        populate_by_name = True


# ===============
# Employment part
# ===============

class PatchEmploymentRequestNotice(BaseModel):
    date_notice_served: Optional[str] = Field(None, alias="dateNoticeServed")
    notice_letter_sent_on: Optional[str] = Field(None, alias="noticeLetterSentOn")
    notice_period: Optional[PatchPeriodNullable] = Field(None, alias="noticePeriod", json_schema_extra={"prefix": "notice_period_"})
    end_disruption_period: Optional[str] = Field(None, alias="endDisruptionPeriod")

    class Config:
        populate_by_name = True


class PatchEmploymentRequestLeavingEmployment(BaseModel):
    date_end_mutual_remuneration: Optional[str] = Field(None, alias="dateEndMutualRemuneration")
    date_end_goodwill_indemnity: Optional[str] = Field(None, alias="dateEndGoodwillIndemnity")
    date_end_integration_compensation: Optional[str] = Field(None, alias="dateEndIntegrationCompensation")
    date_end_non_competition_remuneration: Optional[str] = Field(None, alias="dateEndNonCompetitionRemuneration")
    date_end_medical_force_majeure: Optional[str] = Field(None, alias="dateEndMedicalForceMajeure")

    class Config:
        populate_by_name = True


class PatchEmploymentRequestStudentQuarters(BaseModel):
    days_of_student_work_first_quarter_number: Optional[str] = Field(None, pattern=r"^\d{1,3}(\.00)?$", alias="daysOfStudentWorkFirstQuarterNumber")
    days_of_student_work_second_quarter_number: Optional[str] = Field(None, pattern=r"^\d{1,3}(\.00)?$", alias="daysOfStudentWorkSecondQuarterNumber")
    days_of_student_work_third_quarter_number: Optional[str] = Field(None, pattern=r"^\d{1,3}(\.00)?$", alias="daysOfStudentWorkThirdQuarterNumber")
    days_of_student_work_fourth_quarter_number: Optional[str] = Field(None, pattern=r"^\d{1,3}(\.00)?$", alias="daysOfStudentWorkFourthQuarterNumber")
    days_of_student_work_fifth_quarter_number: Optional[str] = Field(None, pattern=r"^\d{1,3}(\.00)?$", alias="daysOfStudentWorkFifthQuarterNumber")

    class Config:
        populate_by_name = True


class PatchEmploymentRequest(BaseModel):
    employment_period: Optional[PatchPeriodStartNotNullable] = Field(None, alias="employmentPeriod", json_schema_extra={"prefix": "employment_period_"})
    in_organisation_date: Optional[str] = Field(None, alias="inOrganisationDate")
    interim_start_date: Optional[str] = Field(None, alias="interimStartDate")
    trial_period_end_date: Optional[str] = Field(None, alias="trialPeriodEndDate")
    reason_termination: Optional[str] = Field(None, min_length=3, max_length=3, alias="reasonTermination")
    notice: Optional[PatchEmploymentRequestNotice] = Field(None, alias="notice", json_schema_extra={"prefix": "notice_"})
    leaving_employment: Optional[PatchEmploymentRequestLeavingEmployment] = Field(None, alias="leavingEmployment", json_schema_extra={"prefix": "leaving_employment_"})
    ignore_seniority_in_case_of_illness: Optional[bool] = Field(None, alias="ignoreSeniorityInCaseOfIllness")
    students_quarters: Optional[PatchEmploymentRequestStudentQuarters] = Field(None, alias="studentsQuarters", json_schema_extra={"prefix": "students_quarters_"})

    class Config:
        populate_by_name = True


# ==============
# Working Time
# ==============

class PatchWorkingTimeRequestEmploymentFraction(BaseModel):
    numerator: str = Field(..., pattern=r"^\d{1,3}\.\d{3}$", alias="numerator")
    denominator: str = Field(..., pattern=r"^\d{1,3}\.\d{3}$", alias="denominator")

    class Config:
        populate_by_name = True


class PatchFraction(BaseModel):
    numerator: Optional[str] = Field(None, pattern=r"^\d{1,3}\.\d{3}$", alias="numerator")
    denominator: Optional[str] = Field(None, pattern=r"^\d{1,3}\.\d{3}$", alias="denominator")

    class Config:
        populate_by_name = True


class PatchWorkingTimeRequestMeasure(BaseModel):
    code: Optional[str] = Field(None, min_length=3, max_length=3, alias="code")
    percent: Optional[str] = Field(None, pattern=r"^\d{1,3}\.\d{2}$", alias="percent")

    class Config:
        populate_by_name = True


class PatchReducedWorkingHoursRequest(BaseModel):
    regularity: str = Field(..., min_length=1, max_length=1, alias="regularity")
    measure: Optional[str] = Field(None, min_length=3, max_length=3, alias="measure")
    involuntary_part_time: Optional[str] = Field(None, min_length=1, max_length=1, alias="involuntaryPartTime")
    refusal_of_employment_date: Optional[str] = Field(None, alias="refusalOfEmploymentDate")
    has_progressive_work_resumption: Optional[bool] = Field(None, alias="hasProgressiveWorkResumption")
    illness_other_employer_start_date: Optional[str] = Field(None, alias="illnessOtherEmployerStartDate")
    progressive_work_resumption_type: Optional[str] = Field(None, min_length=2, max_length=2, alias="progressiveWorkResumptionType")
    adjusted_work_regime: Optional[str] = Field(None, pattern=r"^\d{1}\.\d{2}$", alias="adjustedWorkRegime")
    adjusted_work_fraction: Optional[PatchFraction] = Field(None, alias="adjustedWorkFraction", json_schema_extra={"prefix": "adjusted_work_fraction_"})
    measure1: Optional[PatchWorkingTimeRequestMeasure] = Field(None, alias="measure1", json_schema_extra={"prefix": "measure1_"})
    measure2: Optional[PatchWorkingTimeRequestMeasure] = Field(None, alias="measure2", json_schema_extra={"prefix": "measure2_"})
    full_time_absence: Optional[bool] = Field(None, alias="fullTimeAbsence")

    class Config:
        populate_by_name = True


class PatchWorkingTimeRequest(BaseModel):
    working_time_type: str = Field(..., min_length=1, max_length=1, alias="workingTimeType")
    work_schedule: Optional[str] = Field(None, min_length=1, max_length=20, alias="workSchedule")
    work_regime: str = Field(..., pattern=r"^\d{1}\.\d{2}$", alias="workRegime")
    hours_week_full_time: str = Field(..., pattern=r"^\d{2}\.\d{2}$", alias="hoursWeekFullTime")
    pay_on_annual_basis: Optional[str] = Field(None, pattern=r"^\d{1}(\.\d{4})?$", alias="payOnAnnualBasis")
    employment_fraction: PatchWorkingTimeRequestEmploymentFraction = Field(..., alias="employmentFraction", json_schema_extra={"prefix": "employment_fraction_"})
    original_employment_fraction: Optional[PatchFraction] = Field(None, alias="originalEmploymentFraction", json_schema_extra={"prefix": "original_employment_fraction_"})
    effective_employment_fraction: Optional[PatchFraction] = Field(None, alias="effectiveEmploymentFraction", json_schema_extra={"prefix": "effective_employment_fraction_"})
    time_credits: Optional[str] = Field(None, min_length=2, max_length=2, alias="timeCredits")
    exemption_type: Optional[str] = Field(None, min_length=1, max_length=2, alias="exemptionType")
    art54bis_or_ter: Optional[str] = Field(None, min_length=1, max_length=2, alias="art54bisOrTer")
    reduced_working_hours: Optional[PatchReducedWorkingHoursRequest] = Field(None, alias="reducedWorkingHours", json_schema_extra={"prefix": "reduced_working_hours_"})

    class Config:
        populate_by_name = True


# ==============
# Remuneration
# ==============

class PatchAgreementRequestGeneralRemuneration(BaseModel):
    steering_group: str = Field(..., min_length=1, max_length=4, alias="steeringGroup")
    accounting_organisation: str = Field(..., min_length=1, max_length=3, alias="accountingOrganisation")
    function: str = Field(..., min_length=1, max_length=8, alias="function")
    function_start_date: Optional[str] = Field(None, alias="functionStartDate")
    organisation: Optional[str] = Field(None, min_length=1, max_length=12, alias="organisation")
    cost_center: Optional[str] = Field(None, min_length=1, max_length=12, alias="costCenter")

    class Config:
        populate_by_name = True


class PatchAgreementRequestRemunerationPayCalculation(BaseModel):
    calculation_method: Optional[str] = Field(None, min_length=1, max_length=1, alias="calculationMethod")
    salary_split: Optional[str] = Field(None, min_length=1, max_length=1, alias="salarySplit")
    salary_qualification: Optional[str] = Field(None, min_length=1, max_length=2, alias="salaryQualification")
    adapted_holiday_pay: Optional[str] = Field(None, min_length=1, max_length=1, alias="adaptedHolidayPay")
    financing_code: Optional[str] = Field(None, min_length=1, max_length=3, alias="financingCode")
    payment_scheme: Optional[str] = Field(None, min_length=1, max_length=8, alias="paymentScheme")

    class Tip(BaseModel):
        type: Optional[str] = Field(None, min_length=1, max_length=1, alias="type")
        professional_role: Optional[str] = Field(None, min_length=2, max_length=2, alias="professionalRole")

        class Config:
            populate_by_name = True

    tip: Optional[Tip] = Field(None, alias="tip", json_schema_extra={"prefix": "tip_"})
    seniority_date: Optional[str] = Field(None, alias="seniorityDate")
    sector_seniority_date: Optional[str] = Field(None, alias="sectorSeniorityDate")
    internal_seniority_date: Optional[str] = Field(None, alias="internalSeniorityDate")
    position_seniority_date: Optional[str] = Field(None, alias="positionSeniorityDate")
    remuneration_fraction: Optional[PatchFraction] = Field(None, alias="remunerationFraction", json_schema_extra={"prefix": "remuneration_fraction_"})
    statutory_retirement_date: Optional[str] = Field(None, alias="statutoryRetirementDate")
    contribution_second_retirement_pillar: Optional[str] = Field(None, min_length=1, max_length=1, alias="contributionSecondRetirementPillar")
    wage_category: Optional[str] = Field(None, min_length=4, max_length=4, alias="wageCategory")

    class Config:
        populate_by_name = True


class PatchAgreementRequestPayScale(BaseModel):
    use_pay_scale: bool = Field(..., alias="usePayScale")
    type: Optional[str] = Field(None, min_length=1, max_length=1, alias="type")
    pay_scale_selection: Optional[str] = Field(None, min_length=1, max_length=9, alias="payScaleSelection")
    experience: Optional[str] = Field(None, alias="experience")
    pay_grade: Optional[str] = Field(None, min_length=1, max_length=1, alias="payGrade")
    level: Optional[str] = Field(None, min_length=1, max_length=1, alias="level")

    class IficNullable(BaseModel):
        useIFIC: Optional[bool] = Field(None, alias="useIFIC")
        useScale: Optional[bool] = Field(None, alias="useScale")

        class Seniority(BaseModel):
            year_number: Optional[str] = Field(None, min_length=1, max_length=2, alias="yearNumber")
            month_number: Optional[str] = Field(None, min_length=1, max_length=2, alias="monthNumber")

            class Config:
                populate_by_name = True

        seniority: Optional[Seniority] = Field(None, alias="seniority", json_schema_extra={"prefix": "seniority_"})
        salary_scale_number: Optional[str] = Field(None, min_length=1, max_length=9, alias="salaryScaleNumber")

        class RemFrac(BaseModel):
            numerator: Optional[str] = Field(None, pattern=r"^\d{1,3}(\.\d{3})?$", alias="numerator")
            denominator: Optional[str] = Field(None, pattern=r"^\d{1,3}(\.\d{3})?$", alias="denominator")

            class Config:
                populate_by_name = True

        remuneration_fraction: Optional[RemFrac] = Field(None, alias="remunerationFraction", json_schema_extra={"prefix": "remuneration_fraction_"})
        function: Optional[str] = Field(None, min_length=4, max_length=4, alias="function")

        class HybridFunction(BaseModel):
            code: Optional[str] = Field(None, min_length=1, max_length=4, alias="code")
            number: Optional[str] = Field(None, min_length=1, max_length=9, alias="number")

            class HybridFraction(BaseModel):
                numerator: Optional[str] = Field(None, pattern=r"^\d{1,3}(\.\d{3})?$", alias="numerator")
                denominator: Optional[str] = Field(None, pattern=r"^\d{1,3}(\.\d{3})?$", alias="denominator")

                class Config:
                    populate_by_name = True

            fraction: Optional[HybridFraction] = Field(None, alias="fraction", json_schema_extra={"prefix": "fraction_"})

            class Config:
                populate_by_name = True

        hybridFunction_1: Optional[HybridFunction] = Field(None, alias="hybridFunction_1", json_schema_extra={"prefix": "hybrid_function_1_"})
        hybridFunction_2: Optional[HybridFunction] = Field(None, alias="hybridFunction_2", json_schema_extra={"prefix": "hybrid_function_2_"})
        hybridFunction_3: Optional[HybridFunction] = Field(None, alias="hybridFunction_3", json_schema_extra={"prefix": "hybrid_function_3_"})

        class Config:
            populate_by_name = True

    ific: Optional[IficNullable] = Field(None, alias="ific", json_schema_extra={"prefix": "ific_"})

    class Config:
        populate_by_name = True


class PatchBankAccounts(BaseModel):
    main_account: Optional[str] = Field(None, min_length=1, max_length=34, alias="mainAccount")
    second_account: Optional[str] = Field(None, min_length=1, max_length=34, alias="secondAccount")

    class Config:
        populate_by_name = True


class PatchAgreementRequestRemunerationMethodOfPayment(BaseModel):
    type: str = Field(..., min_length=1, max_length=1, alias="type")
    employee_bank_accounts: Optional[PatchBankAccounts] = Field(None, alias="employeeBankAccounts", json_schema_extra={"prefix": "employee_bank_accounts_"})
    employer_bank_accounts: Optional[PatchBankAccounts] = Field(None, alias="employerBankAccounts", json_schema_extra={"prefix": "employer_bank_accounts_"})

    class Config:
        populate_by_name = True


class PatchAgreementRequestRemunerationInsuranceDetails(BaseModel):
    work_accident_insurance_number: Optional[str] = Field(None, min_length=1, max_length=15, alias="workAccidentInsuranceNumber")
    work_accident_insurance_policy_number: Optional[str] = Field(None, min_length=1, max_length=15, alias="workAccidentInsurancePolicyNumber")
    has_groups_insurance: Optional[bool] = Field(None, alias="hasGroupsInsurance")
    group_insurance_number: Optional[str] = Field(None, min_length=1, max_length=15, alias="groupInsuranceNumber")
    group_insurance_policy_number: Optional[str] = Field(None, min_length=1, max_length=15, alias="groupInsurancePolicyNumber")
    other_insurance_number: Optional[str] = Field(None, min_length=1, max_length=15, alias="otherInsuranceNumber")
    other_insurance_policy_number: Optional[str] = Field(None, min_length=1, max_length=15, alias="otherInsurancePolicyNumber")
    has_hospital_insurance: Optional[bool] = Field(None, alias="hasHospitalInsurance")
    has_hospital_insurance_for_spouse: Optional[bool] = Field(None, alias="hasHospitalInsuranceForSpouse")

    class Config:
        populate_by_name = True


class PatchAgreementRequestRemuneration(BaseModel):
    general_remuneration: Optional[PatchAgreementRequestGeneralRemuneration] = Field(None, alias="generalRemuneration", json_schema_extra={"prefix": "general_remuneration_"})
    pay_calculation: Optional[PatchAgreementRequestRemunerationPayCalculation] = Field(None, alias="payCalculation", json_schema_extra={"prefix": "pay_calculation_"})
    pay_scale: Optional[PatchAgreementRequestPayScale] = Field(None, alias="payScale", json_schema_extra={"prefix": "pay_scale_"})
    method_of_payment: Optional[PatchAgreementRequestRemunerationMethodOfPayment] = Field(None, alias="methodOfPayment", json_schema_extra={"prefix": "method_of_payment_"})
    insurance_details: Optional[PatchAgreementRequestRemunerationInsuranceDetails] = Field(None, alias="insuranceDetails", json_schema_extra={"prefix": "insurance_details_"})

    class Config:
        populate_by_name = True


# ========================
# Recruitment Incentives
# ========================

class RecruitmentFrameworkNullable(BaseModel):
    code: Optional[str] = Field(None, min_length=3, max_length=3, alias="code")
    start_date: Optional[str] = Field(None, alias="startDate")

    class Config:
        populate_by_name = True


class PatchAgreementRecruitmentIncentives(BaseModel):
    employee_recruitment_framework: Optional[RecruitmentFrameworkNullable] = Field(None, alias="employeeRecruitmentFramework", json_schema_extra={"prefix": "employee_recruitment_framework_"})
    employer_recruitment_framework: Optional[RecruitmentFrameworkNullable] = Field(None, alias="employerRecruitmentFramework", json_schema_extra={"prefix": "employer_recruitment_framework_"})
    regional_recruitment_framework: Optional[RecruitmentFrameworkNullable] = Field(None, alias="regionalRecruitmentFramework", json_schema_extra={"prefix": "regional_recruitment_framework_"})
    number_of_balance_months_work_benefit: Optional[str] = Field(None, pattern=r"^(0|[1-9][0-9]?)$", alias="numberOfBalanceMonthsWorkBenefit")
    gesco_number: Optional[str] = Field(None, min_length=1, max_length=9, alias="gescoNumber")
    career_measure: Optional[str] = Field(None, min_length=2, max_length=2, alias="careerMeasure")
    start_job: Optional[str] = Field(None, min_length=2, max_length=2, alias="startJob")
    restructuring_or_difficulties: Optional[str] = Field(None, min_length=1, max_length=1, alias="restructuringOrDifficulties")
    other_social_services: Optional[str] = Field(None, min_length=2, max_length=2, alias="otherSocialServices")
    research_percent: Optional[str] = Field(None, pattern=r"^\d{1,3}(\.\d{2})?$", alias="researchPercent")
    aid_zone: Optional[str] = Field(None, min_length=1, max_length=1, alias="aidZone")

    class Config:
        populate_by_name = True


# =======
# Sector
# =======

class SocialProfitNumberOfWorkTimeNullable(BaseModel):
    numerator: Optional[str] = Field(None, pattern=r"^(0|[1-9][0-9]?)$", alias="numerator")
    denominator: Optional[str] = Field(None, pattern=r"^(10|11|12)$", alias="denominator")

    class Config:
        populate_by_name = True


class PatchAgreementRequestSectorSocialProfit(BaseModel):
    status_target_group: Optional[str] = Field(None, min_length=1, max_length=1, alias="statusTargetGroup")
    supervision_intensity_code: Optional[str] = Field(None, min_length=1, max_length=1, alias="supervisionIntensityCode")
    wage_bonus_percent: Optional[float] = Field(None, alias="wageBonusPercent")
    is_weak_employee: Optional[bool] = Field(None, alias="isWeakEmployee")
    supervisor_qualification: Optional[str] = Field(None, min_length=2, max_length=2, alias="supervisorQualification")
    occupational_class: Optional[str] = Field(None, min_length=1, max_length=1, alias="occupationalClass")
    employee_qualification: Optional[str] = Field(None, min_length=2, max_length=2, alias="employeeQualification")
    financing: Optional[str] = Field(None, min_length=3, max_length=3, alias="financing")
    rob_particular_competence_code: Optional[str] = Field(None, min_length=1, max_length=1, alias="robParticularCompetenceCode")
    staff_type: Optional[str] = Field(None, min_length=1, max_length=1, alias="staffType")
    nihdi_number: Optional[str] = Field(None, pattern=r"^\d{11}$", alias="nihdiNumber")
    specialism: Optional[str] = Field(None, min_length=1, max_length=3, alias="specialism")
    recognition_year: Optional[str] = Field(None, pattern=r"^\d{4}$", alias="recognitionYear")
    additional_qualification: Optional[str] = Field(None, min_length=1, max_length=2, alias="additionalQualification")
    qualification_year: Optional[str] = Field(None, pattern=r"^\d{4}$", alias="qualificationYear")
    campus: Optional[str] = Field(None, min_length=1, max_length=5, alias="campus")
    hospital_statute: Optional[str] = Field(None, min_length=1, max_length=1, alias="hospitalStatute")
    number_of_work_time: Optional[SocialProfitNumberOfWorkTimeNullable] = Field(None, alias="numberOfWorkTime", json_schema_extra={"prefix": "number_of_work_time_"})
    has_private_practice: Optional[bool] = Field(None, alias="hasPrivatePractice")
    localisation: Optional[str] = Field(None, pattern=r"^\d{4}$", alias="localisation")

    class Policlinic(BaseModel):
        belongs_to_the_own_hospital: Optional[bool] = Field(None, alias="belongsToTheOwnHospital")
        belongs_to_another_hospital: Optional[bool] = Field(None, alias="belongsToAnotherHospital")
        belongs_not_to_hospital: Optional[bool] = Field(None, alias="belongsNotToHospital")

        class Config:
            populate_by_name = True

    policlinic: Optional[Policlinic] = Field(None, alias="policlinic", json_schema_extra={"prefix": "policlinic_"})
    service_activity: Optional[str] = Field(None, min_length=1, max_length=1, alias="serviceActivity")
    distinguishing_letter: Optional[str] = Field(None, min_length=1, max_length=7, alias="distinguishingLetter")
    hospital_particular_competence: Optional[str] = Field(None, min_length=1, max_length=1, alias="hospitalParticularCompetence")
    hospital_organisation_number: Optional[str] = Field(None, min_length=1, max_length=12, alias="hospitalOrganisationNumber")
    physical_department_name: Optional[str] = Field(None, min_length=1, max_length=35, alias="physicalDepartmentName")
    not_medical_registration_zone: Optional[str] = Field(None, min_length=1, max_length=50, alias="notMedicalRegistrationZone")
    nursing_unit_name: Optional[str] = Field(None, min_length=1, max_length=50, alias="nursingUnitName")
    diploma: Optional[str] = Field(None, min_length=1, max_length=4, alias="diploma")

    class Config:
        populate_by_name = True


class PatchAgreementRequestSectorTransport(BaseModel):
    wage_system: Optional[str] = Field(None, min_length=1, max_length=1, alias="wageSystem")

    class Config:
        populate_by_name = True


class PatchAgreementRequestSectorPublicHospital(BaseModel):
    unemployment: Optional[PatchPeriodNullable] = Field(None, alias="unemployment", json_schema_extra={"prefix": "unemployment_"})
    illness: Optional[PatchPeriodNullable] = Field(None, alias="illness", json_schema_extra={"prefix": "illness_"})

    class SickLeaveReserveNullable(BaseModel):
        anniversary_date: Optional[str] = Field(None, alias="anniversaryDate")
        system: Optional[str] = Field(None, min_length=1, max_length=1, alias="system")

        class Config:
            populate_by_name = True

    sick_leave_reserve: Optional[SickLeaveReserveNullable] = Field(None, alias="sickLeaveReserve", json_schema_extra={"prefix": "sick_leave_reserve_"})

    class CapeloNullable(BaseModel):
        has_exception_obligation: Optional[bool] = Field(None, alias="hasExceptionObligation")
        service_type: Optional[str] = Field(None, min_length=1, max_length=1, alias="serviceType")
        institution_type: Optional[str] = Field(None, min_length=1, max_length=2, alias="institutionType")
        function: Optional[str] = Field(None, min_length=1, max_length=1, alias="function")
        staff_category: Optional[str] = Field(None, min_length=1, max_length=4, alias="staffCategory")
        pdos_name: Optional[str] = Field(None, min_length=1, max_length=12, alias="pdosName")
        grade: Optional[str] = Field(None, min_length=1, max_length=8, alias="grade")

        class Config:
            populate_by_name = True

    capelo: Optional[CapeloNullable] = Field(None, alias="capelo", json_schema_extra={"prefix": "capelo_"})

    class Config:
        populate_by_name = True


class PatchAgreementRequestSector(BaseModel):
    social_profit: Optional[PatchAgreementRequestSectorSocialProfit] = Field(None, alias="socialProfit", json_schema_extra={"prefix": "social_profit_"})
    transport: Optional[PatchAgreementRequestSectorTransport] = Field(None, alias="transport", json_schema_extra={"prefix": "transport_"})
    public_hospital: Optional[PatchAgreementRequestSectorPublicHospital] = Field(None, alias="publicHospital", json_schema_extra={"prefix": "public_hospital_"})

    class Config:
        populate_by_name = True


# ============================
# Declarations (OfficialEmployee)
# ============================

class PatchWithHoldingTaxRequest(BaseModel):
    tax_type: str = Field(..., min_length=1, max_length=2, alias="taxType")
    declaration: Optional[str] = Field(None, min_length=1, max_length=1, alias="declaration")
    cross_border_worker: Optional[str] = Field(None, min_length=1, max_length=1, alias="crossBorderWorker")
    gross_net_contraction: str = Field(..., min_length=1, max_length=2, alias="grossNetContraction")

    class Config:
        populate_by_name = True


class PatchOfficialEmployeeDataNSSO(BaseModel):
    work_place_accident_risk_category: Optional[str] = Field(None, min_length=1, max_length=3, alias="workPlaceAccidentRiskCategory")
    nsso_notion: Optional[str] = Field(None, min_length=1, max_length=2, alias="nssoNotion")
    disabled_for_nsso: Optional[bool] = Field(None, alias="disabledForNsso")
    custom_work_type_code: Optional[str] = Field(None, min_length=1, max_length=1, alias="customWorkTypeCode")

    class Config:
        populate_by_name = True


class PatchOfficialEmployeeDataRequestDeclarations(BaseModel):
    with_holding_tax: Optional[PatchWithHoldingTaxRequest] = Field(None, alias="withHoldingTax", json_schema_extra={"prefix": "with_holding_tax_"})
    tax_statute: Optional[str] = Field(None, min_length=1, max_length=2, alias="taxStatute")
    nsso: Optional[PatchOfficialEmployeeDataNSSO] = Field(None, alias="nsso", json_schema_extra={"prefix": "nsso_"})
    transport_costs_fully_taxed: Optional[bool] = Field(None, alias="transportCostsFullyTaxed")
    maribel: Optional[dict] = Field(None, alias="maribel")
    social_balance: Optional[bool] = Field(None, alias="socialBalance")
    via: Optional[str] = Field(None, min_length=1, max_length=5, alias="via")
    nace: Optional[str] = Field(None, min_length=1, max_length=5, alias="nace")
    pension_system: Optional[str] = Field(None, min_length=1, max_length=2, alias="pensionSystem")
    nsso_function: Optional[str] = Field(None, min_length=1, max_length=4, alias="nssoFunction")
    deviating_pension_calculation: Optional[bool] = Field(None, alias="deviatingPensionCalculation")
    measure_non_profit: Optional[str] = Field(None, min_length=1, max_length=2, alias="measureNonProfit")
    illness6_months_date: Optional[str] = Field(None, alias="illness6MonthsDate")

    class Config:
        populate_by_name = True


# =============================
# ROOT: Patch Agreement Request
# =============================

class PatchAgreementRequest(BaseModel):
    """Schema for PATCH /v3/agreements/{agreementId}."""
    from_date: str = Field(..., alias="fromDate")

    basic_information: Optional[PatchAgreementRequestBasicInformation] = Field(None, alias="basicInformation", json_schema_extra={"prefix": "basic_information_"})
    employment: Optional[PatchEmploymentRequest] = Field(None, alias="employment", json_schema_extra={"prefix": "employment_"})
    working_time: Optional[PatchWorkingTimeRequest] = Field(None, alias="workingTime", json_schema_extra={"prefix": "working_time_"})
    remuneration: Optional[PatchAgreementRequestRemuneration] = Field(None, alias="remuneration", json_schema_extra={"prefix": "remuneration_"})
    recruitment_incentives: Optional[PatchAgreementRecruitmentIncentives] = Field(None, alias="recruitmentIncentives", json_schema_extra={"prefix": "recruitment_incentives_"})
    sector: Optional[PatchAgreementRequestSector] = Field(None, alias="sector", json_schema_extra={"prefix": "sector_"})
    declarations: Optional[PatchOfficialEmployeeDataRequestDeclarations] = Field(None, alias="declarations", json_schema_extra={"prefix": "declarations_"})

    class Config:
        populate_by_name = True
