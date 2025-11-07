"""
This module contains the code for the MainContext class. This class is
a context manager that supervises the execution of the main body of the process.

On entrance, it will verify the process manifest.

Upon exit, it will convert the step report into the run report. It will also
evaluate the ultimate status of the process—success if no exceptions were
raised, failure otherwise.

Without this context, the output manifest and run report would not be
generated at the end of the process.
"""

from __future__ import annotations

import datetime
import logging
import os
import pathlib
import warnings
from types import TracebackType
from typing import Callable, Optional, Type, Union
from urllib.parse import urlparse

import boto3
from thoughtful.supervisor.event_bus import ArtifactsUploadedEvent, EventBus
from thoughtful.supervisor.event_bus import NewManifestEvent, RunStatusChangeEvent
from thoughtful.supervisor.manifest import Manifest
from thoughtful.supervisor.reporting.report_builder import ReportBuilder
from thoughtful.supervisor.reporting.status import Status
from thoughtful.supervisor.telemetry.config import TelemetryContext, setup_telemetry
from thoughtful.supervisor.telemetry.config import shutdown_telemetry

logger = logging.getLogger(__name__)


class MainContext:
    """
    Supervises an entire digital worker run and generates a work report
    and drift report for the run from the digital worker's manifest.

    You can optionally specify a callback function that will be run when
    this context is finished via the `callback` param in the constructor. A
    callback is a function that is invoked with two parameters: the
    current context (as the `MainContext` instance) and the `Report`
    generated from this digital worker's run.

    For example:

    .. code-block:: python

        def print_work_report(
            ctx: MainContext,
            work_report: Report
        ):
            print(work_report.__json__())

        def main()
            # ...

        with supervise(callback=print_work_report):
            main()
    """

    def __init__(
        self,
        report_builder: ReportBuilder,
        manifest: Union[Manifest, str, pathlib.Path],
        output_dir: Union[str, pathlib.Path],
        event_bus: EventBus,
        upload_uri: Optional[str] = None,
        callback: Optional[Callable] = None,
        is_robocorp_multistep_run: bool = False,
        otlp_config: Optional[dict[str, Union[str, dict[str, str]]]] = None,
    ):
        """
        Args:
            report_builder (ReportBuilder): A ReportBuilder object that will
                receive the step reports and provide the run report.
                messages and logs throughout the process execution.
            manifest (str, Path): A pathlike object that points to the manifest
                file for the process.
            output_dir (str, Path): A pathlike object that points to the output
                directory for the process. This will receive the run report and
                output manifest.
            event_bus (EventBus): This instance will send events, such as
                a new manifest or a change in the run's status, to this bus.
            upload_uri (str, optional): A URI to upload the output files to.
            callback (callable, optional): a function that is invoked with three
                parameters: the current context (as the `MainContext` instance)
                and the `Report` generated from this digital worker's run.
            is_robocorp_multistep_run (bool, optional): A flag to indicate if this is a
                Robocorp multi-step run or not. If it is, the run status will not be
                updated when the context is entered or exited.
            otlp_config (dict, optional): Configuration for OpenTelemetry tracing.
                Should contain 'endpoint' (str) and optionally 'headers' (dict[str, str]).
        """
        self.report_builder = report_builder
        self.output_path = pathlib.Path(output_dir)
        self.upload_uri = upload_uri

        self.manifest_path = (
            manifest if isinstance(manifest, (str, pathlib.Path)) else None
        )
        self.manifest = self._parse_manifest(manifest)
        self.callback = callback
        self.event_bus = event_bus
        self.is_robocorp_multistep_run = is_robocorp_multistep_run
        self._otlp_config = otlp_config
        self._telemetry_context: Optional[TelemetryContext] = None

    @staticmethod
    def _parse_manifest(
        manifest: Union[Manifest, str, pathlib.Path],
    ) -> Optional[Manifest]:
        if isinstance(manifest, Manifest):
            return manifest
        manifest_path = pathlib.Path(manifest)
        try:
            manifest = Manifest.from_file(manifest_path)
            return manifest
        except Exception:
            logger.exception("warning: could not read manifest")
        return None

    def __enter__(self) -> MainContext:
        """
        Logic for when this context is first started. Attempts to load the
        manifest and returns itself as the context.

        Returns:
            MainContext: This instance.
        """
        if self.manifest:
            self.event_bus.emit(
                NewManifestEvent(
                    manifest=self.manifest,
                )
            )

        if not self.is_robocorp_multistep_run:
            self._stream_run_status_change(Status.RUNNING)

        # Initialize all OpenTelemetry telemetry components (tracing, logging, metrics)
        try:
            self._telemetry_context = setup_telemetry(self._otlp_config, self.manifest)
        except Exception as e:
            logger.error("Failed to initialize telemetry: %s", str(e))
            # Continue without telemetry - context will be None
            self._telemetry_context = None

        return self

    def set_run_status(self, status: Union[Status, str], message: str = None) -> None:
        """
        Sets the run status of the process. This is the final status of the
        process, and will be used to determine the status of the run report.

        Args:
            status (Union[Status, str]): The status to set.
            message (str): The message for the status. Required. The use of None is deprecated.
        """
        if message is not None and len(message) > 125:
            warnings.warn(
                "Status Messages greater than 125 characters will be truncated in Empower "
            )
        # TODO: Next major version increase, make this argument required
        if message is None or not message.strip():
            warnings.warn(
                message="set_run_status missing message argument. This will become required in a future release.",
                category=DeprecationWarning,
                stacklevel=2,
            )

        self.report_builder.set_run_status(status, message)
        self._stream_run_status_change(status, message)

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        """
        Runs when the context is about to close, whether caused
        by a raised Exception or now.

        Returns:
            bool: True if the parent caller should ignore the
                Exception raised before entering this function
                (if any), False otherwise.
        """
        if exc_type:
            self.report_builder.run_had_exception = True
        work_report = self.report_builder.to_report()

        if not self.is_robocorp_multistep_run:
            self._stream_run_status_change(
                work_report.status, work_report.status_message
            )

        # Create the output directory if it doesn't already exist
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Write the work report
        work_report_path = self._safe_report_path(file_prefix="run-report")
        work_report.write(work_report_path)

        # Write the manifest back out as a JSON file
        if self.manifest:
            manifest_json_path = self.output_path / "manifest.json"
            self.manifest.write_to_json_file(manifest_json_path)

        # Run the user-defined callback
        if self.callback:
            self.callback(self, work_report)

        # Upload output files to S3
        if self.upload_uri:
            try:
                self._upload_output_files_to_s3(self.upload_uri)
            except Exception:
                logger.exception("Failed to upload output files to S3")
        elif os.environ.get("ROBOCORP_HOME") is None:
            logger.warning(
                "SUPERVISOR_ARTIFACT_UPLOAD_URI is not set. Artifacts"
                " will not be uploaded to S3."
            )

        # Shutdown telemetry components and record workflow completion
        if self._telemetry_context:
            shutdown_telemetry(
                self._telemetry_context,
                exc_type,
                exc_val,
                exc_tb,
            )

        return False

    # Metrics are disabled - using traces for dashboards instead
    # These properties are kept for backward compatibility but will always return None/False
    # @property
    # def meter(self):
    #     """
    #     Get the OpenTelemetry meter for creating metrics.
    #
    #     Returns:
    #         The meter instance if metrics are initialized, None otherwise.
    #     """
    #     return self._telemetry_context.meter if self._telemetry_context else None
    #
    # @property
    # def metrics_available(self):
    #     """
    #     Check if OpenTelemetry metrics are available.
    #
    #     Returns:
    #         True if metrics are initialized, False otherwise.
    #     """
    #     return (
    #         self._telemetry_context is not None
    #         and self._telemetry_context.meter is not None
    #     )

    def _stream_run_status_change(
        self, status: Status, status_message: str = None
    ) -> None:
        """
        Post a status change to the stream callback if it exists.
        """
        self.event_bus.emit(
            RunStatusChangeEvent(status=status, status_message=status_message)
        )

    def _upload_output_files_to_s3(self, upload_uri: str) -> None:
        """
        It uploads all files in the output directory to S3. It requires the
        environment variable `SUPERVISOR_ARTIFACT_UPLOAD_URI` to be set with
        the S3 URI to upload the files to.

        Args:
            upload_uri (str): The S3 URI to upload the files to.
        """
        s3_client = boto3.client("s3")
        parsed_upload_uri = urlparse(upload_uri.strip())
        bucket = parsed_upload_uri.hostname
        path = parsed_upload_uri.path.strip("/")

        for file in self.output_path.glob("*"):
            try:
                if file.is_file():
                    obj = f"{path}/{file.name}" if path else file.name
                    s3_client.upload_file(str(file), bucket, obj)
            except Exception:
                logger.exception(f"Failed to upload {file} to S3")
        self.event_bus.emit(ArtifactsUploadedEvent(output_uri=upload_uri))

    def _safe_report_path(self, file_prefix: str) -> pathlib.Path:
        """
        A ``pathlib.Path`` instance that points to a new work report writable
        location that is safe across all OSes.

        Returns:
            pathlib.Path: The path to the new report to be written.
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H%M%S"
        )
        filename = f"{file_prefix}-{timestamp}.json"

        # Remove any characters from the timestamp that OSes don't like
        invalid_chars = [":", "*", "?", '"', "<", ">" "|", "'"]
        for char in invalid_chars:
            filename = filename.replace(char, "_")

        return self.output_path / filename
