# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2025-11-10

### Added
- Initial release of Neuraltrust SDK
- OpenAI Agents SDK integration via custom trace processor
- Automatic span capture for LLM calls, tool executions, agent runs, handoffs, and guardrails
- Async batching transport with exponential backoff and retry logic
- Sampling support for high-volume production workloads
- Configurable via environment variables or programmatic config
- Local test server for development
- Support for custom metadata
- Comprehensive trace data model with:
  - Resource metadata (SDK version, language, library info)
  - Trace workflows with group_id support
  - Detailed span attributes by type (LLM, tool, workflow, guardrail, handoff)
  - Event timestamps and status tracking
- HTTP transport with Bearer token authentication
- Debug logging support

### Features
- **OpenAI Agents Integration**: Drop-in trace processor for OpenAI Agents SDK
- **Batching**: Configurable batch size (default: 25 items) with automatic flush
- **Retry Logic**: Exponential backoff with configurable max retries
- **Sampling**: Probabilistic sampling for production workloads
- **Type Safety**: Full Pydantic models for all data structures
- **Async/Await**: Native async support throughout the SDK

### Configuration
- Environment variables for all settings (NEURALTRUST_*)
- Programmatic configuration via `TelemetryConfig`
- Option to replace OpenAI's default trace exporter

[1.5.0]: https://github.com/neuraltrust/neuraltrust-instrumentation/releases/tag/v1.5.0

