#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QRadar integration CLI commands for RegScale"""

import logging
from typing import Any, Dict, Optional

import click

from regscale.models import regscale_ssp_id
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import error_and_exit
from regscale.models.integration_models.qradar_models.connectors.events import QRadarIntegration
from regscale.integrations.commercial.qradar.qradar_api_client import QRadarAPIClient, QRadarAPIException

logger = logging.getLogger("regscale")


# Create group to handle QRadar integration
@click.group()
def qradar():
    """
    Sync events and findings from IBM QRadar SIEM to RegScale.

    QRadar is an enterprise SIEM (Security Information and Event Management) platform
    that collects, normalizes, and analyzes security events from across the IT environment.

    This integration allows you to:
    - Sync assets discovered from QRadar events
    - Create issues/findings from security events
    - Link events to compliance controls
    - Generate evidence for assessments

    Example usage:
        regscale qradar sync-events --base-url https://qradar.example.com --api-key YOUR_KEY --ssp-id 123
        regscale qradar sync-findings --base-url https://qradar.example.com --api-key YOUR_KEY --ssp-id 123
    """


@qradar.command(name="sync-events")  # type: ignore[misc]
@regscale_ssp_id()
@click.option(
    "--base-url",
    help="QRadar instance base URL (overrides config file)",
)
@click.option(
    "--api-key",
    help="QRadar API key (SEC token) (overrides config file)",
)
@click.option(
    "--time-window",
    type=int,
    help="Time window in hours to fetch events (overrides config file)",
)
@click.option(
    "--severity-threshold",
    type=int,
    help="Minimum severity level to sync 0-10 (overrides config file)",
)
@click.option(
    "--verify-ssl/--no-verify-ssl",
    default=None,
    help="Verify SSL certificates (overrides config file)",
)
def sync_events(
    regscale_ssp_id: int,  # pylint: disable=redefined-outer-name
    base_url: Optional[str],
    api_key: Optional[str],
    time_window: Optional[int],
    severity_threshold: Optional[int],
    verify_ssl: Optional[bool],
) -> None:
    """
    Sync security events from QRadar into RegScale as findings.

    This command:
    1. Connects to QRadar instance
    2. Fetches security events within the specified time window
    3. Transforms events into RegScale findings
    4. Maps events to compliance controls
    5. Creates issues in RegScale SSP

    Args:
        regscale_ssp_id: RegScale Security Plan ID
        base_url: QRadar instance URL
        api_key: QRadar API key (SEC token)
        time_window: Hours of events to retrieve (default: 24)
        severity_threshold: Minimum severity to process (0-10, default: 5)
        verify_ssl: Whether to verify SSL certificates

    Examples:
        # Sync last 24 hours of events
        regscale qradar sync-events --id 123

        # Sync last 7 days of critical events
        regscale qradar sync-events --id 123 --time-window 168 --severity-threshold 8

        # Sync with SSL verification disabled (for development)
        regscale qradar sync-events --id 123 --no-verify-ssl
    """
    try:
        logger.info("Starting QRadar event sync for SSP %d", regscale_ssp_id)

        # Load configuration from init.yaml
        app = Application()
        qradar_config = app.config.get("qradar", {})

        # Build kwargs for integration - use CLI args if provided, otherwise use config
        kwargs: Dict[str, Any] = {}
        if base_url or qradar_config.get("base_url"):
            kwargs["base_url"] = base_url or qradar_config.get("base_url")
        if api_key or qradar_config.get("api_key"):
            kwargs["api_key"] = api_key or qradar_config.get("api_key")
        if time_window or qradar_config.get("time_window_hours"):
            kwargs["time_window_hours"] = time_window or qradar_config.get("time_window_hours")
        if severity_threshold or qradar_config.get("severity_threshold"):
            kwargs["severity_threshold"] = severity_threshold or qradar_config.get("severity_threshold")
        # Handle verify_ssl separately since None is a valid CLI value
        if verify_ssl is not None:
            kwargs["verify_ssl"] = verify_ssl
        elif "verify_ssl" in qradar_config:
            kwargs["verify_ssl"] = qradar_config.get("verify_ssl")

        # Use classmethod - framework handles everything
        QRadarIntegration.sync_findings(plan_id=regscale_ssp_id, **kwargs)

        logger.info("QRadar event sync completed successfully")
        click.echo(click.style("QRadar events synced successfully!", fg="green"))

    except Exception as exc:
        error_msg = f"Error syncing QRadar events: {exc!s}"
        logger.error(error_msg)
        logger.debug(error_msg, exc_info=True)
        error_and_exit(error_msg)


