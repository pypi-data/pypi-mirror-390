#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates CSAM into RegScale"""

# standard python imports
import logging
from typing import List, Optional
from rich.progress import track
import click
from rich.console import Console
from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.utils.date import format_to_regscale_iso, date_obj
from regscale.core.app.utils.app_utils import error_and_exit, filter_list
from regscale.models.regscale_models import (
    Organization,
    SecurityPlan,
    User,
)
from regscale.models.regscale_models.module import Module
from regscale.models.regscale_models.form_field_value import FormFieldValue
from regscale.integrations.public.csam.csam_poam import import_csam_poams
from regscale.integrations.public.csam.csam_controls import (
    import_csam_controls,
    set_inheritable,
    import_csam_inheritance,
)
from regscale.integrations.public.csam.csam_agency_defined import update_ssp_agency_details
from regscale.integrations.public.csam.csam_common import (
    retrieve_ssps_custom_form_map,
    retrieve_custom_form_ssps_map,
    retrieve_from_csam,
    set_custom_fields,
    fix_form_field_value,
    CSAM_FIELD_NAME,
    FISMA_FIELD_NAME,
    SSP_BASIC_TAB,
)


logger = logging.getLogger("regscale")
console = Console()

####################################################################################################
#
# IMPORT SSP / POAM FROM DoJ's CSAM GRC
# CSAM API Docs: https://csam.dhs.gov/CSAM/api/docs/index.html (required PIV)
#
####################################################################################################


SSP_SYSTEM_TAB = "System Information"
SSP_FINANCIAL_TAB = "Financial Info"
SSP_PRIVACY_TAB = "Privacy-Details"
SSP_CONTINGENCY_TAB = "Continuity and Incident Response"

CUSTOM_FIELDS_BASIC_LIST = [
    "acronym",
    "Classification",
    "FISMA Reportable",
    "Contractor System",
    "Authorization Process",
    "ATO Date",
    "ATO Status",
    "Critical Infrastructure",
    "Mission Essential",
    "uiiCode",
    "HVA Identifier",
    "External Web Interface",
    "CFO Designation",
    "Law Enforcement Sensitive",
    CSAM_FIELD_NAME,
    FISMA_FIELD_NAME,
]


@click.group()
def csam():
    """Integrate CSAM."""


@csam.command(name="import_ssp")
def import_ssp():
    """
    Import SSP from CSAM
    Into RegScale
    """

    import_csam_ssp()


@csam.command(name="import_poam")
def import_poam():
    """
    Import POAMS from CSAM
    Into RegScale
    """

    import_csam_poams()


