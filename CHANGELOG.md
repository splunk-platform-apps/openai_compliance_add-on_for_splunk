
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## [v1.2.0] - 2026-05-28

### Added
- API base URL selection to account configuration to support FedRAMP environments.
- New AUTH_LOG option for the Compliance Logs Input.
- Automatic retry logic with exponential backoff for compliance log API requests.
- Connect/read timeouts to all outbound HTTP requests.

## [v1.1.0] - 2026-05-28

### Added
- Compliance Logs Input: New CONVERSATION_MESSAGE event type to support the updated OpenAI Compliance API.

### Changed
- Migration Required: Due to OpenAI API changes, conversation ingestion has been relocated from the Compliance Data Input to the Compliance Logs Input.
- Data Continuity: Users must create new inputs using the CONVERSATION_MESSAGE event type to continue receiving conversations data. New logs will be ingested under the sourcetype: `openai:compliance:conversation_message`.
- Verification & Troubleshooting: After installation, please verify that you are running version 1.1.0 by checking the add-on footer. If you encounter version-related errors, it is recommended to perform a clean install by removing the existing version before deploying the new one.

### Removed
- Compliance Data Input: Conversations option from the endpoints list.

## [v1.0.0] - 2026-03-09

### Added

- Initial release 🚀
