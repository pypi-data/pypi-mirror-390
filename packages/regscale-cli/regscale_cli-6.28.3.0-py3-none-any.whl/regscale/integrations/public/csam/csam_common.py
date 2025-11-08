#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates CSAM into RegScale"""

# standard python imports
import logging
from typing import List
from urllib.parse import urljoin
from regscale.core.app.application import Application
from regscale.core.app.api import Api

from regscale.models.regscale_models import SecurityPlan, Module
from regscale.models.regscale_models.regscale_model import RegScaleModel
from regscale.integrations.control_matcher import ControlMatcher
from regscale.models.regscale_models.form_field_value import FormFieldValue

SSP_BASIC_TAB = "Basic Info"
CSAM_FIELD_NAME = "CSAM Id"
FISMA_FIELD_NAME = "FISMA Id"
SYSTEM_ID = "System ID"

logger = logging.getLogger("regscale")


def set_custom_fields(item: dict, ssp: SecurityPlan, custom_fields_map: dict) -> dict:
    """
    Set the custom fields for the SSP

    :param dict item: record from CSAM
    :param SecurityPlan ssp: RegScale Security Plan
    :param dict custom_fields_map: map of custom fields in RegScale
    :return: dictionary of field values to be saved
    :return_type: dict
    """
    return {
        "record_id": ssp.id,
        "record_module": "securityplans",
        "form_field_id": custom_fields_map[item.get("attributeName")],
        "field_value": str(item.get("value")),
    }


def retrieve_custom_form_ssps_map(tab_name: str, field_form_id: int) -> dict:
    """
    Retreives a list of the SSPs in RegScale
    Returns a map of Custom Field Value: RegScale Id

    :param str tab_name: The RegScale tab name where the custom field is located
    :param int field_form_id: The RegScale Form Id of custom field
    :param int tab_id: The RegScale tab id
    :return: dictionary of FieldForm Id: regscale_ssp_id
    :return_type: dict
    """
    tab = Module.get_tab_by_name(regscale_module_name="securityplans", regscale_tab_name=tab_name)

    field_form_map = {}
    ssps = SecurityPlan.get_ssp_list()
    form_values = []
    for ssp in ssps:
        form_values = FormFieldValue.get_field_values(
            record_id=ssp["id"], module_name=SecurityPlan.get_module_slug(), form_id=tab.id
        )

        for form in form_values:
            if form.formFieldId == field_form_id and form.data:
                field_form_map[form.data] = ssp["id"]
        form_values = []
    return field_form_map


def retrieve_ssps_custom_form_map(tab_name: str, field_form_id: int) -> dict:
    """
    Retreives a list of the SSPs in RegScale
    Returns a map of Custom Field Value: RegScale Id

    :param str tab_name: The RegScale tab name where the custom field is located
    :param int field_form_id: The RegScale Form Id of custom field
    :param int tab_id: The RegScale tab id
    :return: dictionary of FieldForm Id: regscale_ssp_id
    :return_type: dict
    """
    tab = Module.get_tab_by_name(regscale_module_name="securityplans", regscale_tab_name=tab_name)

    field_form_map = {}
    ssps = SecurityPlan.get_ssp_list()
    form_values = []
    for ssp in ssps:
        form_values = FormFieldValue.get_field_values(
            record_id=ssp["id"], module_name=SecurityPlan.get_module_slug(), form_id=tab.id
        )

        for form in form_values:
            if form.formFieldId == field_form_id and form.data:
                field_form_map[ssp["id"]] = form.data
        form_values = []
    return field_form_map


def retrieve_from_csam(csam_endpoint: str) -> list:
    """
    Connect to CSAM and retrieve data

    :param str csam_endpoint: API Endpoint
    :return: List of dict objects
    :return_type: list
    """
    logger.debug("Retrieving data from CSAM")
    app = Application()
    api = Api()
    csam_token = app.config.get("csamToken")
    csam_url = app.config.get("csamURL")

    if "Bearer" not in csam_token:
        csam_token = f"Bearer {csam_token}"

    url = urljoin(csam_url, csam_endpoint)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": csam_token,
    }

    issue_response = api.get(url=url, headers=headers)
    if not issue_response or issue_response.status_code in [204, 404]:
        logger.warning(f"Call to {url} Returned error: {issue_response.text}")
        return []
    if issue_response.ok:
        return issue_response.json()

    return []


def fix_form_field_value(form_fields: list) -> list:
    """
    Cleans up a list of FormFieldValue dicts to prevent
    400 errors due to misformed values

    :param form_fields: list of formFieldValue dicts
    :return: list of fixed formFieldValues dicts
    """
    new_field_values = []
    for field_value in form_fields:
        # Check if record_id, record_module, and form_field_id are set
        if (field_value.get("record_id") is None) or (field_value.get("record_id") == 0):
            continue
        if (field_value.get("form_field_id") is None) or (field_value.get("form_field_id") == 0):
            continue

        # Check if value == "None"
        if field_value.get("field_value") == "None":
            field_value["field_value"] = ""

        new_field_values.append(field_value)
    return new_field_values