def import_csam_ssp():
    """
    Import SSPs from CSAM
    Into RegScale
    According to a filter in init.yaml
    """

    logger.info("Gathering reference info...")
    # Check Custom Fields exist
    custom_fields_basic_map = FormFieldValue.check_custom_fields(
        CUSTOM_FIELDS_BASIC_LIST, "securityplans", SSP_BASIC_TAB
    )

    # Get a map of existing custom forms
    ssp_map = retrieve_custom_form_ssps_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[FISMA_FIELD_NAME]
    )

    # Get a list of orgs and create a map to id
    orgs = Organization.get_list()
    org_map = {org.name: org.id for org in orgs}

    # Grab the data from CSAM
    app = Application()
    csam_filter = app.config.get("csamFilter", None)

    logger.info("Retrieving systems from CSAM...")
    results = retrieve_from_csam(
        csam_endpoint="/CSAM/api/v1/systems",
    )

    if not results:
        error_and_exit("Failure to retrieve plans from CSAM")
    else:
        logger.info("Retrieved plans from CSAM, parsing results...")

    results = filter_list(results, csam_filter)
    if not results:
        error_and_exit(
            "No results match filter in CSAM. \
                       Please check your CSAM configuration."
        )

    logger.info("Importing systems... ")
    # Parse the results
    updated_ssps = []
    updated_ssps = save_ssp_front_matter(
        results=results,
        ssp_map=ssp_map,
        custom_fields_basic_map=custom_fields_basic_map,
        org_map=org_map,
    )

    # Now have to get the system details for each system
    update_ssp_agency_details(updated_ssps, custom_fields_basic_map)

    # Import the authorization process and status
    import_csam_authorization(import_ids=[ssp.id for ssp in updated_ssps])

    # Import the Privacy date
    import_csam_privacy_info(import_ids=[ssp.id for ssp in updated_ssps])

    # Import the Contingency & IR data
    import_csam_contingency(import_ids=[ssp.id for ssp in updated_ssps])

    # Import the controls
    import_csam_controls(import_ids=[ssp.id for ssp in updated_ssps])

    # Set inheritance if system type = program
    for result in results:
        if result.get("systemType") == "Program":
            # Get the RegScale SSP Id
            program_id = ssp_map.get(result["externalId"])
            if not program_id:
                logger.error(
                    f"Could not find RegScale SSP for CSAM id: {result['externalId']}. \
                    Please create or import the Security Plan prior to importing inheritance."
                )
                continue

            # Set the inheritable flag
            set_inheritable(regscale_id=program_id)

    # Import the Inheritance
    import_csam_inheritance(import_ids=[ssp.id for ssp in updated_ssps])

    # Import the POCs
    import_csam_pocs(import_ids=[ssp.id for ssp in updated_ssps])


def sync_csam_ssps():

    logger.info("Gathering reference info...")
    # Check Custom Fields exist
    custom_fields_basic_map = FormFieldValue.check_custom_fields(
        CUSTOM_FIELDS_BASIC_LIST, "securityplans", SSP_BASIC_TAB
    )

    # Get a map of existing custom forms
    ssp_map = retrieve_custom_form_ssps_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[FISMA_FIELD_NAME]
    )
    csam_map = retrieve_custom_form_ssps_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[CSAM_FIELD_NAME]
    )

    # Get a list of orgs and create a map to id
    orgs = Organization.get_list()
    org_map = {org.name: org.id for org in orgs}

    csam_list = []
    for id in csam_map.keys():
        csam_list.append(int(id))
    csam_filter = {"id": csam_list}

    logger.info("Retrieving systems from CSAM...")
    results = retrieve_from_csam(
        csam_endpoint="/CSAM/api/v1/systems",
    )

    results = filter_list(results, csam_filter)

    logger.info("Syncing systems... ")
    # Parse the results
    updated_ssps = []
    updated_ssps = save_ssp_front_matter(
        results=results,
        ssp_map=ssp_map,
        custom_fields_basic_map=custom_fields_basic_map,
        org_map=org_map,
    )

    # Now have to get the system details for each system
    update_ssp_agency_details(updated_ssps, custom_fields_basic_map)

    # Import the authorization process and status
    import_csam_authorization(import_ids=[ssp.id for ssp in updated_ssps])

    # Import the Privacy date
    import_csam_privacy_info(import_ids=[ssp.id for ssp in updated_ssps])

    # Import the Contingency & IR data
    import_csam_contingency(import_ids=[ssp.id for ssp in updated_ssps])


def import_csam_pocs(import_ids: Optional[List[int]] = None):
    """
    Import the Points of Contact from CSAM
    Into RegScale
    """
    custom_fields_pocs_list = [
        "Certifying Official",
        "Alternate Information System Security Manager",
        "Alternate Information System Security Officer",
    ]
    # Check Custom Fields exist
    custom_fields_pocs_map = FormFieldValue.check_custom_fields(
        custom_fields_pocs_list, "securityplans", "Points of Contact"
    )

    # Get existing ssps by CSAM Id
    custom_fields_basic_map = FormFieldValue.check_custom_fields([CSAM_FIELD_NAME], "securityplans", SSP_BASIC_TAB)
    ssp_map = retrieve_ssps_custom_form_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[CSAM_FIELD_NAME]
    )

    plans = import_ids if import_ids else list(ssp_map.keys())

    # Get a list of users and create a map to id
    users = User.get_all()
    user_map = {user.userName: user.id for user in users}

    # TO DO... Add the rest of the logic
    # Delete these lines: Added to shut up sonarqube
    logger.debug(f"Custom Fields Map: {custom_fields_pocs_map}, User Map: {user_map}")
    logger.debug(f"SSP Map: {ssp_map}, Plans: {plans}")


