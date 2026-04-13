# openai_compliance_add-on_for_splunk

Essential links for the project:

:books: [Documentation](https://splunk-platform-apps.github.io/openai_compliance_add-on_for_splunk/)<br/>
:writing_hand: [Release Notes](./CHANGELOG.md)<br/>
:heart_on_fire: [Contributing Guidelines](https://github.com/splunk-platform-apps/.github/.github/CONTRIBUTING.md)<br/>
:balance_scale: [License](./LICENSE)

---

## Getting Started
* Structure your code as per [below](#repository-structure)
* Add documentation to your project following [guidelines](https://github.com/splunk-platform-apps/.github/blob/main/documentation/DEV_GUIDELINES.md)
* Understand usage and troubleshooting of provided [automation pipelines](https://github.com/splunk-platform-apps/.github/blob/main/.github/CONTRIBUTING.md)
* Understand the [release process](https://github.com/splunk-platform-apps/.github/blob/main/.github/CONTRIBUTING.md#code-release)

### Repository Structure
```
.
├── README.md
├── CHANGELOG.md
├── docs
│   └── readme.md
├── package
|   ├── README.txt
│   ├── README
│   ├── LICENSES
|   |   └── LICENSE.txt
│   ├── app.manifest
│   ├── appserver
│   ├── bin
│   ├── default
│   ├── metadata
│   └── static
├── etc
├── website
│   └── docusaurus.config.ts
└── tests
    ├── conftest.py
    └── pytest.ini
```

* `README.md` to set expectations and give usage instructions
* `CHANGELOG.md` to keep track of all notable changes made as explained [here](https://github.com/splunk-platform-apps/.github/blob/main/.github/DEV_WORKFLOW.md#changelog)
* `docs/` contains main documentation
* `.gitignore` to ignore hidden or OS_ files
* `etc/` contains additional files such as images, configuration files, etc
* `website/` contain files required by [docusaurus](https://github.com/splunk-platform-apps/.github/blob/main/documentation/DEV_GUIDELINES.md)
* `package/` contains Splunk App / Add-On Source Files
* `tests/` contains files for unit testing, e2e testing, mocks, postman collections, etc

:point_right: Files needed for local development, packaging and local execution such as for example `docker-compose.yml`, `Makefile`, `pyproject.toml` or `poetry.lock` shall be added in the root folder.
