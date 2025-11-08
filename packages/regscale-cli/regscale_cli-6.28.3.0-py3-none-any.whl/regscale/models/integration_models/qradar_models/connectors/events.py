"""QRadar Events Connector Model for RegScale Integration"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Iterator, Optional, Dict, Any, List

from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.integrations.scanner_integration import (
    IntegrationAsset,
    IntegrationFinding,
    ScannerIntegration,
    ScannerIntegrationType,
)
from regscale.models.integration_models.qradar_models.event import QRadarEvent
from regscale.models.regscale_models import (
    IssueSeverity,
    AssetStatus,
    IssueStatus,
)

logger = logging.getLogger("regscale")


class QRadarIntegration(ScannerIntegration):
    """
    QRadar SIEM integration for RegScale.

    This integration syncs security events and findings from IBM QRadar SIEM
    into RegScale for compliance and risk management.

    Supports:
    - Asset synchronization from QRadar events
    - Finding/issue creation from security events
    - Control mapping for compliance frameworks
    - Event correlation and aggregation

    Example usage:
        >>> from regscale.integrations.commercial.qradar.qradar_api_client import QRadarAPIClient
        >>> client = QRadarAPIClient(
        ...     base_url="https://qradar.example.com",
        ...     api_key="your-api-key"
        ... )
        >>> integration = QRadarIntegration(
        ...     plan_id=123,
        ...     qradar_client=client,
        ...     time_window_hours=24
        ... )
        >>> integration.sync_assets(plan_id=123)
        >>> integration.sync_findings(plan_id=123)
    """

    # Required fields from ScannerIntegration
    title = "QRadar"
    asset_identifier_field = "ipAddress"  # Primary field for asset identification (camelCase)

    # Map QRadar severity levels to RegScale IssueSeverity
    finding_severity_map = {
        "10": IssueSeverity.Critical,  # QRadar severity 10 (Critical)
        "9": IssueSeverity.Critical,  # QRadar severity 9 (Critical)
        "8": IssueSeverity.High,  # QRadar severity 8 (High)
        "7": IssueSeverity.High,  # QRadar severity 7 (High)
        "6": IssueSeverity.Moderate,  # QRadar severity 6 (Medium)
        "5": IssueSeverity.Moderate,  # QRadar severity 5 (Medium)
        "4": IssueSeverity.Low,  # QRadar severity 4 (Low)
        "3": IssueSeverity.Low,  # QRadar severity 3 (Low)
        "2": IssueSeverity.Low,  # QRadar severity 2 (Info)
        "1": IssueSeverity.Low,  # QRadar severity 1 (Info)
        "0": IssueSeverity.NotAssigned,  # QRadar severity 0 (Unknown)
    }

    # Map QRadar severity levels to RegScale Priority
    finding_priority_map = {
        "10": "Critical",  # QRadar severity 10 (Critical)
        "9": "Critical",  # QRadar severity 9 (Critical)
        "8": "High",  # QRadar severity 8 (High)
        "7": "High",  # QRadar severity 7 (High)
        "6": "Medium",  # QRadar severity 6 (Medium)
        "5": "Medium",  # QRadar severity 5 (Medium)
        "4": "Low",  # QRadar severity 4 (Low)
        "3": "Low",  # QRadar severity 3 (Low)
        "2": "Low",  # QRadar severity 2 (Info)
        "1": "Low",  # QRadar severity 1 (Info)
        "0": "Low",  # QRadar severity 0 (Unknown)
    }

    # Integration type - QRadar events should be created as Vulnerabilities and Issues
    # VULNERABILITY type creates both vulnerability records and linked issues
    type = ScannerIntegrationType.VULNERABILITY

    app = Application()

    def __init__(self, plan_id: int, *args, **kwargs):
        """
        Initialize QRadar integration.

        Args:
            plan_id: RegScale security plan ID
            *args: Additional positional arguments for ScannerIntegration
            **kwargs: Additional keyword arguments for ScannerIntegration
                - time_window_hours: Time window for fetching events (default: 24 hours)
                - severity_threshold: Minimum severity level to sync (default: 5)
                - verify_ssl: Whether to verify SSL certificates (default: from config)
                - base_url: QRadar instance URL (default: from config)
                - api_key: QRadar API key (default: from config)
        """
        super().__init__(plan_id, *args, **kwargs)

        # Lazy initialization - client created on first use
        self._qradar_client: Optional[Any] = None

        # Track discovered assets for sync_findings_and_assets
        self.discovered_assets: List[IntegrationAsset] = []
        self.processed_asset_identifiers: set = set()

        # Get configuration from kwargs or config file
        qradar_config = self.app.config.get("qradar", {})

        # Override config with kwargs if provided
        self.base_url = kwargs.get("base_url") or qradar_config.get("base_url")
        self.api_key = kwargs.get("api_key") or qradar_config.get("api_key")
        self.time_window_hours = kwargs.get("time_window_hours") or qradar_config.get("time_window_hours", 24)
        self.severity_threshold = kwargs.get("severity_threshold") or qradar_config.get("severity_threshold", 5)
        verify_ssl_value = kwargs.get("verify_ssl")
        if verify_ssl_value is None:
            verify_ssl_value = qradar_config.get("verify_ssl", True)
        self.verify_ssl: bool = bool(verify_ssl_value)

        # Additional client configuration
        self.timeout = qradar_config.get("timeout", 30)
        self.max_retries = qradar_config.get("max_retries", 3)
        self.query_timeout = qradar_config.get("query_timeout", 300)
        self.max_events = qradar_config.get("max_events", 10000)

        # Calculate time range for queries
        self.end_time = datetime.now(timezone.utc)
        self.start_time = self.end_time - timedelta(hours=self.time_window_hours)

        logger.info(
            f"QRadar integration initialized for plan {plan_id} "
            f"(time window: {self.time_window_hours}h, severity >= {self.severity_threshold})"
        )

    @property
    def qradar_client(self) -> Any:
        """
        Lazy initialization of QRadar API client.

        Returns:
            QRadarAPIClient instance

        Raises:
            ValueError: If base_url or api_key not configured
        """
        if self._qradar_client is None:
            # Validate required configuration
            if not self.base_url:
                raise ValueError(
                    "QRadar base_url required. Add to init.yaml under 'qradar' section or pass as --base-url"
                )
            if not self.api_key:
                raise ValueError(
                    "QRadar api_key required. Add to init.yaml under 'qradar' section or pass as --api-key"
                )

            # Import here to avoid circular dependencies
            from regscale.integrations.commercial.qradar.qradar_api_client import QRadarAPIClient

            logger.info(f"Creating QRadar API client for {self.base_url}")
            self._qradar_client = QRadarAPIClient(
                base_url=self.base_url,
                api_key=self.api_key,
                verify_ssl=self.verify_ssl,
                timeout=self.timeout,
                max_retries=self.max_retries,
            )

        return self._qradar_client

    def fetch_assets(self, *args, **kwargs) -> Iterator[IntegrationAsset]:
        """
        Fetch assets from QRadar events.

        Extracts unique assets from QRadar security events based on:
        - Source IP addresses
        - Destination IP addresses
        - Hostnames/FQDNs
        - Log sources

        Yields:
            IntegrationAsset objects for each unique asset discovered
        """
        logger.info("Fetching assets from QRadar events...")

        # Track unique assets by IP address to avoid duplicates
        seen_assets: Dict[str, IntegrationAsset] = {}

        try:
            # Fetch events from QRadar
            events = self._fetch_qradar_events()

            for event in events:
                # Extract assets from source IP
                if event.is_valid_source_asset() and event.source_ip:
                    source_ip = event.source_ip
                    if source_ip not in seen_assets:
                        asset = self._create_asset_from_event(event, source_ip)
                        seen_assets[source_ip] = asset
                        logger.debug(
                            f"Created source asset: {asset.name} (IP: {asset.ip_address}, identifier: {asset.identifier})"
                        )
                        yield asset

                # Extract assets from destination IP
                if event.is_valid_dest_asset() and event.dest_ip:
                    dest_ip = event.dest_ip
                    if dest_ip not in seen_assets:
                        asset = self._create_asset_from_event(event, dest_ip)
                        seen_assets[dest_ip] = asset
                        logger.debug(
                            f"Created dest asset: {asset.name} (IP: {asset.ip_address}, identifier: {asset.identifier})"
                        )
                        yield asset

            logger.info(f"Fetched {len(seen_assets)} unique assets from QRadar")
            logger.debug(f"Asset identifiers: {list(seen_assets.keys())}")

        except Exception as e:
            logger.error(f"Error fetching assets from QRadar: {str(e)}")
            raise

    def _determine_asset_hostname(self, event: QRadarEvent, ip_address: str, is_hostname: bool) -> str:
        """
        Determine the hostname for an asset.

        Args:
            event: QRadarEvent object
            ip_address: IP address or hostname string
            is_hostname: Whether the address is a hostname

        Returns:
            Formatted hostname string
        """
        if is_hostname:
            return ip_address

        # For IP addresses, try to use username or log source as name
        if event.username and event.username not in ["", "N/A", "Unknown", "unknown"]:
            return f"{event.username}@{ip_address}"

        if event.log_source and event.log_source not in ["Unknown Source", "N/A"]:
            log_source_parts = event.log_source.split()
            if log_source_parts:
                return f"{log_source_parts[0]}-{ip_address}"

        return f"host-{ip_address}"

    def _determine_asset_category_and_type(self, log_source: str, ip_address: str) -> tuple[str, str]:
        """
        Determine asset category and type based on log source.

        Args:
            log_source: QRadar log source string
            ip_address: IP address or hostname

        Returns:
            Tuple of (asset_category, asset_type)
        """
        log_source_lower = log_source.lower()

        if "cloudtrail" in log_source_lower or "amazonaws.com" in ip_address:
            return "Cloud Service", "Cloud Resource"
        if "windows" in log_source_lower:
            return "Windows System", "Server"
        if "linux" in log_source_lower:
            return "Linux System", "Server"
        if "firewall" in log_source_lower:
            return "Network Device", "Firewall"
        if "ids" in log_source_lower or "ips" in log_source_lower:
            return "Security Device", "IDS/IPS"

        return "Unknown", "Other"

    def _create_asset_from_event(self, event: QRadarEvent, ip_address: str) -> IntegrationAsset:
        """
        Create an IntegrationAsset from a QRadar event.

        Args:
            event: QRadarEvent object
            ip_address: IP address or hostname for the asset

        Returns:
            IntegrationAsset object
        """
        # Determine if this is an IP address or hostname
        import re

        is_hostname = bool(re.search(r"[a-zA-Z]", ip_address))

        # Determine asset name
        hostname = self._determine_asset_hostname(event, ip_address, is_hostname)

        # Determine asset category and type
        log_source = event.log_source or "Unknown"
        asset_category, asset_type = self._determine_asset_category_and_type(log_source, ip_address)

        # Set ip_address and fqdn based on whether it's a hostname
        # IMPORTANT: Always set ip_address even for hostnames because scanner integration
        # uses asset_identifier_field="ipAddress" to look up assets
        return IntegrationAsset(
            name=hostname,
            identifier=ip_address,
            ip_address=ip_address,  # Set for both IPs and hostnames for asset lookup
            fqdn=ip_address if is_hostname else None,  # Also set FQDN for hostnames
            asset_type=asset_type,
            asset_category=asset_category,
            status=AssetStatus.Active,
            date_last_updated=get_current_datetime(),
            description=f"Asset discovered from QRadar event: {event.event_name}",
            scanning_tool="QRadar SIEM",
            is_latest_scan=True,
            notes=f"Log Source: {log_source}",
        )

    def _discover_asset_from_event(
        self, event: QRadarEvent, ip_address: str, discovered_asset_ips: Dict[str, IntegrationAsset]
    ) -> None:
        """
        Discover and add asset from event if valid.

        Args:
            event: QRadarEvent object
            ip_address: IP address to create asset from
            discovered_asset_ips: Dictionary to store discovered assets
        """
        if ip_address not in discovered_asset_ips:
            asset = self._create_asset_from_event(event, ip_address)
            # Only add asset if it has a valid name (not empty, not "Unknown")
            if asset.name and asset.name not in ["Unknown", ""]:
                discovered_asset_ips[ip_address] = asset
                logger.debug(f"  -> Discovered asset: {ip_address} (name: {asset.name})")
            else:
                logger.debug(f"  -> Skipping invalid asset: {ip_address} (name: {asset.name})")

    def fetch_findings(self, plan_id: int, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Fetch findings from QRadar events.

        Transforms QRadar security events into RegScale findings/issues with:
        - Event classification and severity mapping
        - Asset correlation
        - Control mapping based on event categories
        - Evidence linking

        Also discovers assets during finding processing and stores them
        in self.discovered_assets for use by sync_findings_and_assets.

        Args:
            plan_id: RegScale security plan ID

        Yields:
            IntegrationFinding objects for each security event
        """
        logger.info(f"Fetching findings from QRadar events for plan {plan_id}...")

        finding_count = 0
        discovered_asset_ips: Dict[str, IntegrationAsset] = {}

        try:
            # Fetch events from QRadar
            events = self._fetch_qradar_events()
            if not events:
                logger.warning(f"No QRadar events found for plan {plan_id}")
                return

            for event in events:
                # Log event details for debugging
                logger.debug(
                    f"Processing event: {event.event_name} | "
                    f"Source: {event.source_ip or 'N/A'} | "
                    f"Dest: {event.dest_ip or 'N/A'} | "
                    f"Severity: {event.get_severity_value()}/10 | "
                    f"Category: {event.category}"
                )

                # Discover assets from this event
                if event.is_valid_source_asset() and event.source_ip:
                    self._discover_asset_from_event(event, event.source_ip, discovered_asset_ips)

                if event.is_valid_dest_asset() and event.dest_ip:
                    self._discover_asset_from_event(event, event.dest_ip, discovered_asset_ips)

                # Create finding from event
                finding = self._create_finding_from_event(event)
                logger.debug(f"  -> Created finding: {finding.title}")
                yield finding
                finding_count += 1

            # Store discovered assets for use by sync_findings_and_assets
            if hasattr(self, "discovered_assets"):
                self.discovered_assets.extend(discovered_asset_ips.values())

            logger.info(
                f"Fetched {finding_count} findings and discovered {len(discovered_asset_ips)} unique assets from QRadar"
            )

        except Exception as e:
            logger.error(f"Error fetching findings from QRadar: {str(e)}")
            raise

    def get_discovered_assets(self) -> Iterator[IntegrationAsset]:
        """
        Yield discovered assets that were found during finding processing.

        This is a helper method used by sync_findings_and_assets to iterate
        over assets discovered while processing findings.

        Yields:
            IntegrationAsset objects for each discovered asset
        """
        yield from self.discovered_assets

    def sync_findings_and_assets(self, **kwargs) -> tuple[int, int]:
        """
        Sync both findings and discovered assets from QRadar.

        This method first discovers assets from QRadar events, creates them in RegScale,
        then processes the findings and links them to the created assets.

        Also collects evidence from QRadar events and uploads as JSONL.GZ files
        to RegScale as SSP attachments or Evidence records.

        This follows the AWS Security Hub pattern where assets are automatically
        discovered and synced as part of the findings sync process.

        Args:
            **kwargs: Additional keyword arguments passed to underlying methods
                - create_evidence: Create evidence files (default: True)
                - evidence_as_attachment: Upload as SSP attachment vs Evidence record (default: True)
                - evidence_control_ids: List of control IDs to link evidence to (default: None)

        Returns:
            tuple[int, int]: Tuple of (findings_processed, assets_processed)
        """
        from regscale.core.app.utils.app_utils import create_progress_object

        logger.info("Starting QRadar findings and assets sync...")

        # Create progress bar context for the entire operation
        with create_progress_object() as progress:
            # Store progress object for use by nested methods
            self.finding_progress = progress

            # First, fetch findings to discover assets (but don't sync findings yet)
            logger.info("Discovering assets from QRadar events...")

            # Reset discovered assets for this run
            self.discovered_assets.clear()
            self.processed_asset_identifiers.clear()

            # Fetch findings to discover assets - store them to avoid re-fetching
            findings_list = list(self.fetch_findings(self.plan_id, **kwargs))

            # Sync the discovered assets first
            if self.discovered_assets:
                logger.info(f"Creating {len(self.discovered_assets)} assets discovered from findings...")
                logger.debug(f"Assets to create: {[asset.identifier for asset in self.discovered_assets]}")
                self.num_assets_to_process = len(self.discovered_assets)
                assets_processed = self.update_regscale_assets(self.get_discovered_assets())
                logger.info(f"Successfully created {assets_processed} assets in RegScale")
            else:
                logger.info("No assets discovered from findings")
                assets_processed = 0

            # Now process the findings we already fetched (avoid double-fetching)
            logger.info(f"Now syncing {len(findings_list)} findings with created assets...")
            logger.info(f"Integration type: {self.type}")
            logger.info(f"Scanner title: {self.title}")

            # Log first few findings for debugging
            if findings_list:
                logger.info("Sample findings to be processed:")
                for i, finding in enumerate(findings_list[:3]):
                    logger.info(
                        f"  Finding {i + 1}: {finding.title} | "
                        f"Severity: {finding.severity} | "
                        f"Asset: {finding.asset_identifier} | "
                        f"Status: {finding.status}"
                    )

            findings_processed = self.update_regscale_findings(iter(findings_list))
            logger.info(f"Successfully processed {findings_processed} findings in RegScale")

            # Collect and upload evidence files
            create_evidence = kwargs.get("create_evidence", True)
            if create_evidence and self._qradar_client is not None:
                logger.info("Collecting QRadar event evidence...")
                evidence_uploaded = self._collect_and_upload_evidence(
                    evidence_as_attachment=kwargs.get("evidence_as_attachment", True),
                    control_ids=kwargs.get("evidence_control_ids"),
                )
                if evidence_uploaded:
                    logger.info("Successfully uploaded QRadar evidence files")
                else:
                    logger.warning("No evidence files were uploaded")

            # Log completion summary
            logger.info(
                f"QRadar sync completed successfully: {findings_processed} findings processed, {assets_processed} assets created"
            )

        return findings_processed, assets_processed

    def _create_finding_from_event(self, event: QRadarEvent) -> IntegrationFinding:
        """
        Create an IntegrationFinding from a QRadar event.

        Args:
            event: QRadarEvent object

        Returns:
            IntegrationFinding object
        """
        # Extract event fields from validated Pydantic model
        event_name = event.event_name
        log_source = event.log_source
        source_ip = event.source_ip or ""
        dest_ip = event.dest_ip or ""
        username = event.username or ""
        category = event.category or "Unknown"
        event_count = str(event.event_count)

        # Convert event_time from milliseconds to ISO format datetime string
        from datetime import datetime, timezone

        if event.event_time:
            # QRadar event_time is in milliseconds since epoch
            event_datetime = datetime.fromtimestamp(event.event_time / 1000, tz=timezone.utc)
            event_time_str = event_datetime.isoformat()
        else:
            # Fallback to current time if no event_time
            event_time_str = datetime.now(timezone.utc).isoformat()

        # Determine severity from magnitude field (QRadar severity scale 0-10)
        raw_magnitude = event.get_severity_value()
        magnitude_str = str(raw_magnitude)
        severity = self.finding_severity_map.get(magnitude_str, IssueSeverity.Moderate)

        # Determine priority based on same QRadar severity
        priority = self.finding_priority_map.get(magnitude_str, "Medium")

        # Map category to controls
        control_labels = self._map_category_to_controls(category)

        # Build description with event details
        description = self._build_event_description(event)

        # Build comprehensive evidence from event data
        evidence = self._build_event_evidence(event)

        # Determine issue status
        status = IssueStatus.Open

        # Create stable external_id that doesn't change between syncs
        # Use event_name, source_ip, and category to uniquely identify this type of security event
        # This allows proper deduplication - same event type from same source updates existing issue
        stable_id_base = f"{event_name}:{source_ip}:{category}"
        external_id = f"qradar-{abs(hash(stable_id_base))}"

        # Create plugin_id for vulnerability identification
        # Group by event type and source IP for better organization
        plugin_id = f"qradar-{(event_name or 'unknown').lower().replace(' ', '-')}"

        # Create finding
        return IntegrationFinding(
            title=f"{event_name} from {source_ip or 'Unknown Source'}",
            asset_identifier=source_ip or dest_ip or "",
            ip_address=source_ip or None,
            dns=username if username and "@" in username else None,
            severity=severity,
            status=status,
            priority=priority,
            category=category,
            plugin_name="QRadar SIEM",
            plugin_id=plugin_id,
            description=description,
            control_labels=control_labels,
            source_report=f"QRadar - {log_source}",
            identification="Security Event",
            date_created=event_time_str,
            first_seen=event_time_str,
            last_seen=event_time_str,
            issue_type="Risk",
            external_id=external_id,
            # Store additional QRadar-specific data in extra_data
            extra_data={
                "event_name": event_name,
                "log_source": log_source,
                "event_count": event_count,
                "source_ip": source_ip,
                "source_port": str(event.source_port) if event.source_port else "",
                "dest_ip": dest_ip,
                "dest_port": str(event.dest_port) if event.dest_port else "",
                "username": username,
                "low_level_category": category,
                "magnitude": raw_magnitude,
            },
            # Add to observations for visibility
            observations=f"Event Count: {event_count}",
            evidence=evidence,
        )

    def _fetch_qradar_events(self) -> List[QRadarEvent]:
        """
        Fetch events from QRadar within the configured time window.

        Returns:
            List of validated QRadarEvent objects

        Raises:
            Exception: If QRadar API call fails
        """
        # Format times for QRadar API
        start_time_str = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = self.end_time.strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"Fetching QRadar events from {start_time_str} to {end_time_str}")

        try:
            # Use the QRadar API client to fetch events
            raw_events = self.qradar_client.get_events(
                start_time=start_time_str,
                end_time=end_time_str,
                filters={},  # Could add severity filter here
                limit=self.max_events,
            )

            logger.info(f"Retrieved {len(raw_events)} raw events from QRadar")

            # Validate and parse events with Pydantic
            validated_events = []
            for idx, raw_event in enumerate(raw_events):
                try:
                    event = QRadarEvent(**raw_event)
                    validated_events.append(event)
                except Exception as e:
                    if idx == 0:
                        # Log first event structure for debugging
                        logger.debug(f"First event structure: {raw_event}")
                    logger.warning(f"Skipping invalid event at index {idx}: {str(e)}")
                    continue

            logger.info(f"Successfully validated {len(validated_events)} events")
            return validated_events

        except Exception as e:
            logger.error(f"Failed to fetch events from QRadar: {str(e)}")
            raise

    def _map_category_to_controls(self, category: str) -> List[str]:
        """
        Map QRadar event category to NIST 800-53 controls.

        Args:
            category: QRadar low-level category

        Returns:
            List of control IDs
        """
        # Category to control mapping
        category_mapping = {
            "authentication": ["AC-2", "AC-7", "IA-2", "IA-4"],
            "authorization": ["AC-3", "AC-6"],
            "access": ["AC-2", "AC-3", "AC-17"],
            "logon": ["AC-2", "AC-7", "IA-2"],
            "logoff": ["AC-2", "AC-12"],
            "account": ["AC-2", "IA-4"],
            "audit": ["AU-2", "AU-3", "AU-6", "AU-12"],
            "logging": ["AU-2", "AU-3", "AU-12"],
            "firewall": ["SC-7", "AC-4"],
            "intrusion": ["SI-4", "SI-7"],
            "malware": ["SI-3", "SI-7"],
            "vulnerability": ["RA-5", "SI-2"],
            "configuration": ["CM-2", "CM-6"],
            "system": ["SI-2", "SI-4"],
            "network": ["SC-7", "AC-17"],
            "encryption": ["SC-8", "SC-13"],
            "data": ["SC-28", "MP-4"],
            "incident": ["IR-4", "IR-6"],
        }

        # Normalize category to lowercase for matching
        category_lower = category.lower()

        # Find matching controls
        controls = []
        for keyword, control_list in category_mapping.items():
            if keyword in category_lower:
                controls.extend(control_list)

        # Remove duplicates and sort
        controls = sorted(set(controls))

        # Return default controls if no match found
        if not controls:
            controls = ["AU-6"]  # Default to audit and monitoring

        return controls

    def _build_event_description(self, event: QRadarEvent) -> str:
        """
        Build a detailed description from QRadar event data.

        Args:
            event: QRadarEvent object

        Returns:
            Formatted description string
        """
        description_parts = []

        # Event overview
        description_parts.append(f"**Event:** {event.event_name}")

        # Source and destination
        if event.source_ip:
            source_str = (
                f"{event.source_ip}:{event.source_port}"
                if event.source_port and event.source_port != 0
                else event.source_ip
            )
            description_parts.append(f"**Source:** {source_str}")

        if event.dest_ip:
            dest_str = (
                f"{event.dest_ip}:{event.dest_port}" if event.dest_port and event.dest_port != 0 else event.dest_ip
            )
            description_parts.append(f"**Destination:** {dest_str}")

        # User information
        if event.username:
            description_parts.append(f"**User:** {event.username}")

        # Event metadata
        description_parts.append(f"**Log Source:** {event.log_source}")
        description_parts.append(f"**Category:** {event.category}")
        description_parts.append(f"**Event Count:** {event.event_count}")
        description_parts.append(f"**Severity/Magnitude:** {event.get_severity_value()}")

        # Time information
        description_parts.append(f"**Time:** {event.event_time}")

        # Join all parts
        return "<br>".join(description_parts)

    def _build_network_evidence(self, event: QRadarEvent) -> List[str]:
        """
        Build network evidence section.

        Args:
            event: QRadarEvent object

        Returns:
            List of evidence strings
        """
        evidence_parts = ["## Network Evidence"]

        if event.source_ip:
            source_info = f"{event.source_ip}"
            if event.source_port and event.source_port != 0:
                source_info += f":{event.source_port}"
            evidence_parts.append(f"- **Source Address:** {source_info}")

        if event.dest_ip:
            dest_info = f"{event.dest_ip}"
            if event.dest_port and event.dest_port != 0:
                dest_info += f":{event.dest_port}"
            evidence_parts.append(f"- **Destination Address:** {dest_info}")

        return evidence_parts

    def _build_extra_fields_evidence(self, extra_fields: Dict[str, Any]) -> List[str]:
        """
        Build evidence from extra fields (payload and metadata).

        Args:
            extra_fields: Dictionary of extra fields from Pydantic model

        Returns:
            List of evidence strings
        """
        evidence_parts = []
        payload_fields = ["payload", "utf8_payload", "message", "event_data"]
        has_payload = False

        # Process payload fields
        for field_name in payload_fields:
            if field_name in extra_fields and extra_fields[field_name]:
                if not has_payload:
                    evidence_parts.append("\n## Raw Event Data")
                    has_payload = True

                payload_value = extra_fields[field_name]
                # Limit payload size to avoid overly large evidence fields
                if isinstance(payload_value, str) and len(payload_value) > 5000:
                    payload_value = payload_value[:5000] + "\n... (truncated)"

                evidence_parts.append(f"- **{field_name.replace('_', ' ').title()}:**\n```\n{payload_value}\n```")

        # Process other metadata fields
        other_fields = {k: v for k, v in extra_fields.items() if k not in payload_fields and v is not None}
        if other_fields:
            evidence_parts.append("\n## Additional Event Metadata")
            for key, value in sorted(other_fields.items()):
                if not key.startswith("_"):
                    evidence_parts.append(f"- **{key.replace('_', ' ').title()}:** {value}")

        return evidence_parts

    def _build_event_evidence(self, event: QRadarEvent) -> str:
        """
        Build comprehensive evidence documentation from QRadar event data.

        This method extracts all relevant evidence from the QRadar event including
        network information, user context, event metadata, and any raw payload data.

        Args:
            event: QRadarEvent object

        Returns:
            Formatted evidence string with all available event data
        """
        evidence_parts = []

        # Network Evidence
        evidence_parts.extend(self._build_network_evidence(event))

        # Identity Evidence
        if event.username:
            evidence_parts.append("\n## Identity Evidence")
            evidence_parts.append(f"- **Username:** {event.username}")

        # Event Context
        evidence_parts.append("\n## Event Context")
        evidence_parts.append(f"- **Event Name:** {event.event_name}")
        evidence_parts.append(f"- **Log Source:** {event.log_source}")
        evidence_parts.append(f"- **Category:** {event.category}")
        evidence_parts.append(f"- **Severity/Magnitude:** {event.get_severity_value()}/10")
        evidence_parts.append(f"- **Event Count:** {event.event_count}")

        # Timestamp Evidence
        if event.event_time:
            evidence_parts.append(f"- **Event Time:** {event.event_time}")

        # Extract any additional payload data from extra fields
        if hasattr(event, "__pydantic_extra__") and event.__pydantic_extra__:
            evidence_parts.extend(self._build_extra_fields_evidence(event.__pydantic_extra__))

        # Add QRadar-specific attribution
        evidence_parts.append("\n---")
        evidence_parts.append("*Evidence collected from QRadar SIEM*")

        return "\n".join(evidence_parts)

    def _collect_and_upload_evidence(
        self, evidence_as_attachment: bool = True, control_ids: Optional[List[int]] = None
    ) -> bool:
        """
        Collect QRadar events and upload as evidence files.

        Args:
            evidence_as_attachment: If True, upload as SSP attachment; if False, create Evidence record
            control_ids: Optional list of control IDs to link evidence to

        Returns:
            bool: True if evidence was successfully uploaded
        """
        try:
            # Fetch events again for evidence (they were already fetched for findings)
            # In a production scenario, we'd cache these events to avoid re-fetching
            events = self._fetch_qradar_events()

            if not events:
                logger.info("No events to collect for evidence")
                return False

            # Import evidence collector and API
            from regscale.integrations.commercial.qradar.qradar_evidence import QRadarEvidenceCollector
            from regscale.core.app.api import Api

            # Extract control IDs from the events if not provided
            if control_ids is None:
                control_ids = self._extract_control_ids_from_events(events)

            # Create API instance for evidence upload
            api = Api()

            # Create evidence collector
            collector = QRadarEvidenceCollector(
                plan_id=self.plan_id,
                api=api,
                events=events,
                control_ids=control_ids,
                create_ssp_attachment=evidence_as_attachment,
            )

            # Collect and upload evidence
            success = collector.collect_and_upload_evidence()

            return success

        except Exception as e:
            logger.error(f"Failed to collect and upload evidence: {e}")
            logger.debug(f"Failed to collect and upload evidence: {e}", exc_info=True)
            return False

    def _extract_control_ids_from_events(self, events: List[QRadarEvent]) -> List[int]:
        """
        Extract unique control IDs from events based on their categories.

        Args:
            events: List of QRadarEvent objects

        Returns:
            List of control IDs
        """
        # This would map event categories to actual control IDs from RegScale
        # For now, return empty list - this can be enhanced later
        # to fetch control IDs from RegScale based on control_labels
        return []
