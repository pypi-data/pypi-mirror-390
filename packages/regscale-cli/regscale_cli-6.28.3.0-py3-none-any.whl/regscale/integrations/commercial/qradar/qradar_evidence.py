"""QRadar evidence collection and upload module."""

import gzip
import json
import logging
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional

from regscale.models.regscale_models import Evidence
from regscale.models.regscale_models.file import File
from regscale.models.integration_models.qradar_models.event import QRadarEvent

logger = logging.getLogger("regscale")


class QRadarEvidenceCollector:
    """
    Collect and upload QRadar security event evidence to RegScale.

    This class creates JSONL.GZ evidence files containing QRadar security events
    and uploads them as SSP attachments or Evidence records in RegScale.

    Follows the AWS integration pattern for evidence collection.
    """

    def __init__(
        self,
        plan_id: int,
        api: Any,  # RegScale API instance from Application
        events: List[QRadarEvent],
        control_ids: Optional[List[int]] = None,
        create_ssp_attachment: bool = True,
    ):
        """
        Initialize QRadar evidence collector.

        Args:
            plan_id: RegScale Security Plan ID
            api: RegScale API client instance from Application().api
            events: List of QRadarEvent objects to include in evidence
            control_ids: Optional list of control IDs to link evidence to
            create_ssp_attachment: If True, create SSP attachment (default: True)
        """
        self.plan_id = plan_id
        self.api = api
        self.events = events
        self.control_ids = control_ids or []
        self.create_ssp_attachment = create_ssp_attachment

    def collect_and_upload_evidence(self) -> bool:
        """
        Collect QRadar events and upload as evidence file.

        Returns:
            bool: True if evidence was successfully uploaded
        """
        if not self.events:
            logger.info("No QRadar events to include in evidence file")
            return False

        try:
            # Create evidence file
            evidence_file_path = self._create_evidence_file()

            if self.create_ssp_attachment:
                success = self._create_ssp_attachment_with_evidence(evidence_file_path)
            else:
                success = self._create_evidence_record_with_file(evidence_file_path)

            # Clean up temporary file
            if os.path.exists(evidence_file_path):
                os.remove(evidence_file_path)
                logger.debug("Cleaned up temporary evidence file: %s", evidence_file_path)

            return success

        except Exception as exc:
            logger.error("Failed to collect and upload QRadar evidence: %s", exc)
            logger.debug("Failed to collect and upload QRadar evidence: %s", exc, exc_info=True)
            return False

    def _create_evidence_file(self) -> str:
        """
        Create JSONL.GZ evidence file with QRadar security events.

        Returns:
            str: Path to created evidence file
        """
        evidence_file = self._get_evidence_file_path()

        try:
            with gzip.open(evidence_file, "wt", encoding="utf-8") as f:
                # Write metadata record
                self._write_metadata(f)

                # Write summary record
                self._write_event_summary(f)

                # Write individual event records
                self._write_event_records(f)

            logger.info("Created QRadar evidence file: %s (%d events)", evidence_file, len(self.events))
            return evidence_file

        except Exception as exc:
            logger.error("Failed to create QRadar evidence file: %s", exc)
            logger.debug("Failed to create QRadar evidence file: %s", exc, exc_info=True)
            raise

    def _get_evidence_file_path(self) -> str:
        """Generate evidence file path with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(tempfile.gettempdir(), f"qradar_evidence_{timestamp}.jsonl.gz")

    def _write_metadata(self, file_handle) -> None:
        """Write metadata record to evidence file."""
        metadata = {
            "type": "metadata",
            "timestamp": datetime.now().isoformat(),
            "source": "QRadar SIEM",
            "security_plan_id": self.plan_id,
            "event_count": len(self.events),
            "evidence_framework": "Security Event Logging",
        }
        file_handle.write(json.dumps(metadata) + "\n")

    def _write_event_summary(self, file_handle) -> None:
        """Write event summary statistics to evidence file."""
        # Calculate summary statistics
        severity_counts: Dict[int, int] = {}
        category_counts: Dict[str, int] = {}
        source_ips: set[str] = set()
        log_sources: set[str] = set()

        for event in self.events:
            # Count severity levels
            severity = event.get_severity_value()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

            # Count categories
            category = event.category or "Unknown"
            category_counts[category] = category_counts.get(category, 0) + 1

            # Track unique source IPs
            if event.source_ip:
                source_ips.add(event.source_ip)

            # Track unique log sources
            if event.log_source:
                log_sources.add(event.log_source)

        summary = {
            "type": "event_summary",
            "total_events": len(self.events),
            "severity_distribution": severity_counts,
            "category_distribution": category_counts,
            "unique_source_ips": len(source_ips),
            "unique_log_sources": len(log_sources),
            "log_sources": sorted(log_sources),
        }
        file_handle.write(json.dumps(summary) + "\n")

    def _write_event_records(self, file_handle) -> None:
        """Write individual event records to evidence file."""
        for event in self.events:
            event_record = self._build_event_record(event)
            file_handle.write(json.dumps(event_record, default=str) + "\n")

    def _build_event_record(self, event: QRadarEvent) -> Dict[str, Any]:
        """
        Build event record for evidence file.

        Args:
            event: QRadarEvent object

        Returns:
            Dict containing event data
        """
        record = {
            "type": "security_event",
            "event_name": event.event_name,
            "log_source": event.log_source,
            "category": event.category,
            "severity": event.get_severity_value(),
            "magnitude": event.magnitude,
            "event_count": event.event_count,
            "source_ip": event.source_ip,
            "source_port": event.source_port,
            "destination_ip": event.dest_ip,
            "destination_port": event.dest_port,
            "username": event.username,
            "event_time": event.event_time,
        }

        # Include any extra fields from Pydantic model
        if hasattr(event, "__pydantic_extra__") and event.__pydantic_extra__:
            # Type ignore since we're adding a dict value which is valid for JSON serialization
            record["additional_fields"] = event.__pydantic_extra__  # type: ignore[assignment]

        return record

    def _create_ssp_attachment_with_evidence(self, evidence_file_path: str) -> bool:
        """
        Create SSP attachment with QRadar evidence.

        Args:
            evidence_file_path: Path to evidence file

        Returns:
            bool: True if upload was successful
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"qradar_evidence_{timestamp}.jsonl.gz"

            # Read the compressed file
            with open(evidence_file_path, "rb") as f:
                file_data = f.read()

            # Upload file to RegScale
            result = File.upload_file_to_regscale(
                file_name=file_name,
                parent_id=self.plan_id,
                parent_module="securityplans",
                api=self.api,
                file_data=file_data,
                tags="qradar,siem,security,events,compliance,automated",
            )

            success = bool(result)
            if success:
                logger.info("Successfully uploaded QRadar evidence file: %s", file_name)
                # Note: SSP attachments don't return IDs from upload_file_to_regscale
                # Control linking would need additional implementation
            else:
                logger.error("Failed to upload QRadar evidence file")

            return success

        except Exception as exc:
            logger.error("Failed to create SSP attachment: %s", exc)
            logger.debug("Failed to create SSP attachment: %s", exc, exc_info=True)
            return False

    def _create_evidence_record_with_file(self, evidence_file_path: str) -> bool:
        """
        Create Evidence record and upload file.

        Args:
            evidence_file_path: Path to evidence file

        Returns:
            bool: True if creation was successful
        """
        try:
            # Create Evidence record
            date_str = datetime.now().strftime("%Y-%m-%d")
            evidence_name = f"QRadar Security Events - {date_str}"

            evidence_description = (
                f"QRadar SIEM security events collected on {date_str}. "
                f"Contains {len(self.events)} security events from QRadar. "
                "Evidence includes event details, severity information, and source/destination data."
            )

            evidence_record = Evidence(  # type: ignore[call-arg]
                security_plan_id=self.plan_id,
                name=evidence_name,
                description=evidence_description,
                evidence_type="Log Files",
                status="Active",
                date_collected=date_str,
            )

            created_evidence = evidence_record.create()
            logger.info("Created Evidence record: %s (ID: %s)", evidence_name, created_evidence.id)

            # Upload file to evidence record
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"qradar_evidence_{timestamp}.jsonl.gz"

            with open(evidence_file_path, "rb") as f:
                file_data = f.read()

            result = File.upload_file_to_regscale(
                file_name=file_name,
                parent_id=created_evidence.id,
                parent_module="evidence",
                api=self.api,
                file_data=file_data,
                tags="qradar,siem,security,events,compliance,automated",
            )

            file_success = bool(result)
            if file_success:
                logger.info("Successfully uploaded file to Evidence record %d", created_evidence.id)

                # Link evidence to controls
                if self.control_ids:
                    self._link_evidence_to_controls(created_evidence.id)
            else:
                logger.error("Failed to upload file to Evidence record %d", created_evidence.id)

            return file_success

        except Exception as exc:
            logger.error("Failed to create Evidence record: %s", exc)
            logger.debug("Failed to create Evidence record: %s", exc, exc_info=True)
            return False

    def _link_evidence_to_controls(self, evidence_id: int) -> None:
        """
        Link evidence record to specified control IDs.

        Args:
            evidence_id: Evidence record ID
        """
        try:
            for control_id in self.control_ids:
                try:
                    # Link evidence to control
                    self.api.link_evidence_to_control(self.plan_id, evidence_id, control_id)
                    logger.info("Linked evidence %d to control %d", evidence_id, control_id)
                except Exception as exc:
                    logger.warning("Failed to link evidence %d to control %d: %s", evidence_id, control_id, exc)
        except Exception as exc:
            logger.error("Error linking evidence to controls: %s", exc)
            logger.debug("Error linking evidence to controls: %s", exc, exc_info=True)
