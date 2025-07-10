# Vertex AI Agent Manager

This script provides a command-line interface (CLI) to manage and interact with agents deployed on Google Cloud's Vertex AI Agent Engine. It simplifies tasks like deploying agents, managing chat sessions, and sending messages.

This tool is intended for developers who need a quick and easy way to test and interact with agents from a local terminal.

***

## About The Project

The `AgentManager` script helps with the following tasks:

* **Deploying**: Package and deploy a new agent.
* **Listing**: View all deployed agents in the project.
* **Deleting**: Remove an agent deployment.
* **Session Management**: Create and list chat sessions for an agent.
* **Chatting**: Send messages to an agent within a session and receive responses.

***

## Folder Structure

The project is organized with the following directory structure:

```
agent_framework/
├── .venv/
├── adk_short_bot/
│   ├── __init__.py
│   ├── agent.py
│   ├── prompt.py
│   └── tools/
│       ├── __init__.py
│       ├── character_counter.py
│       └── json_formatter.py
├── deployment/
│   └── remote.py
├── .env
├── pyproject.toml
├── README.md
└── requirements.txt
```

### File Descriptions

* **`agent_framework/`**: The root directory containing all project files.
* **`adk_short_bot/`**: The main Python package for the agent.
    * `agent.py`: Defines the core agent logic, integrating tools and prompts.
    * `prompt.py`: Contains prompt templates that guide the agent's behavior.
    * `tools/`: A sub-package containing the agent's custom tools.
        * `character_counter.py`: A sample tool for counting characters.
        * `json_formatter.py`: A sample tool for converting output to a json file.
* **`deployment/`**: Contains scripts for deploying and managing the agent.
    * `remote.py`: The CLI script for interacting with the Vertex AI Agent Engine.
* **`.env`**: Stores environment variables, such as GCP project details.
* **`pyproject.toml`**: Defines project metadata and build dependencies.
* **`README.md`**: The project's documentation file.
* **`requirements.txt`**: Lists the Python dependencies required for the project.

### Understanding `pyproject.toml`

The `pyproject.toml` file is the standard for configuring Python projects. It specifies build dependencies and project metadata, ensuring the agent can be packaged correctly for deployment.

#### File Contents Explained

```toml
[project]
name = "adk-short-bot"
version = "0.1.0"
description = "A bot that shortens your messages"
authors = [
    {name = "add name here", email = "add email here"}
]
readme = "README.md"
requires-python = ">=3.9"
license = "Apache-2.0"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["adk_short_bot"]
```

* **`[project]`**: Contains standard project metadata.
    * `name`: The official name of the Python package.
    * `version`: The current version of the package.
    * `description`, `authors`, `readme`, `license`: General project information.
    * `requires-python`: The minimum Python version needed.
* **`[build-system]`**: Specifies which tools are needed to build the package. Here, it's configured to use `setuptools`.
* **`[tool.setuptools]`**: A section for `setuptools`-specific configuration.
    * `packages`: This crucial line tells the build system which package directories to include. In this case, it includes the `adk_short_bot` package.

#### Maintaining for Future Projects

When using this framework for a new agent, the `pyproject.toml` file must be updated:

1.  **Update Project Metadata**: Change the `name`, `version`, `description`, and `authors` under the `[project]` section to match the new agent's details.
2.  **Update Package Name**: In the `[tool.setuptools]` section, change `packages = ["adk_short_bot"]` to `packages = ["your_new_agent_package_name"]`. This ensures that the correct agent code is packaged during deployment.

***

## Getting Started

Follow these steps to set up the project environment.

### Prerequisites

* Python 3.9 or newer (this framework was tested on Python 3.9.2).
* Google Cloud SDK (`gcloud`) installed on the local machine.

### Installation and Configuration

1.  **Set up the Python Virtual Environment**:
    From the root of the project directory, create and activate a virtual environment.

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install Dependencies**:
    Install the required Python libraries from `requirements.txt` and install the local agent package in editable mode, which allows for local development.

    ```bash
    pip install -r requirements.txt
    pip install -e .
    ```
    **Note:** Whenever a new tool is added or the agent's package structure is modified, the `pip install -e .` command should be run again to ensure the changes are recognized by the environment.

3.  **Authenticate with Google Cloud**:
    Log in with the `gcloud` CLI to authenticate for Application Default Credentials.

    ```bash
    gcloud auth application-default login
    ```

4.  **Create a Cloud Storage Bucket**:
    The agent engine requires a Cloud Storage bucket to stage deployment files. Create a new bucket using the following command, replacing `<bucket-name>` with a unique name.

    ```bash
    gcloud storage buckets create gs://<bucket-name> --project=<the-gcp-project-id> --location=<the-gcp-region>
    ```

5.  **Configure Environment Variables**:
    Create a `.env` file in the project's root directory. Populate the `.env` file with the Google Cloud project details.

    ```dotenv
    # .env file
    GOOGLE_CLOUD_PROJECT="the-gcp-project-id"
    GOOGLE_CLOUD_LOCATION="the-gcp-region" # e.g., us-central1
    GOOGLE_CLOUD_STAGING_BUCKET="gs://the-cloud-storage-bucket-name"
    AGENT_DISPLAY_NAME="My Agent"
    AGENT_PACKAGE_NAME="adk_short_bot"
    AGENT_DESCRIPTION="An agent that does things"
    AGENT_REQUIREMENTS="google-cloud-aiplatform[adk,agent_engines]"
    ```

    * `GOOGLE_CLOUD_PROJECT`: The Google Cloud Project ID.
    * `GOOGLE_CLOUD_LOCATION`: The GCP region for agent deployment (e.g., `us-central1`).
    * `GOOGLE_CLOUD_STAGING_BUCKET`: The name of the Cloud Storage bucket for staging files.
    * `AGENT_DISPLAY_NAME`: The name for the agent that will be displayed in the console.
    * `AGENT_PACKAGE_NAME`: The name of the local Python package containing the agent's code. This must match the package name in `pyproject.toml`.
    * `AGENT_DESCRIPTION`: An optional description for the agent.
    * `AGENT_REQUIREMENTS`: A comma-separated string of Python dependencies for the agent.