@qradar.command(name="sync-findings")  # type: ignore[misc]
@regscale_ssp_id()
@click.option(
    "--base-url",
    help="QRadar instance base URL (overrides config file)",
)
@click.option(
    "--api-key",
    help="QRadar API key (SEC token) (overrides config file)",
)
@click.option(
    "--time-window",
    type=int,
    help="Time window in hours to fetch events (overrides config file)",
)
@click.option(
    "--severity-threshold",
    type=int,
    help="Minimum severity level to sync 0-10 (overrides config file)",
)
@click.option(
    "--verify-ssl/--no-verify-ssl",
    default=None,
    help="Verify SSL certificates (overrides config file)",
)
def sync_findings(
    regscale_ssp_id: int,  # pylint: disable=redefined-outer-name
    base_url: Optional[str],
    api_key: Optional[str],
    time_window: Optional[int],
    severity_threshold: Optional[int],
    verify_ssl: Optional[bool],
) -> None:
    """
    Sync findings and assets from QRadar security events into RegScale.

    This command automatically discovers assets from QRadar events and syncs both
    findings and assets. Assets are created first, then findings are linked to them.

    This follows the AWS Security Hub pattern where assets are automatically
    discovered and synced as part of the findings sync process.

    Args:
        regscale_ssp_id: RegScale Security Plan ID
        base_url: QRadar instance URL
        api_key: QRadar API key (SEC token)
        time_window: Hours of events to retrieve (default: 24)
        severity_threshold: Minimum severity to process (0-10, default: 5)
        verify_ssl: Whether to verify SSL certificates

    Examples:
        # Sync findings and assets from last 24 hours
        regscale qradar sync-findings --id 123

        # Sync findings and assets from last week
        regscale qradar sync-findings --id 123 --time-window 168
    """
    try:
        logger.info("Starting QRadar findings and assets sync for SSP %d", regscale_ssp_id)

        # Load configuration from init.yaml
        app = Application()
        qradar_config = app.config.get("qradar", {})

        # Build kwargs for integration - use CLI args if provided, otherwise use config
        kwargs: Dict[str, Any] = {}
        if base_url or qradar_config.get("base_url"):
            kwargs["base_url"] = base_url or qradar_config.get("base_url")
        if api_key or qradar_config.get("api_key"):
            kwargs["api_key"] = api_key or qradar_config.get("api_key")
        if time_window or qradar_config.get("time_window_hours"):
            kwargs["time_window_hours"] = time_window or qradar_config.get("time_window_hours")
        if severity_threshold or qradar_config.get("severity_threshold"):
            kwargs["severity_threshold"] = severity_threshold or qradar_config.get("severity_threshold")
        # Handle verify_ssl separately since None is a valid CLI value
        if verify_ssl is not None:
            kwargs["verify_ssl"] = verify_ssl
        elif "verify_ssl" in qradar_config:
            kwargs["verify_ssl"] = qradar_config.get("verify_ssl")

        # Create integration instance and sync findings + assets
        scanner = QRadarIntegration(plan_id=regscale_ssp_id, **kwargs)
        findings_processed, assets_processed = scanner.sync_findings_and_assets(**kwargs)

        logger.info("QRadar sync completed: %d findings, %d assets", findings_processed, assets_processed)
        click.echo(
            click.style(
                f"QRadar sync completed successfully: {findings_processed} findings, {assets_processed} assets",
                fg="green",
            )
        )

    except Exception as exc:
        error_msg = f"Error syncing QRadar findings: {exc!s}"
        logger.error(error_msg)
        logger.debug(error_msg, exc_info=True)
        error_and_exit(error_msg)