def import_csam_privacy_info(import_ids: Optional[List[int]] = None):
    """
    Import the Privacy Info from CSAM
    Into RegScale
    """

    # Get existing ssps by CSAM Id
    custom_fields_basic_map = FormFieldValue.check_custom_fields([CSAM_FIELD_NAME], "securityplans", SSP_BASIC_TAB)
    ssp_map = retrieve_ssps_custom_form_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[CSAM_FIELD_NAME]
    )

    ssps = import_ids if import_ids else list(ssp_map.keys())

    updated_ssps = []
    if len(ssps) == 0:
        return
    for index in track(
        range(len(ssps)),
        description=f"Importing {len(ssps)} SSP privacy...",
    ):
        ssp = ssps[index]
        system_id = ssp_map.get(ssp)
        if not system_id:
            logger.error(f"Could not find CSAM ID for SSP id: {ssp}")
            continue
        else:
            updated_ssps.append(ssp)

        result = retrieve_from_csam(csam_endpoint=f"/CSAM/api/v1/systems/{system_id}/privacy")
        if len(result) == 0:
            logger.error(f"Could not retrieve privacy for CSAM ID {system_id}. RegScale SSP id: {ssp}")
            continue

        pia_date = result.get("privacyImpactAssessmentDateCompleted")
        pta_date = result.get("privacyThresholdAnalysisDateCompleted")

        # Get SORN Status
        result = retrieve_from_csam(
            csam_endpoint=f"/CSAM/api/v1/systems/{system_id}/sorn",
        )
        if len(result) == 0:
            logger.debug(f"Could not retrieve SORN for CSAM ID {system_id}. RegScale SSP id: {ssp}")
            continue
        sorn_date = 0
        sorn_id = ""
        for sorn_status in result:
            if date_obj(sorn_status.get("publishedDate")) > date_obj(sorn_date):
                sorn_date = sorn_status.get("publishedDate")
                sorn_id = sorn_status.get("systemOfRecordsNoticeId").strip()

        # Set the records
        record = {"pia_date": pia_date, "pta_date": pta_date, "sorn_date": sorn_date, "sorn_id": sorn_id}
        save_privacy_records(regscale_id=ssp, record=record)

        logger.info(f"Updated {len(updated_ssps)} Security Plans with privacy data")


def save_privacy_records(regscale_id: int, record: dict):

    custom_fields_privacy_list = ["PIA Date", "PTA Date", "SORN Date", "SORN Id"]

    # Check for custom fields
    custom_fields_map = FormFieldValue.check_custom_fields(custom_fields_privacy_list, "securityplans", SSP_PRIVACY_TAB)

    privacy_fields = []
    if record.get("pia_date"):
        privacy_fields.append(
            {
                "record_id": regscale_id,
                "record_module": "securityplans",
                "form_field_id": custom_fields_map["PIA Date"],
                "field_value": format_to_regscale_iso(record.get("pia_date")),
            }
        )
    if record.get("pta_date"):
        privacy_fields.append(
            {
                "record_id": regscale_id,
                "record_module": "securityplans",
                "form_field_id": custom_fields_map["PTA Date"],
                "field_value": format_to_regscale_iso(record.get("pta_date")),
            }
        )
    if record.get("sorn_date"):
        privacy_fields.append(
            {
                "record_id": regscale_id,
                "record_module": "securityplans",
                "form_field_id": custom_fields_map["SORN Date"],
                "field_value": format_to_regscale_iso(record.get("sorn_date")),
            }
        )
    if record.get("sorn_id"):
        privacy_fields.append(
            {
                "record_id": regscale_id,
                "record_module": "securityplans",
                "form_field_id": custom_fields_map["SORN Id"],
                "field_value": str(record.get("sorn_id")),
            }
        )
    if len(privacy_fields) > 0:
        privacy_fields = fix_form_field_value(privacy_fields)
        FormFieldValue.save_custom_fields(privacy_fields)


