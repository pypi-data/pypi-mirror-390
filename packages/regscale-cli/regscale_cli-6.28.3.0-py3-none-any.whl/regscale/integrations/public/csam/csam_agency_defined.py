#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates CSAM agencydefineddata into RegScale"""

from rich.progress import track
import logging
from regscale.models.regscale_models import SecurityPlan, FormFieldValue
from regscale.integrations.public.csam.csam_common import retrieve_from_csam, set_custom_fields

logger = logging.getLogger("regscale")

"""This should be refactored as a custom field to custom field parser"""
"""Add logic to grab all the fields from agencydefineddataitems"""
"""Create custom fields in RegScale under "CSAM custom fields tab in SSP"""
"""Shove in whatever attributename: value pairs"""


def update_ssp_agency_details(ssps: list, custom_fields_basic_map: dict) -> list:
    """
    Update the Agency Details of the SSPs
    This requires a call to the /system/{id}/agencydefineddataitems
    endpoint

    :param list ssps: list of RegScale SSPs
    :param dict custom_fields_basic_map: map of custom fields in RegScale
    :return: list of updated SSPs
    :return_type: List[SecurityPlan]
    """
    updated_ssps = []
    # Check for no ssps:
    if len(ssps) == 0:
        return updated_ssps

    # Check if existing customer
    custom_fields_system_list = ["AI/ML Components", "IOT/OT"]
    custom_fields_system_map = FormFieldValue.check_custom_fields(
        custom_fields_system_list, "securityplans", "System Information"
    )
    if custom_fields_system_map:
        # Specific
        updated_ssps = update_specific_details(ssps, custom_fields_basic_map, custom_fields_system_map)
        return updated_ssps

    # Generic Agency
    # STUB - REG-18030

    return updated_ssps


def update_specific_details(ssps: list, custom_fields_basic_map: dict, custom_fields_system_map: dict):
    """
    Handles the CSAM custom fields for existing customer

    :param ssps: List of SSP ids
    :param custom_fields_basic_map: dictionary mapping custom field names to ids
    :param custom_fields_system_map: dictionary mapping custom field names to ids
    :return: list of ssps
    :return_type: list
    """
    updated_ssps = []
    if len(ssps) == 0:
        return updated_ssps

    for index in track(
        range(len(ssps)),
        description=f"Importing {len(ssps)} SSP agency details...",
    ):
        ssp = ssps[index]
        csam_id = ssp.otherIdentifier
        if not csam_id:
            logger.error(f"Could not find CSAM ID for SSP {ssp.systemName} id: {ssp.id}")
            continue
        else:
            updated_ssps.append(ssp)

        result = retrieve_from_csam(
            csam_endpoint=f"/CSAM/api/v1/systems/{csam_id}/agencydefineddataitems",
        )
        if len(result) == 0:
            logger.error(
                f"Could not retrieve details for CSAM ID {csam_id}. RegScale SSP: Name: {ssp.systemName} id: {ssp.id}"
            )
            continue
        # Get the custom fields
        set_agency_details(result, ssp, custom_fields_basic_map, custom_fields_system_map)

    logger.info(f"Updated {len(updated_ssps)} Security Plans with Agency Details")
    return updated_ssps


def set_agency_details(result: list, ssp: SecurityPlan, custom_fields_basic_map: dict, custom_fields_system_map: dict):
    """
    Loop through results of agencydefineddataitems
    and set the custom fields in RegScale

    :param list result: list of dict objects from CSAM
    :param SecurityPlan ssp: RegScale Security Plan
    :param dict custom_fields_basic_map: map of custom field names to ids
    :param dict custom_fields_system_map: map of custom fields names to ids
    """

    field_values = []
    # Update the fields we need
    for item in result:
        if item.get("attributeName") == "High Value Asset":
            ssp.hva = True if item.get("value") == "1" else False

        # Binary Values
        elif item.get("attributeName") in ["External Web Interface", "CFO Designation", "Law Enforcement Sensitive"]:
            field_values.append(set_binary_fields(item, ssp, custom_fields_basic_map))

        elif item.get("attributeName") == "Cloud System":
            ssp = set_cloud_system(ssp, item)

        elif item.get("attributeName") == "Cloud Service Model":
            ssp = set_cloud_service(ssp, item)

        elif item.get("attributeName") == "HVA Identifier":
            field_values.append(set_custom_fields(item, ssp, custom_fields_basic_map))

        elif item.get("attributeName") in ["AI/ML Components", "IOT/OT"]:
            field_values.append(set_custom_fields(item, ssp, custom_fields_system_map))

    # Save the SSP & Custom Fields
    ssp.defaultAssessmentDays = 0
    ssp.save()
    if len(field_values) > 0:
        FormFieldValue.save_custom_fields(field_values)


def set_cloud_system(ssp: SecurityPlan, item: dict) -> SecurityPlan:
    """
    Set the cloud system values in the SSP
    :param SeucrityPlan ssp: RegScale Security Plan
    :param dict item: record from CSAM
    :return: SecurityPlan object with updated cloud system values
    :return_type: SecurityPlan
    """
    ssp.bDeployPublic = True if item.get("value") == "Public" else False
    ssp.bDeployPrivate = True if item.get("value") == "Private" else False
    ssp.bDeployHybrid = True if item.get("value") == "Hybrid" else False
    ssp.bDeployGov = True if item.get("value") == "GovCloud" else False
    ssp.bDeployOther = True if item.get("value") == "Community" else False
    if ssp.bDeployHybrid or ssp.bDeployOther:
        ssp.deployOtherRemarks = "Hybrid or Community"

    return ssp


def set_cloud_service(ssp: SecurityPlan, item: dict) -> SecurityPlan:
    """
    Set the cloud service model values in the SSP

    :param SecurityPlan ssp: RegScale Security Plan
    :param dict item: record from CSAM
    :return: Updated SecurityPlan object
    :return_type: SecurityPlan
    """
    ssp.bModelIaaS = True if "IaaS" in item.get("value") else False
    ssp.bModelPaaS = True if "PaaS" in item.get("value") else False
    ssp.bModelSaaS = True if "SaaS" in item.get("value") else False
    return ssp


def set_binary_fields(item: dict, ssp: SecurityPlan, custom_fields_map: dict) -> dict:
    """
    Logic to set the custom fields were the source are binary

    :param dict item: record from CSAM
    :param SecurityPlan ssp: RegScale Security Plan
    :param custom_fields_map: map of custom field names to ids
    :return: RegScale custom fields records
    :return_type: dict
    """
    return {
        "record_id": ssp.id,
        "form_field_id": custom_fields_map[item.get("attributeName")],
        "field_value": "Yes" if (item.get("value")) == "1" else "No",
    }
