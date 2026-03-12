# OpenAI Compliance Add-on for Splunk

This project involves the development of a Splunk add-on designed to automate the ingestion of OpenAI resource data and compliance logs from the OpenAI Compliance API into Splunk Enterprise or Splunk Cloud Platform. The primary objective is to provide organizations with centralized visibility into OpenAI through audit logging, policy enforcement, and regulatory compliance monitoring.

## Getting Started
> This add-on ingests data from an enterprise ChatGPT workspace using the OpenAI Compliance API.

### Requirements

- The OpenAI Compliance API is only available for **enterprise** administrators, so you must have an enterprise account to be able to enable it.
- Authentication is handled through an **API key**. The organization administrator must generate a new key for the corresponding workspace. Refer to the official OpenAI Compliance API documentation, as additional steps might be required to grant full API access to the key.

Review the OpenAI Compliance API documentation for more details on this [page](https://chatgpt.com/admin/api-reference).

### Installation

#### Steps for `Splunk Enterprise`
- Follow the instructions [here](https://docs.splunk.com/Documentation/AddOns/released/Overview/Singleserverinstall) to install the Add-on in a **single-instance** Splunk Enterprise deployment.

- Follow the instructions [here](https://docs.splunk.com/Documentation/AddOns/released/Overview/Distributedinstall) to install the Add-on in a **distributed** Splunk Enterprise deployment.

#### Steps for `Splunk Cloud Platform`
- Follow the instructions [here](https://docs.splunk.com/Documentation/AddOns/released/Overview/SplunkCloudinstall) to install the Add-on in Splunk Cloud Platform.

### Configuration
1. Open Splunk Web on the Heavy Forwarder (or IDM). Access the OpenAI Compliance Add-on for Splunk from the list of applications. 
2. Select the `Configuration` tab on the top left corner.
3. Press the `Account` button.
4. Press the `Add` button on the top right to create a new account.
5. Enter the following details in the dialog box:
    - **Account name**: Enter a unique name for this account.
    - **Workspace id**: Enter the workspace id where you want to get data from.
    - **API key**: The API key generated for your workspace.
6. Press the `Add` button.

### Usage

This add-on includes 2 inputs. Usage and configuration are described in the following steps.

#### OpenAI Compliance Data Input

This input can retrieve data from: Canvases, Conversations, GPTs, Projects, Users.

To create such an input, follow these instructions:

1. In the **Inputs** tab, select **Create New Input**.
2. Select **OpenAI Compliance Data Input**.
3. Enter the information in the related fields using the following input parameters table.

##### Input Parameters

Input name                |Corresponding field in Splunk Web | Description|
|-------------------------|----------------------------------|------------|
|`name`                   |Name                              |A unique name for your input.|
|`interval`               |Interval                          |Time interval of input in seconds.|
|`index`                  |Index                             |The index in which the data will be stored. The default is <code>default</code>.|
|`account`                |Account to use                    |The account created in the Configuration tab.|
|`endpoint`               |Endpoint                          |The endpoint where you want to get data from. Available options: Canvases, Conversations, GPTs, Projects, Users.
|`start_time`             |From                              |The start date for data ingestion in the format: YYYY-MM-DDTHH:MM:SSZ (for example, `2025-08-01T00:00:00Z`). This field is only supported and required by the conversations endpoint.|

##### Sourcetypes

---------------------------------------------------------
|      Endpoint      |            Sourcetype            |
---------------------|----------------------------------|
Canvases             | openai:compliance:canvases       |
Conversations        | openai:compliance:conversations  |
GPTS                 | openai:compliance:gpts           |
Projects             | openai:compliance:projects       |
Users                | openai:compliance:users          |

#### OpenAI Compliance Logs Input

This input gets the content of log files for the following event types: AUDIT_LOG, APP_LOG, APP_AUTH_LOG, CODEX_LOG.

To create such an input, follow these instructions:

1. In the **Inputs** tab, select **Create New Input**.
2. Select **OpenAI Compliance Logs Input**.
3. Enter the information in the related fields using the following input parameters table.

##### Input Parameters 

Input name                |Corresponding field in Splunk Web | Description|
|-------------------------|----------------------------------|------------|
|`name`                   |Name                              |A unique name for your input.|
|`interval`               |Interval                          |Time interval of input in seconds.|
|`index`                  |Index                             |The index in which the data will be stored. The default is <code>default</code>.|
|`account`                |Account to use                    |The account created in the Configuration tab.|
|`event_type`             |Event Type                        |Required. The log category. You can select multiple event types. Available options: AUDIT_LOG, APP_LOG, APP_AUTH_LOG, CODEX_LOG.
|`start_time`             |From                              |Required. The start date for data ingestion in the format: YYYY-MM-DDTHH:MM:SSZ (for example, `2025-08-01T00:00:00Z`).|

##### Sourcetypes

---------------------------------------------------------
|      Event Type      |          Sourcetype             |
-----------------------|---------------------------------|
AUDIT_LOG              | openai:compliance:audit_log     |
APP_LOG                | openai:compliance:app_log       |
APP_LOG_AUTH           | openai:compliance:app_log_auth  |
CODEX_LOG              | openai:compliance:codex_log     |

## Troubleshooting

Are you not seeing any events in Splunk? 
- Verify that you have an API key with the required permissions to access compliance data for the specified workspace.

The API key and Workspace id are correct, but still not events?
- Check Splunk internal logs for error details:
 `index=_internal source="*openai_compliance_addon_for_splunk_*"`

## Versions Supported

Tested for installation and basic ingestion on Splunk 10.x, 9.x and 8.2.

## Credits & Acknowledgements
> Built by [Splunk's FDSE Team (#team-fdse)]

* [Yuan Ling](https://github.com/lingy1028)
* [Isaac Fonseca Monge](https://github.com/ifonsecam)
* Sam Valley

## Contributing
See the [CONTRIBUTING.md](https://github.com/splunk-platform-apps/.github/blob/main/.github/CONTRIBUTING.md) file for details.