def import_csam_authorization(import_ids: Optional[List[int]] = None):
    """
    Update the Authorization of the SSPs
    This requires a call to the /system/{id}/securityauthorization
    endpoint

    :param list import_ids: Filtered list of SSPs
    :return: None
    """
    # Get existing ssps by CSAM Id
    custom_fields_basic_map = FormFieldValue.check_custom_fields([CSAM_FIELD_NAME], "securityplans", SSP_BASIC_TAB)
    ssp_map = retrieve_ssps_custom_form_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[CSAM_FIELD_NAME]
    )

    ssps = import_ids if import_ids else list(ssp_map.keys())

    updated_ssps = []
    field_values = []
    if len(ssps) == 0:
        return
    for index in track(
        range(len(ssps)),
        description=f"Importing {len(ssps)} SSP authorization...",
    ):
        ssp = ssps[index]
        csam_id = ssp_map.get(ssp)
        if not csam_id:
            logger.error(f"Could not find CSAM ID for SSP id: {ssp}")
            continue
        else:
            updated_ssps.append(ssp)

        result = retrieve_from_csam(
            csam_endpoint=f"/CSAM/api/v1/systems/{csam_id}/securityauthorization",
        )
        if len(result) == 0:
            logger.error(f"Could not retrieve details for CSAM ID {csam_id}. RegScale SSP id: {ssp}")
            continue
        # Set the authorization expiration date
        ssp_obj = SecurityPlan.get_object(object_id=ssp)
        if ssp_obj:
            ssp_obj.authorizationTerminationDate = result.get("authorizationExpirationDate")
            ssp_obj.save()
        else:
            logger.debug(f"Failed to retrieve Security Plan id: {ssp}")
        # Get the custom fields
        field_values.append(
            {
                "record_id": ssp,
                "record_module": "securityplans",
                "form_field_id": custom_fields_basic_map["Authorization Process"],
                "field_value": str(result.get("authorizationProcess")),
            }
        )
        field_values.append(
            {
                "record_id": ssp,
                "record_module": "securityplans",
                "form_field_id": custom_fields_basic_map["ATO Date"],
                "field_value": str(result.get("lastAuthorizationDate")),
            }
        )
        field_values.append(
            {
                "record_id": ssp,
                "record_module": "securityplans",
                "form_field_id": custom_fields_basic_map["ATO Status"],
                "field_value": str(result.get("authorizationStatus")),
            }
        )
    # Save the Custom Fields
    if len(field_values) > 0:
        field_values = fix_form_field_value(field_values)
        FormFieldValue.save_custom_fields(field_values)

    logger.info(f"Updated {len(updated_ssps)} Security Plans with authorization data")


