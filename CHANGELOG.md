# Changelog

All notable changes to MedObsMind will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete backend API implementation
  - Vitals recording endpoints (`/api/v1/vitals`)
  - Alerts management endpoints (`/api/v1/alerts`)
  - Patient management endpoints (`/api/v1/patients`)
- Comprehensive documentation suite
  - Feature Matrix by user type
  - AI Architecture (Edge + Cloud)
  - ICU MVP Roadmap (3-phase)
  - Cost vs Impact Model
  - Governance & Ethics framework
- Community files
  - CONTRIBUTING.md - Contribution guidelines
  - CODE_OF_CONDUCT.md - Community standards
  - LICENSE - MIT license with medical disclaimer
- Android app structure
  - MVVM architecture foundation
  - Material Design 3 setup
  - Core activities and services
- Web landing page
  - Responsive design
  - Story and vision sections
  - Feature showcase
- Docker deployment setup
  - docker-compose.yml for multi-service orchestration
  - Backend Dockerfile
  - PostgreSQL and Redis integration

### Changed
- Updated README with complete project vision
- Reorganized documentation structure
- Enhanced security and compliance documentation

### Fixed
- None yet (initial release)

## [1.0.0] - 2026-02-06

### Added
- Initial repository setup
- Project structure for backend, Android, and web
- NEWS2 calculator implementation
- Database models (Patient, Vitals, Alert)
- FastAPI backend foundation
- Android app skeleton
- Comprehensive project documentation

### Security
- Environment-based configuration
- HIPAA/DISHA compliance considerations
- Role-based access control structure
- Audit logging framework

---

## Version History Notes

### Version Numbering

MedObsMind follows semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Incompatible API changes or major feature releases
- **MINOR**: New functionality in a backward-compatible manner
- **PATCH**: Backward-compatible bug fixes

### Medical Safety Changelog

Any changes affecting clinical algorithms or patient safety will be marked with:
- 🏥 Clinical algorithm changes
- ⚠️ Safety-critical changes
- 🔒 Security updates

### Deprecation Policy

- Features will be deprecated with at least one minor version notice
- Deprecated features will be removed in the next major version
- Critical security fixes may require immediate changes

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute to this changelog.

## Questions?

For questions about releases or changes:
- GitHub Issues: [Report an issue]
- Email: support@medobsmind.com