***

## Usage

All commands can be run from the terminal. The script uses `python-fire` to map class methods to CLI commands.

### List Deployed Agents

To view all agents currently deployed in the project:

```bash
python deployment/remote.py list
```

### Create and Deploy an Agent

To package and deploy the agent, run the create command. This command uses the `AGENT_DISPLAY_NAME` and other variables from the `.env` file.
*Note: This requires the agent's source code (e.g., the `adk_short_bot` package) to be in the same directory.*

```bash
python deployment/remote.py create
```

On success, this will output the **Engine ID** for the new agent. This ID should be copied for use in other commands.

### Delete an Agent

To remove an agent deployment, its **Engine ID** is required.

```bash
python deployment/remote.py delete --engine_id="<the-engine-id>"
```

If the agent has active sessions, the command will fail. Use the `--force=True` flag to delete the agent and all of its underlying resources, including sessions.

```bash
python deployment/remote.py delete --engine_id="<the-engine-id>" --force=True
```

### Create a Chat Session

Before chatting, a session must be created using the **Engine ID**.

```bash
python deployment/remote.py create_session --engine_id="<the-engine-id>" --user_id="default_user"
```

On success, this will output a **Session ID**. This ID is needed to start chatting.

### List Existing Sessions

To see all sessions created for a specific user, the **Engine ID** is required.

```bash
python deployment/remote.py list_sessions --engine_id="<the-engine-id>" --user_id="default_user"
```

### Chat with the Agent

Send a message to the agent using the **Engine ID** and **Session ID**.

```bash
python deployment/remote.py chat --engine_id="<the-engine-id>" --session_id="<the-session-id>" --message="Hello, agent!"
```

The `--user_id` can optionally be included if it differs from the default. The agent's response will be streamed to the console.

The following optional flags can be used for debugging:

* `--raw_output=True`: Prints the raw, unformatted JSON response from the agent stream.
* `--debug=True`: Prints a full traceback if an unexpected error occurs during the chat session.

### Interacting with cURL

For direct API testing, `cURL` can be used to interact with the agent's `:streamQuery` endpoint.

1.  **Set Environment Variables**:
    Define the necessary variables in the terminal.

    ```bash
    PROJECT_ID="<the-project-id>"
    LOCATION="<the-location>" # ex. us-central1
    ENGINE_ID="<the-engine-id>"
    USER_ID="<a-unique-user-id>"
    SESSION_ID="<an-active-session-id>"
    MESSAGE="In a sunny meadow, a dog named Max loved to dig" # Sample message
    ACCESS_TOKEN=$(gcloud auth print-access-token)
    ```

2.  **Execute the cURL Command**:
    Send the request to the agent's endpoint.

    ```bash
    curl -N -X POST \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json; charset=utf-8" \
      -d "{\"input\": {\"user_id\": \"$USER_ID\", \"session_id\": \"$SESSION_ID\", \"message\": \"$MESSAGE\"}}" \
      "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/reasoningEngines/$ENGINE_ID:streamQuery"
    ```
***
## Troubleshooting

This section covers common issues that may be encountered and their solutions.

### `ModuleNotFoundError: No module named '...'`

* **Issue**: Python cannot find a required library (e.g., `fire`, `dotenv`).
* **Solution**: Ensure the virtual environment is active (`source .venv/bin/activate`) and all dependencies are installed by running `pip install -r requirements.txt`.

### `ImportError: No module named 'adk_short_bot'`

* **Issue**: The `remote.py` script cannot find the local agent package.
* **Solution**: The local package must be installed in editable mode. Run `pip install -e .` from the project's root directory after activating the virtual environment.

### New Tool/Sub-Agent Not Deployed
* **Issue**: A newly added tool or sub-agent is not being recognized or used by the deployed agent.
* **Solution**: When new Python files are added to the agent package (e.g., a new tool in the `tools/` directory), the package must be re-installed for the changes to be included in the next deployment. Run `pip install -e .` from the project's root directory to update the installation.

### Authentication or Permission Errors

* **Issue**: The script fails with an error related to permissions (e.g., `403 Forbidden`).
* **Solution**:
    1.  Confirm that the `gcloud auth application-default login` command was run successfully.
    2.  Verify that the authenticated user has the necessary IAM roles (e.g., "Vertex AI User", "Storage Object Admin") in the target Google Cloud project.

### Deployment Fails

* **Issue**: The `python deployment/remote.py create` command fails during the deployment step.
* **Solution**:
    1.  **Check Environment Variables**: Ensure all required variables in the `.env` file are set correctly.
    2.  **Check the Staging Bucket**: Ensure the `GOOGLE_CLOUD_STAGING_BUCKET` in the `.env` file exists and that the authenticated user has permission to write to it.
    3.  **Review Agent Code**: There may be an issue in the agent's code (`adk_short_bot/`) that prevents it from being packaged correctly. Check for syntax errors or incorrect dependencies.
    4.  **Check `pyproject.toml`**: Ensure the `packages` list under `[tool.setuptools]` correctly points to the agent's package directory and that this name matches the `AGENT_PACKAGE_NAME` in the `.env` file.