def import_csam_contingency(import_ids: Optional[List[int]] = None):
    """
    Update the Contingency & IR of the SSPs
    This requires a call to the /systems/<system_id>/continuityresponse
    endpoint

    :param list import_ids: Filtered list of SSPs
    :return: None
    """
    # Continuity & IR Fields
    # Goes to "Continuity and Incident Response" Tab
    # /CSAM/api/v1/systems/<system_id>/continuityresponse
    continuity_map = {
        "maximumTolerableDowntime": "MTD",
        "recoveryTimeObjective": "RTO",
        "recoveryPointObjective": "RPO",
        "businessImpactAnalysisDateCompleted": "BIA Completed",
        "businessImpactAnalysisNextDueDate": "BIA Next Due Date",
        "contingencyPlanDateCompleted": "CP Completed",
        "contingencyPlanNextDueDate": "CP Next Due Date",
        "contingencyPlanTrainingDateCompleted": "CP Training Completed",
        "contingencyPlanTrainingNextDueDate": "CP Training Next Due Date",
        "contingencyPlanTestNextDueDate": "CP Test Next Due Date",
        "incidentResponsePlanDateCompleted": "IRP Completed",
        "incidentResponsePlanNextDueDate": "IRP Next Due Date",
        "incidentResponsePlanTrainingDateCompleted": "IRP Training Completed",
        "incidentResponsePlanTrainingNextDueDate": "IRP Training Next Due Date",
        "incidentResponsePlanTestNextDueDate": "IRP Test Next Due Date",
    }

    # /CSAM/api/v1/systems/<system_id>/continuitytest
    # testItem == "Contingency Plan (CP)""
    continuity_test_map = {"testType": "CP Test Type", "dateTested": "CP Date Tested", "outcome": "CP Test Outcome"}
    # testItem == "Incident Response Plan (IRP)"
    irp_test_map = {"testType": "IRP Test Type", "dateTested": "IRP Date Tested", "outcome": "IRP Test Outcome"}

    # /CSAM/api/v1/systems/{system_id}/additionalstatus
    # name == "Contingency Plan Review"
    contingency_plan_map = {
        "dateCompleted": "CPR Completed",
        "nextDueDate": "CPR Next Due Date",
        "expirationDate": "CPR Expiration Date",
    }
    continuity_ir_fields = []
    continuity_ir_fields = continuity_ir_fields + list(continuity_map.values())
    continuity_ir_fields = continuity_ir_fields + list(continuity_test_map.values())
    continuity_ir_fields = continuity_ir_fields + list(irp_test_map.values())
    continuity_ir_fields = continuity_ir_fields + list(contingency_plan_map.values())
    continuity_ir_fields_map = FormFieldValue.check_custom_fields(
        continuity_ir_fields, "securityplans", "Continuity and Incident Response"
    )

    # name == "Document Review Approval"
    # goes to "Document Review" Tab
    doc_approv_map = {
        "dateCompleted": "Doc Review Completed",
        "nextDueDate": "Doc Review Next Due Date",
        "expirationDate": "Doc Review Expiration Date",
    }
    doc_approv_fields = list(doc_approv_map.values())
    doc_approv_fields_map = FormFieldValue.check_custom_fields(doc_approv_fields, "securityplans", "Document Review")

    # Get existing ssps by CSAM Id
    custom_fields_basic_map = FormFieldValue.check_custom_fields([CSAM_FIELD_NAME], "securityplans", SSP_BASIC_TAB)
    ssp_map = retrieve_ssps_custom_form_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[CSAM_FIELD_NAME]
    )

    ssps = import_ids if import_ids else list(ssp_map.keys())

    updated_ssps = []
    field_values = []
    if len(ssps) == 0:
        return
    for index in track(
        range(len(ssps)),
        description=f"Importing {len(ssps)} SSP contingency data...",
    ):
        ssp = ssps[index]
        csam_id = ssp_map.get(ssp)
        if not csam_id:
            logger.error(f"Could not find CSAM ID for SSP id: {ssp}")
            continue
        else:
            updated_ssps.append(ssp)

        continuity_response = get_continuity_response_fields(
            ssp=ssp, csam_id=csam_id, continuity_ir_fields_map=continuity_ir_fields_map, continuity_map=continuity_map
        )
        field_values = field_values + continuity_response

        continuity_test = get_continuity_test_fields(
            ssp=ssp,
            csam_id=csam_id,
            continuity_ir_fields_map=continuity_ir_fields_map,
            continuity_test_map=continuity_test_map,
            irp_test_map=irp_test_map,
        )
        field_values = field_values + continuity_test

        additional_status = get_additional_status_fields(
            ssp=ssp,
            csam_id=csam_id,
            continuity_ir_fields_map=continuity_ir_fields_map,
            contingency_plan_map=contingency_plan_map,
            doc_approv_fields_map=doc_approv_fields_map,
            doc_approv_map=doc_approv_map,
        )
        field_values = field_values + additional_status

    # Save the Custom Fields
    if len(field_values) > 0:
        field_values = fix_form_field_value(field_values)
        FormFieldValue.save_custom_fields(field_values)

    logger.info(f"Updated {len(updated_ssps)} Security Plans with contingency data")


