"""Log processors with masking support for Brizz SDK."""

import logging

from opentelemetry.attributes import BoundedAttributes
from opentelemetry.sdk._logs import LogData
from opentelemetry.sdk._logs._internal.export import (
    BatchLogRecordProcessor,
    LogExporter,
    SimpleLogRecordProcessor,
)

from brizz._internal.models import AttributesMaskingRule, EventMaskingConfig

from ...config import BrizzConfig
from ...masking.patterns import DEFAULT_PII_PATTERN_ENTRIES
from ...masking.utils import mask_attributes, mask_value

logger = logging.getLogger("brizz.masking")

# Default log masking rules
DEFAULT_LOG_MASKING_RULES = [
    AttributesMaskingRule(
        attribute_pattern="event.name",
        mode="partial",
        patterns=DEFAULT_PII_PATTERN_ENTRIES,
    )
]


class BrizzSimpleLogRecordProcessor(SimpleLogRecordProcessor):
    """Simple log record processor with masking and context support."""

    def __init__(
        self,
        exporter: LogExporter,
        config: BrizzConfig,
    ) -> None:
        super().__init__(exporter)
        self.config = config

    def on_emit(self, log_data: LogData) -> None:
        """Emit a log record after applying masking and context association."""
        # Apply masking if configured
        masking_config = getattr(self.config.masking, "event_masking", None) if self.config.masking else None
        if masking_config:
            log_data = _mask_log(log_data, masking_config)

        # Note: Context properties are now added directly in emit_event() method
        # to ensure proper context capture at the time of event emission

        super().on_emit(log_data)


class BrizzBatchLogRecordProcessor(BatchLogRecordProcessor):
    """Batch log record processor with masking and context support."""

    def __init__(
        self,
        exporter: LogExporter,
        config: BrizzConfig,
    ) -> None:
        super().__init__(exporter)
        self._exporter = exporter
        self.config = config

    def on_emit(self, log_data: LogData) -> None:
        """Emit a log record after applying masking and context association."""
        # Apply masking if configured
        masking_config = getattr(self.config.masking, "event_masking", None) if self.config.masking else None
        if masking_config:
            log_data = _mask_log(log_data, masking_config)

        # Note: Context properties are now added directly in emit_event() method
        # to ensure proper context capture at the time of event emission

        super().on_emit(log_data)


def _mask_log(log_data: LogData, config: EventMaskingConfig) -> LogData:
    """Apply masking to a log record based on the provided configuration."""
    if not log_data.log_record.attributes:
        return log_data

    # Get masking rules
    rules = config.rules if config.rules else []
    if not getattr(config, "disable_default_rules", False):
        rules = DEFAULT_LOG_MASKING_RULES + rules

    try:
        # Apply masking to attributes
        masked_attributes = mask_attributes(
            log_data.log_record.attributes, rules, getattr(config, "_output_original_value", False)
        )

        # Apply masking to body if enabled
        if getattr(config, "mask_body", False) and log_data.log_record.body is not None:
            masked_body = log_data.log_record.body
            for rule in rules:
                masked_body = mask_value(masked_body, rule)
            log_data.log_record.body = masked_body

        # Update log attributes
        log_data.log_record.attributes = BoundedAttributes(attributes=masked_attributes)
        return log_data

    except Exception as error:
        logger.error("Error masking log record: %s", error)
        return log_data
