#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates CSAM into RegScale"""

# standard python imports
import logging
from typing import List
from rich.progress import track
from rich.console import Console
from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.utils.date import format_to_regscale_iso, date_obj
from regscale.core.app.utils.app_utils import error_and_exit, filter_list
from regscale.core.app.utils.parser_utils import safe_date_str
from regscale.models.regscale_models import (
    Issue,
    SecurityControl,
    SecurityPlan,
    User,
)
from regscale.models.regscale_models.regscale_model import RegScaleModel
from regscale.integrations.control_matcher import ControlMatcher
from regscale.models.regscale_models.form_field_value import FormFieldValue
from regscale.integrations.public.csam.csam_common import (
    retrieve_ssps_custom_form_map,
    retrieve_from_csam,
    FISMA_FIELD_NAME,
    CSAM_FIELD_NAME,
    SSP_BASIC_TAB,
    SYSTEM_ID,
)

POAM_ID = "POAM Id"

logger = logging.getLogger("regscale")
console = Console()

####################################################################################################
#
# IMPORT SSP / POAM FROM DoJ's CSAM GRC
# CSAM API Docs: https://csam.dhs.gov/CSAM/api/docs/index.html (required PIV)
#
####################################################################################################


def import_csam_poams():
    # Check Custom Fields
    custom_fields_basic_map = FormFieldValue.check_custom_fields(
        fields_list=[FISMA_FIELD_NAME, CSAM_FIELD_NAME], module_name="securityplans", tab_name=SSP_BASIC_TAB
    )

    # Get the SSPs
    ssp_map = retrieve_ssps_custom_form_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[CSAM_FIELD_NAME]
    )

    # Get a list of users and create a map to id
    users = User.get_all()
    user_map = {user.userName: user.id for user in users}

    # Grab the data from CSAM
    results = retrieve_from_csam(csam_endpoint="/CSAM/api/v1/reports/POAM_Details_Report_CBP")

    # Parse the results
    poam_list = []
    for index in track(
        range(len(results)),
        description=f"Importing {len(results)} POA&Ms...",
    ):
        result = results[index]

        # Get the existing SSP:
        ssp_id = ssp_map.get(str(result[SYSTEM_ID]))
        if not ssp_id:
            logger.error(
                f"A RegScale Security Plan does not exist for CSAM id: {result[SYSTEM_ID]}\
             create or import the Security Plan prior to importing POA&Ms"
            )
            continue

        # Check if the POAM exists:
        existing_issue = Issue.find_by_other_identifier(result[POAM_ID])
        if existing_issue:
            new_issue = existing_issue
        else:
            new_issue = Issue()

        # Update the issue
        new_issue.isPoam = True
        new_issue.parentId = ssp_id
        new_issue.parentModule = "securityplans"
        new_issue.otherIdentifier = result[POAM_ID]
        new_issue.title = result["POAM Title"]
        new_issue.affectedControls = result["Controls"]
        new_issue.securityPlanId = ssp_id
        new_issue.identification = "Vulnerability Assessment"
        new_issue.description = result["Detailed Weakness Description"]
        new_issue.poamComments = f"{result['Weakness Comments']}\n \
            {result['POA&M Delayed Comments']}\n \
            {result['POA&M Comments']}"
        new_issue.dateFirstDetected = safe_date_str(result["Create Date"])
        new_issue.dueDate = safe_date_str(result["Planned Finish Date"])
        # Need to convert cost to a int
        # new_issue.costEstimate = result['Cost']
        new_issue.issueOwnerId = (
            user_map.get(result["Email"]) if user_map.get(result["Email"]) else RegScaleModel.get_user_id()
        )
        # Update with IssueSeverity String
        new_issue.severityLevel = result["Severity"]
        # Update with IssueStatus String
        new_issue.status = result["Status"]

        poam_list.append(new_issue)

    for index in track(
        range(len(poam_list)),
        description=f"Updating RegScale with {len(poam_list)} POA&Ms...",
    ):
        poam = poam_list[index]
        if poam.id == 0:
            poam.create()
        else:
            poam.save()
    logger.info(f"Added or updated {len(poam_list)} POA&Ms in RegScale")