def get_continuity_response_fields(ssp: int, csam_id: int, continuity_map: dict, continuity_ir_fields_map: dict):
    # Get the data from /continuityresponse
    result = retrieve_from_csam(
        csam_endpoint=f"/CSAM/api/v1/systems/{csam_id}/continuityresponse",
    )

    if not result:
        logger.error(f"Could not retrieve details for CSAM ID {csam_id}. RegScale SSP id: {ssp}")
        return []

    response_data = result[0]

    # Pre-compute the field mapping to avoid nested lookups
    field_mapping = {
        field: continuity_ir_fields_map[mapped_name]
        for field, mapped_name in continuity_map.items()
        if mapped_name in continuity_ir_fields_map
    }

    # Build field values with single-level lookup
    return [
        {
            "record_id": ssp,
            "record_module": "securityplans",
            "form_field_id": field_id,
            "field_value": str(response_data[field]),
        }
        for field, field_id in field_mapping.items()
        if field in response_data
    ]


def get_continuity_test_fields(
    ssp: int, csam_id: int, continuity_ir_fields_map: dict, continuity_test_map: dict, irp_test_map: dict
):
    # Get the data from continuitytest
    results = retrieve_from_csam(csam_endpoint=f"/CSAM/api/v1/systems/{csam_id}/continuitytest")

    if not results:
        logger.error(f"Could not retrieve details for CSAM ID {csam_id}. RegScale SSP id: {ssp}")
        return []

    # Pre-compute field mappings to avoid nested lookups
    cp_field_mapping = {
        field: continuity_ir_fields_map[mapped_name]
        for field, mapped_name in continuity_test_map.items()
        if mapped_name in continuity_ir_fields_map
    }

    irp_field_mapping = {
        field: continuity_ir_fields_map[mapped_name]
        for field, mapped_name in irp_test_map.items()
        if mapped_name in continuity_ir_fields_map
    }

    field_values = []
    for result in results:
        test_item = result.get("testItem")

        # Process Contingency Plan (CP) fields
        if test_item == "Contingency Plan (CP)":
            field_values.extend(
                [
                    {
                        "record_id": ssp,
                        "record_module": "securityplans",
                        "form_field_id": field_id,
                        "field_value": str(result[field]),
                    }
                    for field, field_id in cp_field_mapping.items()
                    if field in result
                ]
            )

        # Process Incident Response Plan (IRP) fields
        elif test_item == "Incident Response Plan (IRP)":
            field_values.extend(
                [
                    {
                        "record_id": ssp,
                        "record_module": "securityplans",
                        "form_field_id": field_id,
                        "field_value": str(result[field]),
                    }
                    for field, field_id in irp_field_mapping.items()
                    if field in result
                ]
            )

    return field_values


