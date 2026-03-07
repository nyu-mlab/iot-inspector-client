"""
Lightweight two-thread event inference pipeline.
"""
import logging
import traceback

from . import global_state
from . import packet_processor
from . import burst_processor
from . import feature_generation
from . import feature_standardization
from . import periodic_filter
from . import predict_event


logger = logging.getLogger(__name__)


def ingest_and_burst_worker():
    """Consume raw packets, filter them, and assemble bursts."""
    pkt = global_state.packet_queue.get()
    try:
        filtered_pkt = packet_processor.filter_packet(pkt)
        if filtered_pkt is None:
            return
        burst_processor.process_burst(filtered_pkt)
    except Exception as exc:
        logger.error(
            "[Pipeline] Error in ingest/burst: %s for packet: %s\n%s",
            exc,
            pkt,
            traceback.format_exc(),
        )


def inference_worker():
    """Consume completed bursts and run inference sequentially."""
    flow_key, pop_time, pop_burst = global_state.pending_burst_queue.get()
    try:
        burst_features = feature_generation.compute_burst_features(
            flow_key,
            pop_time,
            pop_burst,
        )
        if burst_features is None:
            return
        standardized = feature_standardization.standardize_burst_feature_data(
            burst_features
        )
        if standardized is None:
            return

        filtered = periodic_filter.filter_periodic_burst(*standardized)
        if filtered is None:
            return

        burst, device_name, model_name = filtered
        predict_event.predict_event_helper(burst, device_name, model_name)
    except Exception as exc:
        logger.error(
            "[Pipeline] Error in inference: %s for burst: %s\n%s",
            exc,
            flow_key,
            traceback.format_exc(),
        )