@qradar.command(name="sync-assets")  # type: ignore[misc]
@regscale_ssp_id()
@click.option(
    "--base-url",
    help="QRadar instance base URL (overrides config file)",
)
@click.option(
    "--api-key",
    help="QRadar API key (SEC token) (overrides config file)",
)
@click.option(
    "--time-window",
    type=int,
    help="Time window in hours to fetch events (overrides config file)",
)
@click.option(
    "--verify-ssl/--no-verify-ssl",
    default=None,
    help="Verify SSL certificates (overrides config file)",
)
def sync_assets(
    regscale_ssp_id: int,  # pylint: disable=redefined-outer-name
    base_url: Optional[str],
    api_key: Optional[str],
    time_window: Optional[int],
    verify_ssl: Optional[bool],
) -> None:
    """
    Sync assets discovered from QRadar events into RegScale.

    Extracts unique assets from QRadar security events based on:
    - Source IP addresses
    - Destination IP addresses
    - Hostnames
    - Log sources

    Args:
        regscale_ssp_id: RegScale Security Plan ID
        base_url: QRadar instance URL
        api_key: QRadar API key (SEC token)
        time_window: Hours of events to analyze (default: 24)
        verify_ssl: Whether to verify SSL certificates

    Examples:
        # Sync assets from last 24 hours
        regscale qradar sync-assets --id 123

        # Sync assets from last week
        regscale qradar sync-assets --id 123 --time-window 168
    """
    try:
        logger.info("Starting QRadar asset sync for SSP %d", regscale_ssp_id)

        # Load configuration from init.yaml
        app = Application()
        qradar_config = app.config.get("qradar", {})

        # Build kwargs for integration - use CLI args if provided, otherwise use config
        kwargs: Dict[str, Any] = {}
        if base_url or qradar_config.get("base_url"):
            kwargs["base_url"] = base_url or qradar_config.get("base_url")
        if api_key or qradar_config.get("api_key"):
            kwargs["api_key"] = api_key or qradar_config.get("api_key")
        if time_window or qradar_config.get("time_window_hours"):
            kwargs["time_window_hours"] = time_window or qradar_config.get("time_window_hours")
        # Handle verify_ssl separately since None is a valid CLI value
        if verify_ssl is not None:
            kwargs["verify_ssl"] = verify_ssl
        elif "verify_ssl" in qradar_config:
            kwargs["verify_ssl"] = qradar_config.get("verify_ssl")

        # Use classmethod - framework handles everything
        QRadarIntegration.sync_assets(plan_id=regscale_ssp_id, **kwargs)

        logger.info("QRadar asset sync completed successfully")
        click.echo(click.style("QRadar assets synced successfully!", fg="green"))

    except Exception as exc:
        error_msg = f"Error syncing QRadar assets: {exc!s}"
        logger.error(error_msg)
        logger.debug(error_msg, exc_info=True)
        error_and_exit(error_msg)


@qradar.command(name="test-connection")
@click.option(
    "--base-url",
    help="QRadar instance base URL (overrides config file)",
)
@click.option(
    "--api-key",
    help="QRadar API key (SEC token) (overrides config file)",
)
@click.option(
    "--verify-ssl/--no-verify-ssl",
    default=None,
    help="Verify SSL certificates (overrides config file)",
)
def test_connection(
    base_url: Optional[str],
    api_key: Optional[str],
    verify_ssl: Optional[bool],
) -> None:
    """
    Test connection to QRadar instance.

    Verifies that:
    - QRadar API is accessible
    - API credentials are valid
    - SSL certificates are valid (if verification enabled)

    Args:
        base_url: QRadar instance URL
        api_key: QRadar API key (SEC token)
        verify_ssl: Whether to verify SSL certificates

    Examples:
        # Test connection with config from init.yaml
        regscale qradar test-connection

        # Test connection without SSL verification (development)
        regscale qradar test-connection --no-verify-ssl
    """
    try:
        # Load configuration from init.yaml
        app = Application()
        qradar_config = app.config.get("qradar", {})

        # Use CLI args if provided, otherwise use config
        base_url = base_url or qradar_config.get("base_url")
        api_key = api_key or qradar_config.get("api_key")
        verify_ssl = verify_ssl if verify_ssl is not None else qradar_config.get("verify_ssl", True)

        # Validate required fields
        if not base_url:
            error_and_exit("QRadar base_url required (provide --base-url or add to init.yaml)")
        if not api_key:
            error_and_exit("QRadar api_key required (provide --api-key or add to init.yaml)")

        logger.info("Testing connection to QRadar at %s", base_url)
        click.echo(f"Connecting to QRadar at {base_url}...")

        # Initialize client
        qradar_client = QRadarAPIClient(
            base_url=base_url,
            api_key=api_key,
            verify_ssl=verify_ssl,
        )

        # Test connection
        qradar_client.test_connection()

        click.echo(click.style("Connection successful!", fg="green"))
        logger.info("QRadar connection test successful")

    except QRadarAPIException as exc:
        error_msg = f"Connection test failed: {exc!s}"
        logger.error(error_msg)
        click.echo(click.style(error_msg, fg="red"))
        error_and_exit(error_msg)

    except Exception as exc:
        error_msg = f"Connection test failed: {exc!s}"
        logger.error(error_msg)
        logger.debug(error_msg, exc_info=True)
        click.echo(click.style(error_msg, fg="red"))
        error_and_exit(error_msg)