def get_additional_status_fields(
    ssp: int,
    csam_id: int,
    continuity_ir_fields_map: dict,
    contingency_plan_map: dict,
    doc_approv_fields_map: dict,
    doc_approv_map: dict,
):
    # Get the data from additional status
    results = retrieve_from_csam(csam_endpoint=f"/CSAM/api/v1/systems/{csam_id}/additionalstatus")

    if not results:
        logger.error(f"Could not retrieve details for CSAM ID {csam_id}. RegScale SSP id: {ssp}")
        return []

    # Pre-compute field mappings to avoid nested lookups
    cp_field_mapping = {
        field: continuity_ir_fields_map[mapped_name]
        for field, mapped_name in contingency_plan_map.items()
        if mapped_name in continuity_ir_fields_map
    }

    doc_field_mapping = {
        field: doc_approv_fields_map[mapped_name]
        for field, mapped_name in doc_approv_map.items()
        if mapped_name in doc_approv_fields_map
    }

    field_values = []
    for result in results:
        result_name = result.get("name")

        # Process Contingency Plan Review fields
        if result_name == "Contingency Plan Review":
            field_values.extend(
                [
                    {
                        "record_id": ssp,
                        "record_module": "securityplans",
                        "form_field_id": field_id,
                        "field_value": str(result[field]),
                    }
                    for field, field_id in cp_field_mapping.items()
                    if field in result
                ]
            )

        # Process Document Review Approval fields
        elif result_name == "Document Review Approval":
            field_values.extend(
                [
                    {
                        "record_id": ssp,
                        "record_module": "securityplans",
                        "form_field_id": field_id,
                        "field_value": str(result[field]),
                    }
                    for field, field_id in doc_field_mapping.items()
                    if field in result
                ]
            )

    return field_values


def update_ssp_general(ssp: SecurityPlan, record: dict, org_map: dict) -> SecurityPlan:
    """
    Update or Create the SSP Record
    Based upon the values in Record

    :param SecurityPlan ssp: RegScale Security Plan
    :param dict record: record of values
    :param dict org_map: map of org names to orgId
    :return: SecurityPlan Object
    :return_type: SecurityPlan
    """

    ssp.otherIdentifier = record["id"]
    ssp.overallCategorization = record["categorization"]
    ssp.confidentiality = record["categorization"]
    ssp.integrity = record["categorization"]
    ssp.availability = record["categorization"]
    ssp.status = record["operationalStatus"]
    ssp.systemType = record["systemType"]
    ssp.description = record["purpose"]
    ssp.defaultAssessmentDays = 0
    if record["organization"] and org_map.get(record["organization"]):
        ssp.orgId = org_map.get(record["organization"])

    if ssp.id == 0:
        new_ssp = ssp.create()
    else:
        new_ssp = ssp.save()

    return new_ssp


def save_ssp_front_matter(results: list, ssp_map: dict, custom_fields_basic_map: dict, org_map: dict) -> list:
    """
    Save the SSP data from the /systems endpoint

    :param list results: list of results from CSAM
    :param dict ssp_map: map of existing SSPs in RegScale
    :param dict custom_fields_basic_map: map of custom fields in RegScale
    :param dict org_map: map of existing orgs in RegScale
    :return: list of updated SSPs
    :return_type: List[SecurityPlan]
    """

    updated_ssps = []
    for index in track(
        range(len(results)),
        description=f"Importing {len(results)} SSP front matter...",
    ):
        result = results[index]

        # Get the existing SSP:
        ssp_id = ssp_map.get(result["externalId"])
        if ssp_id:
            ssp = SecurityPlan.get_object(ssp_id)
        else:
            ssp = SecurityPlan(systemName=result["name"])
        # Update the SSP
        ssp = update_ssp_general(ssp, result, org_map)

        # Grab the Custom Fields
        field_values = set_front_matter_fields(ssp=ssp, result=result, custom_fields_basic_map=custom_fields_basic_map)

        # System Custom Fields
        field_values = fix_form_field_value(field_values)
        FormFieldValue.save_custom_fields(field_values)
        updated_ssps.append(ssp)
    logger.info(f"Updated {len(results)} Security Plans Front Matter")
    return updated_ssps


