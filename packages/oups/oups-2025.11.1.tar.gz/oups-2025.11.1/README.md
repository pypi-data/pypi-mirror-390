# Welcome to oups!

## What is oups?
*oups* stands for Ordered Unified Processing Stack — out-of-core processing for ordered data (batch + live).

*oups* is a Python toolkit for building end-to-end pipelines over ordered data with the same code in offline training and live streaming/batch contexts.

It centers on ``StatefulLoop`` (``loop.bind_function_state``, ``loop.iterate``, ``loop.buffer``), which binds and persists function/object state, orchestrates chunked iteration, and buffers DataFrames under a memory cap with flush-on-limit or last-iteration semantics.
Complementing the loop, ``stateful_ops`` provides vectorized, chunk-friendly primitives like ``AsofMerger`` for multi-DataFrame as-of joins (with optional windows of previous values) and ``SegmentedAggregator`` (planned) for streamed segmentation and aggregation.
The ``store`` package manages ordered Parquet datasets via schema-driven keys (``@toplevel``), supports incremental updates (``store[key].write(...)``) and duplicate handling, and offers synchronized iteration across datasets via ``store.iter_intersections(...)`` with optional warm-up (``n_prev``).

Together these pieces enable out-of-core processing with resumability, and deterministic buffering. The design favors explicit, minimal APIs and reproducible results, aligning offline feature generation with online serving.

## Links

- 📖 **[Documentation](https://pierrot.codeberg.page/oups)** - Guides and API reference
- 📋 **[Changelog](https://codeberg.org/pierrot/oups/src/branch/main/CHANGELOG.md)** - Release notes and version history
