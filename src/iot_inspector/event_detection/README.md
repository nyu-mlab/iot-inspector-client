# Event Detection Pipeline

This module now uses a two-thread pipeline to reduce resource usage while keeping the same event inference behavior.

## Why the change

The previous design started six long-lived threads, one per stage. Each stage blocked on its own queue, which increased thread overhead and context switching. The new design keeps the same processing steps but executes them in sequence inside a single inference worker.

## Current design (2 threads)

- Packet/Burst Thread
  - Consumes packets from `global_state.packet_queue`
  - Filters and deduplicates packets
  - Builds bursts and enqueues completed bursts into `global_state.pending_burst_queue`

- Event Inference Thread
  - Consumes completed bursts from `global_state.pending_burst_queue`
  - Runs feature generation -> standardization -> periodic filtering -> event prediction in order
  - Emits events into `global_state.filtered_event_queue`

The pipeline entry points are implemented in `pipeline.py`:

- `ingest_and_burst_worker()`
- `inference_worker()`

## Compatibility

The original stage modules still provide their queue-based `start()` functions for compatibility. The new pipeline uses helper functions that return data instead of pushing to intermediate queues:

- `packet_processor.filter_packet()`
- `feature_generation.compute_burst_features()`
- `feature_standardization.standardize_burst_feature_data()`
- `periodic_filter.filter_periodic_burst()`

## Notes

- This change reduces thread count from 6 to 2 for event inference.
- The rest of the system (UI pages and global state queues) remains unchanged.