def set_front_matter_fields(ssp: SecurityPlan, result: dict, custom_fields_basic_map: dict) -> list:
    """
    parse the front matter custom fields
    and return a list of field values to be saved

    :param SecurityPlan ssp: RegScale Security Plan object
    :param dict result: response from CSAM
    :param dict custom_fields_basic_map: map of basic custom fields
    :return: list of dictionaries with field values
    :return_type: list
    """
    custom_fields_financial_list = [
        "Financial System",
        "omb Exhibit",
        "Investment Name",
        "Portfolio",
        "Prior Fy Funding",
        "Current Fy Funding",
        "Next Fy Funding",
        "Funding Import Status",
    ]

    custom_fields_financial_map = FormFieldValue.check_custom_fields(
        custom_fields_financial_list, "securityplans", SSP_FINANCIAL_TAB
    )

    custom_fields_map = {
        "acronym": "acronym",
        "classification": "Classification",
        "fismaReportable": "FISMA Reportable",
        "contractorSystem": "Contractor System",
        "criticalInfrastructure": "Critical Infrastructure",
        "missionCritical": "Mission Essential",
        "uiiCode": "uiiCode",
    }
    custom_fields_fin_map = {
        "financialSystem": "Financial System",
        "ombExhibit": "omb Exhibit",
        "investmentName": "Investment Name",
        "portfolio": "Portfolio",
        "priorFyFunding": "Prior Fy Funding",
        "currentFyFunding": "Current Fy Funding",
        "nextFyFunding": "Next Fy Funding",
        "fundingImportStatus": "Funding Import Status",
    }

    # Pre-compute field mappings to avoid nested lookups
    basic_field_mapping = {
        field: custom_fields_basic_map[mapped_name]
        for field, mapped_name in custom_fields_map.items()
        if mapped_name in custom_fields_basic_map and field in result
    }

    financial_field_mapping = {
        field: custom_fields_financial_map[mapped_name]
        for field, mapped_name in custom_fields_fin_map.items()
        if mapped_name in custom_fields_financial_map and field in result
    }

    # Start with required ID fields
    field_values = [
        {
            "record_id": ssp.id,
            "record_module": "securityplans",
            "form_field_id": custom_fields_basic_map[FISMA_FIELD_NAME],
            "field_value": str(result["externalId"]),
        },
        {
            "record_id": ssp.id,
            "record_module": "securityplans",
            "form_field_id": custom_fields_basic_map[CSAM_FIELD_NAME],
            "field_value": str(result["id"]),
        },
    ]

    # Process basic tab fields
    field_values.extend(_create_basic_field_values(ssp.id, result, basic_field_mapping))

    # Process financial tab fields
    field_values.extend(_create_financial_field_values(ssp.id, result, financial_field_mapping))

    return field_values


def _create_basic_field_values(record_id: int, result: dict, field_mapping: dict) -> list:
    """Helper function to create basic field values with proper type handling"""
    field_values = []
    for field, field_id in field_mapping.items():
        value = result.get(field)
        if isinstance(value, bool):
            field_value = "Yes" if value else "No"
        else:
            field_value = str(value)

        field_values.append(
            {
                "record_id": record_id,
                "record_module": "securityplans",
                "form_field_id": field_id,
                "field_value": field_value,
            }
        )
    return field_values


def _create_financial_field_values(record_id: int, result: dict, field_mapping: dict) -> list:
    """Helper function to create financial field values with proper handling of funding fields"""
    funding_fields = ["priorFyFunding", "currentFyFunding", "nextFyFunding"]

    field_values = []
    for field, field_id in field_mapping.items():
        value = result.get(field)
        # Handle blank dollar values
        if field in funding_fields:
            field_value = str(value) if value else "0"
        else:
            field_value = str(value)

        field_values.append(
            {
                "record_id": record_id,
                "record_module": "securityplans",
                "form_field_id": field_id,
                "field_value": field_value,
            }
        )
    return field_values
