import os
import sys
import json
import traceback

import fire
import vertexai
from dotenv import load_dotenv
from google.api_core import exceptions as api_exceptions
from vertexai import agent_engines
from vertexai.preview import reasoning_engines


class AgentManager:
    """A manager for creating, deploying, and interacting with Vertex AI Agent Engines."""

    def __init__(self):
        """Initializes the AgentManager, loads environment variables, and configures Vertex AI."""
        load_dotenv()
        
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION")
        self.bucket = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET")
        self.agent_package_name = os.getenv("AGENT_PACKAGE_NAME")
        self.agent_display_name = os.getenv("AGENT_DISPLAY_NAME")
        self.agent_description = os.getenv("AGENT_DESCRIPTION", "") # Optional
        
        agent_requirements_str = os.getenv("AGENT_REQUIREMENTS", "google-cloud-aiplatform[adk,agent_engines]")
        self.agent_requirements = [req.strip() for req in agent_requirements_str.split(',')]

        required_vars = {
            "GOOGLE_CLOUD_PROJECT": self.project_id,
            "GOOGLE_CLOUD_LOCATION": self.location,
            "GOOGLE_CLOUD_STAGING_BUCKET": self.bucket,
            "AGENT_PACKAGE_NAME": self.agent_package_name,
            "AGENT_DISPLAY_NAME": self.agent_display_name,
        }
        missing_vars = [key for key, value in required_vars.items() if not value]
        if missing_vars:
            print(f"Error: Missing required environment variables: {', '.join(missing_vars)}", file=sys.stderr)
            sys.exit(1)

        try:
            print("Initializing Vertex AI...")
            vertexai.init(project=self.project_id, location=self.location, staging_bucket=self.bucket)
            print(f"   Project: {self.project_id}")
            print(f"   Location: {self.location}")
            print(f"   Staging Bucket: {self.bucket}\n")
        except Exception as e:
            print(f"Error initializing Vertex AI: {e}", file=sys.stderr)
            sys.exit(1)

    def _get_full_resource_name(self, engine_id: str) -> str:
        """Constructs the full agent resource name from the engine ID."""
        engine_id = str(engine_id)
        if "projects/" in engine_id:
            return engine_id
        return f"projects/{self.project_id}/locations/{self.location}/reasoningEngines/{engine_id}"

    def create(self):
        """Packages and deploys a new agent to Vertex AI Agent Engine."""
        try:
            from adk_short_bot.agent import root_agent
        except ImportError:
            print("Error: Could not import 'root_agent' from 'adk_short_bot.agent'.", file=sys.stderr)
            print("Ensure the agent package is in the correct path and installed in editable mode (pip install -e .).", file=sys.stderr)
            return

        print("Packaging agent...")
        packaged_agent = reasoning_engines.AdkApp(
            agent=root_agent,
            enable_tracing=True,
        )

        print("Deploying agent to Vertex AI...")
        try:
            remote_agent = agent_engines.create(
                display_name=AGENT_DISPLAY_NAME,
                description=AGENT_DESCRIPTION,
                agent_engine=packaged_agent,
                requirements=AGENT_REQUIREMENTS,
                extra_packages=[f"./{AGENT_PACKAGE_NAME}"],
            )
            engine_id = remote_agent.resource_name.split('/')[-1]
            print(f"\nSuccessfully created agent '{AGENT_DISPLAY_NAME}'")
            print(f"   Full Resource Name: {remote_agent.resource_name}")
            print(f"   Engine ID: {engine_id}")
        except api_exceptions.GoogleAPICallError as e:
            print(f"\nError deploying agent: API call failed with status {e.code()}", file=sys.stderr)
            print(f"Details: {e.message}", file=sys.stderr)
        except Exception as e:
            print(f"\nAn unexpected error occurred during deployment: {e}", file=sys.stderr)

    def delete(self, engine_id: str, force: bool = False):
        """
        Deletes an existing agent deployment.

        Args:
            engine_id: The unique ID of the agent to delete.
            force: If True, deletes the agent and all its associated resources.
        """
        if not engine_id:
            print("Error: engine_id is required.", file=sys.stderr)
            return

        full_resource_name = self._get_full_resource_name(engine_id)
        print(f"Deleting agent: {full_resource_name}...")
        if force:
            print("   --force flag set. Deleting agent and all child resources.")

        try:
            agent_engines.delete(resource_name=full_resource_name, force=force)
            print("\nAgent deleted successfully.")
        except api_exceptions.FailedPrecondition as e:
            print(f"\nError: Agent '{engine_id}' cannot be deleted because it has existing sessions or other child resources.", file=sys.stderr)
            print("To proceed, you must delete the agent and all its resources by using the --force flag.", file=sys.stderr)
            # Reconstruct the original command and suggest adding the --force flag
            command_args = [arg for arg in sys.argv if not arg.startswith('--force')]
            suggested_command = ' '.join(command_args) + ' --force=True'
            print("\nExample command:", file=sys.stderr)
            print(f"   {suggested_command}", file=sys.stderr)
        except api_exceptions.NotFound:
            print(f"\nError: Agent with ID '{engine_id}' not found.", file=sys.stderr)
        except api_exceptions.GoogleAPICallError as e:
            print(f"\nError deleting agent: API call failed with status {e.code()}", file=sys.stderr)
            print(f"Details: {e.message}", file=sys.stderr)
        except Exception as e:
            print(f"\nAn unexpected error occurred during deletion: {e}", file=sys.stderr)


    def list(self):
        """Lists all available agent deployments in the project."""
        print("Listing available agent deployments...")
        try:
            deployments = agent_engines.list()
            if not deployments:
                print("No deployments found.")
                return

            print("\n--- Available Agents ---")
            for i, deployment in enumerate(deployments):
                engine_id = deployment.name.split('/')[-1]
                print(f"[{i+1}] {deployment.display_name}")
                print(f"    Engine ID: {engine_id}")
                print(f"    Created: {deployment.create_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            print("------------------------")
        except api_exceptions.GoogleAPICallError as e:
            print(f"\nError listing agents: API call failed with status {e.code()}", file=sys.stderr)
            print(f"Details: {e.message}", file=sys.stderr)
        except Exception as e:
            print(f"\nAn unexpected error occurred while listing agents: {e}", file=sys.stderr)

    def _get_remote_agent(self, engine_id: str):
        """Helper to get a remote agent instance and handle common errors."""
        try:
            return agent_engines.get(str(engine_id))
        except api_exceptions.NotFound:
            print(f"Error: Agent with ID '{engine_id}' not found.", file=sys.stderr)
            return None
        except api_exceptions.GoogleAPICallError as e:
            print(f"Error retrieving agent: API call failed with status {e.code()}", file=sys.stderr)
            print(f"Details: {e.message}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"An unexpected error occurred while retrieving agent: {e}", file=sys.stderr)
            return None

    def create_session(self, engine_id: str, user_id: str = "default-user"):
        """
        Creates a new chat session for a given agent.

        Args:
            engine_id: The agent's unique ID.
            user_id: A unique identifier for the user.
        """
        print(f"Creating new session for user '{user_id}'...")
        remote_agent = self._get_remote_agent(engine_id)
        if not remote_agent:
            return

        try:
            session = remote_agent.create_session(user_id=user_id)
            print("\nSession created:")
            print(f"   Session ID: {session.get('id', 'N/A')}")
            print(f"   User ID: {user_id}")
        except Exception as e:
            print(f"\nError creating session: {e}", file=sys.stderr)

    def list_sessions(self, engine_id: str, user_id: str = "default-user"):
        """
        Lists all sessions for a specific user and agent.

        Args:
            engine_id: The agent's unique ID.
            user_id: The user's unique identifier.
        """
        print(f"Listing sessions for user '{user_id}'...")
        remote_agent = self._get_remote_agent(engine_id)
        if not remote_agent:
            return

        try:
            response_data = remote_agent.list_sessions(user_id=user_id)
            sessions_list = response_data.get("sessions", [])
            if not sessions_list:
                print(f"No sessions found for user '{user_id}'.")
                return

            print(f"\n--- Sessions for {user_id} ---")
            for session_object in sessions_list:
                print(f"- {session_object.get('id')}")
            print("--------------------------")
        except Exception as e:
            print(f"\nError listing sessions: {e}", file=sys.stderr)

    def chat(self, engine_id: str, session_id: str, message: str, user_id: str = "default-user", raw_output: bool = False, debug: bool = False):
        """
        Sends a message to the agent and streams the response.

        Args:
            engine_id: The agent's unique ID.
            session_id: The active session ID.
            message: The message to send to the agent.
            user_id: The user's unique identifier.
            raw_output: If True, prints the raw JSON response from the agent.
            debug: If True, prints full traceback on error.
        """
        print(f"Sending message to session '{session_id}'...")
        print(f"   User: '{message}'")
        
        remote_agent = self._get_remote_agent(engine_id)
        if not remote_agent:
            return

        try:
            stream = remote_agent.stream_query(
                user_id=user_id,
                session_id=str(session_id),
                message=message,
            )

            if raw_output:
                print("\n--- RAW AGENT STREAM ---")
                for chunk in stream:
                    print(json.dumps(chunk, indent=2))
                print("--- END RAW AGENT STREAM ---")
            else:
                print("\nAgent:")
                # Parse the stream for the text response.
                for chunk in stream:
                    if (isinstance(chunk, dict)
                        and (content := chunk.get('content'))
                        and isinstance(content, dict)
                        and (parts := content.get('parts'))
                        and isinstance(parts, list) and parts):

                        text = parts[0].get('text')
                        if text:
                            print(text, end="", flush=True)
                print() 

        except api_exceptions.NotFound as e:
            print(f"\nError during chat: Resource not found. Check your session ID.", file=sys.stderr)
            print(f"Details: {e.message}", file=sys.stderr)
        except api_exceptions.GoogleAPICallError as e:
            print(f"\nError during chat: API call failed with status {e.code()}", file=sys.stderr)
            print(f"Details: {e.message}", file=sys.stderr)
        except Exception as e:
            print(f"\nAn unexpected error occurred during chat session: {e}", file=sys.stderr)
            if debug:
                traceback.print_exc()


if __name__ == "__main__":
    fire.Fire(AgentManager)

