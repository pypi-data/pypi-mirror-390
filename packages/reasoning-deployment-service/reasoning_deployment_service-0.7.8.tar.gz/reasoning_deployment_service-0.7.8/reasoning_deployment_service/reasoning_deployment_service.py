import json, os, subprocess, yaml, sys
import uuid
import urllib.parse, vertexai, google.auth
import requests as _requests
from typing import Dict, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.agent_engines import AgentEngine
from google.adk.agents import BaseAgent
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.api_core.exceptions import NotFound
import logging
from datetime import datetime
from urllib.parse import urlparse, parse_qs

DISCOVERY_ENGINE_URL = "https://discoveryengine.googleapis.com/v1alpha"

class ReasoningEngineDeploymentService:
    def __init__(self, root_agent: BaseAgent, deployment_environment: str="DEV"):
        self._setup_logging()
        
        self._check_required_files_exist()
        load_dotenv(dotenv_path=".env.agent", override=True)

        self.root_agent = root_agent
        self.deployment_env = deployment_environment
        self.attempt_to_use_existing_auth = False

        self._cicd_deploy = False
        self._staging_bucket = None
        self._project_id = None
        self._project_number = None
        self._project_location = None
        self._oauth_client_id = None
        self._oauth_client_secret = None
        self._agent_space_engine = None


        self._load_agent_definition()
        self._load_deployment_environment_variables(deployment_environment=deployment_environment)
        self._load_runtime_variables()
        self._check_requirements_file_present()
         
        self._http = _requests.Session()
        self._http.headers.update({"Content-Type": "application/json"})
        self.authenticate()

    def _setup_logging(self):
        os.makedirs("logs", exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger("ReasoningEngineDeployment")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False  

        if not self.logger.handlers:
            self.log_filename = f"logs/deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_handler = logging.FileHandler(self.log_filename)
            file_handler.setLevel(logging.DEBUG)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            
            console_formatter = logging.Formatter('%(message)s')
            console_handler.setFormatter(console_formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        
        logging.getLogger('google').setLevel(logging.ERROR)
        logging.getLogger('urllib3').setLevel(logging.ERROR)
        logging.getLogger('requests').setLevel(logging.ERROR)

    def _log_record_file(self, level="ERROR"):
        """Log the current deployment record file contents to file only."""
        try:
            record = self._read_engine_deployment_record()
            if record:
                record_str = json.dumps(record, indent=2)
                # Write directly to the same log file without terminal output
                with open(self.log_filename, 'a') as f:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
                    f.write(f"{timestamp} - ReasoningEngineDeployment - {level} - Current deployment record:\n{record_str}\n")
        except Exception as e:
            self.logger.error(f"Failed to read deployment record: {e}")

    def error(self, message: str):
        self.logger.error(f"[DEPLOYMENT SERVICE: CRITICAL FAILURE]: {message}")
        self._log_record_file("ERROR")

    def warning(self, message: str):
        self.logger.warning(f"[DEPLOYMENT SERVICE: WARNING]: {message}")

    def info(self, message: str):
        self.logger.info(f"[DEPLOYMENT SERVICE: INFO]: {message}")

    def _generate_authorization_id(self) -> str:
        get_deployment_environment = os.getenv('AGENT_DEPLOYMENT_PIPELINE_ID', "LOCAL_RUN")

        if self._authorization_override:
            return self._authorization_override.lower()

        return f"{get_deployment_environment}-{self._reasoning_engine_name}-{str(uuid.uuid4())}-auth".lower()
        
    def _load_runtime_variables(self):
        load_dotenv(dotenv_path=".env", override=True)
        runtime_vars = {}

        for key in self._specific_dot_env_variables:
            if key in os.environ:
                runtime_vars[key] = os.environ[key]
        
        runtime_vars.update(self._runtime_variable_definitions or {})
        runtime_vars.update({'AUTHORIZATION_ID': self._generate_authorization_id()})
        runtime_vars.update({f"DEPLOYED_PROJECT_NUMBER": self._project_number})
        runtime_vars.update({f"DEPLOYED_PROJECT_ID": self._project_id})
        runtime_vars.update({f"AGENT_DEPLOYMENT_PIPELINE_ID": self._deployed_environment})

        self._authorization_id = runtime_vars.get('AUTHORIZATION_ID')
        self._environment_variables = runtime_vars

    def _check_required_files_exist(self):
        end_run = False
        if not os.path.exists(".env.agent"):
            self.warning("Creating .env.agent file ... done")
            self._generate_env_agent()
            end_run = True
        
        if not os.path.exists("agent.yaml"):
            self._generate_example_yaml_config()
            self.warning("Creating agent.yaml file ... done")
            end_run = True

        self.warning("Please fill in the required values in the generated files and re-run the deployment.")

        if end_run:
            sys.exit(1)

    def _access_token(self) -> str:
        """Live: fetch ADC access token; raises if not available."""
        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])

        if not creds.valid or (creds.expired and creds.refresh_token):
            creds.refresh(GoogleAuthRequest())
        return creds.token

    def authenticate(self) -> bool:
        try:
            _ = self._access_token()
            return True
        except Exception:
            pass

        try:
            subprocess.run(["gcloud", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except Exception:
            raise RuntimeError("'gcloud' not found on PATH. Install Google Cloud SDK.")

        proc = subprocess.run(
            ["gcloud", "auth", "application-default", "login"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        if proc.returncode != 0:
            raise RuntimeError(f"ADC auth failed:\n{proc.stdout}")

        _ = self._access_token()
        return True

    def _get_deployment_record_path(self):
        return Path("deployments") / f"{self.deployment_env}_{self._reasoning_engine_name}.json"

    def _read_engine_deployment_record(self) -> dict:
        file_path = self._get_deployment_record_path()
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f) or {}
        return {}

    def _write_engine_deployment(self, json_payload: dict):
        if not os.path.exists("deployments"):
            self.info(f"Creating deployments directory")
            os.makedirs("deployments")

        file_path = self._get_deployment_record_path()
        read_engine_deployment = self._read_engine_deployment_record()

        if read_engine_deployment:
            read_engine_deployment.update(json_payload)

            with open(file_path, "w") as f:
                json.dump(read_engine_deployment, f, sort_keys=False)

                self.info(f"Successfully wrote entry {json_payload} to {file_path}")
            return
        
        with open(file_path, "w") as f:
            self.info(f"Successfully created {file_path}")
            json.dump(json_payload, f, sort_keys=False)
            self.info(f"Successfully wrote entry {json_payload} to {file_path}")

    def _generate_env_agent(self, path: str | Path = ".env.agent", overwrite: bool = False) -> Path:
        """
        Generate a .env.agent template file with all deployment profile
        and app environment variables, left empty for later filling.
        """
        path = Path(path)
        if path.exists() and not overwrite:
            raise FileExistsError(f"{path} already exists. Pass overwrite=True to replace it.")

        template = """
        DEV_PROJECT_ID=
        DEV_PROJECT_NUMBER=
        DEV_PROJECT_LOCATION=
        DEV_OAUTH_CLIENT_ID=
        DEV_OAUTH_CLIENT_SECRET="""

        path.write_text(template.strip() + "\n")
        self._update_gitignore()
        
        return path

    def _update_gitignore(self):
        """Add common ignore patterns to .gitignore."""
        gitignore_path = Path(".gitignore")
        patterns_to_add = [
            "logs/",
            "deployments/", 
            ".env.agent",
            "__pycache__/",
            "*.pyc",
            ".venv/",
            "deploy_env/"
        ]
        
        existing_patterns = set()
        if gitignore_path.exists():
            existing_patterns = set(gitignore_path.read_text().splitlines())
        
        new_patterns = [p for p in patterns_to_add if p not in existing_patterns]
        
        if new_patterns:
            with open(gitignore_path, "a") as f:
                if existing_patterns:  # Add newline if file has content
                    f.write("\n")
                f.write("# Added by ReasoningEngineDeploymentService\n")
                for pattern in new_patterns:
                    f.write(f"{pattern}\n")

    def _generate_example_yaml_config(self, path: str | Path = "agent.yaml", overwrite: bool = False) -> Path:
        """
        Create an example YAML config matching the requested schema.
        """
        path = Path(path)
        if path.exists() and not overwrite:
            raise FileExistsError(f"{path} already exists. Pass overwrite=True to replace it.")

        config = {
            "defaults": {
                "reasoning_engine": {
                    "name": "reasoning-engine-dev",
                    "description": "A reasoning engine for development"
                },
                "gemini_enterprise": {
                    "target_deployment_engine_id": "your-gemini-enterprise-engine-id",
                    "name": "Agent Name Here",
                    "description": "Agent description here",
                    "tool_description": "Tool description here",
                },
                "authorization": {
                    "enabled": True,
                    "scopes": [
                        "https://www.googleapis.com/auth/cloud-platform",
                        "https://www.googleapis.com/auth/userinfo.email"
                        ]
                },
                "import_from_dot_env_by_name": ["TEST_ENV_VAR"],
                "runtime_variable_definitions":{
                    "EXAMPLE_VAR": "An example environment variable for the agent runtime"
                }
            }
        }

        path.write_text(yaml.safe_dump(config, sort_keys=False))
        return path
 
    def _load_agent_definition(self):
        try:
            with open("agent.yaml", "r") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            self._generate_example_yaml_config()
            self.error("Could not locate a valid agent.yaml file. Generating example file in your directory.")
            sys.exit(1)

        try:
            config = config['defaults']
            authorization = config['authorization']
            gemini_enterprise = config['gemini_enterprise']
            reasoning_engine = config['reasoning_engine']
            self._specific_dot_env_variables = config.get('import_from_dot_env_by_name', [])
            self._runtime_variable_definitions = config.get('runtime_variable_definitions', {})

            reasoning_engine_name = reasoning_engine.get('name')
            reasoning_engine_description = reasoning_engine.get('description')

            gemini_enterprise_name = gemini_enterprise.get('name')
            gemini_enterprise_description = gemini_enterprise.get('description')
            gemini_enterprise_tool_description = gemini_enterprise.get('tool_description')
            gemini_enterprise_engine_id = gemini_enterprise.get('target_deployment_engine_id')
            gemini_enterprise_icon_uri = gemini_enterprise.get('icon_uri')

            self._icon_uri = gemini_enterprise_icon_uri
            self._agent_space_engine = gemini_enterprise_engine_id or os.getenv(f"{self.deployment_env}_AGENT_SPACE_ENGINE")
            self._required_scopes = authorization.get('scopes', [])
            self._agent_folder = "agent"
            self._reasoning_engine_name = reasoning_engine_name
            self._reasoning_engine_description = reasoning_engine_description
            self._agent_space_name = gemini_enterprise_name
            self._agent_space_description = gemini_enterprise_description
            self._agent_space_tool_description = gemini_enterprise_tool_description
            self._use_authorization = authorization.get('enabled', False)
            self._authorization_override = authorization.get('authorization_id_override', None)
        except KeyError as e:
             raise RuntimeError(f"Missing required key in agent.yaml: {e}. Your agent.yaml file is not valid for this deployment service version.")
        
    def _load_deployment_environment_variables(self, deployment_environment: str):
        required_vars = ['PROJECT_ID', 'PROJECT_NUMBER', 'PROJECT_LOCATION', 'STAGING_BUCKET']
        
        for var in required_vars:
            env_var = f"{deployment_environment}_{var}"
            if env_var not in os.environ or not os.getenv(env_var):
                raise RuntimeError(f"Missing required environment variable: {env_var}.")
            
            setattr(self, f"_{var.lower()}", os.getenv(env_var))

        if not self._agent_space_engine:
            raise RuntimeError(f"Missing AGENT_SPACE_ENGINE for deployment environment {deployment_environment}.")

        if self._use_authorization:
            required_auth_vars = ['OAUTH_CLIENT_ID', 'OAUTH_CLIENT_SECRET']

            for var in required_auth_vars:
                env_var = f"{deployment_environment}_{var}"
                if env_var not in os.environ or not os.getenv(env_var):
                    raise RuntimeError(f"Missing required environment variable: {env_var}")

                setattr(self, f"_{var.lower()}", os.getenv(env_var))

        self._deployed_environment = os.getenv(f"AGENT_DEPLOYMENT_PIPELINE_ID", "unregistered_environment")

    def _check_requirements_file_present(self):
        if not os.path.exists("requirements.txt"):
            raise RuntimeError("Missing requirements.txt file")
        
    def _load_requirements(self):
        with open("requirements.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]

    def create_reasoning_engine(self):
        vertexai.init(
            project=self._project_id,
            location=self._project_location,
            staging_bucket=self._staging_bucket,
        )

        creation = agent_engines.create(
            self.root_agent,
            display_name=self._reasoning_engine_name,
            description=self._reasoning_engine_description,
            requirements=self._load_requirements(),
            env_vars=self._environment_variables,
            extra_packages=[f"./{self._agent_folder}"]
        )

        if creation:
            self.info(f"Reasoning engine created successfully: {creation.resource_name}")

        json_payload = {"reasoning_engine_id": creation.resource_name}
        self._write_engine_deployment(json_payload)

    def update_reasoning_engine(self, reasoning_engine_id):
        vertexai.init(
            project=self._project_id,
            location=self._project_location,
            staging_bucket=self._staging_bucket,
        )

        try:
            updating = agent_engines.update(
                resource_name=reasoning_engine_id,
                agent_engine=self.root_agent,
                display_name=self._reasoning_engine_name,
                description=self._reasoning_engine_description,
                requirements=self._load_requirements(),
                env_vars=self._environment_variables,
                extra_packages=[f"./{self._agent_folder}"]
            )
        except NotFound as e:
            self.error(f"Reasoning engine {reasoning_engine_id} not found. Cannot update.")
            self.error(f"Please inspect using CLI, GUI or GCP Interface to identify root cause.")
            self.error(f"Deleting deployment record {self._get_deployment_record_path()} to allow re-creation.")
            self.error(f"System reported: {e}")
            os.remove(self._get_deployment_record_path())
            sys.exit(1)
            

        if updating:
            self.info(f"Reasoning engine updated successfully: {updating.resource_name}")

        self._write_engine_deployment({'reasoning_engine_id': updating.resource_name})

    def _get_agent_space_payload(self, reasoning_engine: str) -> Tuple[dict, dict]:
        headers = {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self._project_number,
        }
        payload = {
            "displayName": self._agent_space_name,
            "description": self._agent_space_description,
            "adk_agent_definition": {
                "tool_settings": {"tool_description": self._agent_space_tool_description},
                "provisioned_reasoning_engine": {"reasoning_engine": reasoning_engine},
            },
        }

        if self._icon_uri:
            payload["icon"] = {"uri": self._icon_uri}

        if self._authorization_id:
            payload["adk_agent_definition"]["authorizations"] = [
                f"projects/{self._project_number}/locations/global/authorizations/{self._authorization_id}"
            ]

        return headers, payload
    
    def _get_agent_space_agent_url_new(self):
        return (f"{DISCOVERY_ENGINE_URL}/projects/{self._project_number}/locations/global/collections/default_collection/"
               f"engines/{self._agent_space_engine}/assistants/default_assistant/agents")

    def _deploy_to_agent_space(self):
        get_reasoning_engine = self._read_engine_deployment_record()

        if not get_reasoning_engine or not get_reasoning_engine.get("reasoning_engine_id"):
            return ("failed", "Reasoning engine required before deploy", None)
        
        if get_reasoning_engine.get("agent_space_id"):
            self.warning("Agent space already exists; skipping creation.")
            
            return

        headers, payload = self._get_agent_space_payload(get_reasoning_engine["reasoning_engine_id"])
        url = self._get_agent_space_agent_url_new()
        r = self._http.post(url, headers=headers, json=payload, timeout=90)

        if r.status_code < 400:
            self.info("Agent space deployed successfully.")
            if self.attempt_to_use_existing_auth:
                self.warning("Using existing authorization.")
                self._write_engine_deployment({"authorization_id": self._authorization_id, 'scopes': self._required_scopes})
            self._write_engine_deployment({"agent_space_id": r.json().get("name")})
        else:
            # Log API failure details to file only
            with open(self.log_filename, 'a') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
                f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - Agent space deployment failed with status {r.status_code} {r.reason}\n")
                f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - URL: {r.url}\n")
                f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - Response: {r.text}\n")
                if r.headers.get('content-type', '').startswith('application/json'):
                    try:
                        error_json = r.json()
                        f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - Error details: {json.dumps(error_json, indent=2)}\n")
                    except:
                        pass
            
            # Terminal message - simple
            self.error("Agent space deployment failed")
            # This will also log the record file

    def _update_in_agent_space(self):
        get_reasoning_engine = self._read_engine_deployment_record()

        if not get_reasoning_engine or not get_reasoning_engine.get("reasoning_engine_id"):
            return ("failed", "Reasoning engine required before update", None)
        
        if not get_reasoning_engine.get("agent_space_id"):
            self.warning("No agent space to update; skipping.")
            return

        headers, payload = self._get_agent_space_payload(get_reasoning_engine["reasoning_engine_id"])
        url = f'{DISCOVERY_ENGINE_URL}/' + get_reasoning_engine.get("agent_space_id")
        r = self._http.patch(url, headers=headers, json=payload, timeout=90)

        if r.status_code < 400:
            if self.attempt_to_use_existing_auth:
                self.info("Using existing authorization.")
                self._write_engine_deployment({"authorization_id": self._authorization_id, 'scopes': self._required_scopes})
            self.info("Agent space updated successfully.")
            return True
        else:
            # Log API failure details to file only
            with open(self.log_filename, 'a') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
                f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - Failed to update agent space with status {r.status_code} {r.reason}\n")
                f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - URL: {r.url}\n")
                f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - Response: {r.text}\n")
                if r.headers.get('content-type', '').startswith('application/json'):
                    try:
                        error_json = r.json()
                        f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - Error details: {json.dumps(error_json, indent=2)}\n")
                    except:
                        pass
            
            # Terminal message - simple
            self.error("Failed to update agent space")
            # This will also log the record file
            return False

    def _build_authorization_uri(self, client_id: str, scopes: list[str]) -> str:
        base = "https://accounts.google.com/o/oauth2/auth"
        query = {
            "response_type": "code",
            "client_id": client_id,
            "scope": " ".join(scopes),
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{base}?{urllib.parse.urlencode(query)}"

    def _create_authorization(self) -> dict:
        read_authorizations = self._read_engine_deployment_record()

        if not self._authorization_id:
            self.warning("No authorization ID provided; skipping authorization creation.")

            return

        if read_authorizations and (read_authorizations.get("authorization_id") and read_authorizations.get("authorization_id") == self._authorization_id):
            self.warning("Authorization already exists; skipping creation.")

            return
        
        discovery_engine_url = "https://discoveryengine.googleapis.com/v1alpha"
        headers = {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self._project_number,
        }

        client_id = self._oauth_client_id or "your-client-id"
        client_secret = self._oauth_client_secret or "your-client-secret"

        payload = {
            "name": f"projects/{self._project_number}/locations/global/authorizations/{self._authorization_id}",
            "serverSideOauth2": {
                "clientId": client_id,
                "clientSecret": client_secret,
                "authorizationUri": self._build_authorization_uri(client_id, self._required_scopes),
                "tokenUri": "https://oauth2.googleapis.com/token",
            },
        }

        url = (
            f"{discovery_engine_url}/projects/{self._project_id}/locations/global/authorizations"
            f"?authorizationId={self._authorization_id}"
        )

        r = self._http.post(url, headers=headers, json=payload, timeout=60)

        if r.status_code < 400:
            payload = {"authorization_id": self._authorization_id, 'scopes': self._required_scopes}
            self._write_engine_deployment(payload)
            return True
        
        if r.status_code == 409:
            self.warning("Authorization conflict detected; attempting to use existing authorization.")
            self.logger.debug(f"Conflict response: {r.text}")
            self.attempt_to_use_existing_auth = True
        elif r.status_code >= 400:
            # Log API failure details to file only
            with open(self.log_filename, 'a') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
                f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - Authorization creation failed with status {r.status_code} {r.reason}\n")
                f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - URL: {r.url}\n")
                f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - Response: {r.text}\n")
                if r.headers.get('content-type', '').startswith('application/json'):
                    try:
                        error_json = r.json()
                        f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - Error details: {json.dumps(error_json, indent=2)}\n")
                    except:
                        pass
            
            # Terminal message - simple
            self.error("Authorization creation failed")
            # This will also log the record file


    def _drop_authorization(self) -> bool:
        temp_auth = self._authorization_id
        self._authorization_id = None
        self._update_in_agent_space()
        self._authorization_id = temp_auth

        read_record = self._read_engine_deployment_record()
        read_record.pop("authorization_id", None)

        file_path = self._get_deployment_record_path()

        with open(file_path, "w") as f:
            json.dump(read_record, f, sort_keys=False, indent=2)

        self.info("Authorization dropped successfully")

        return True
    
    def _delete_authorization(self, drop_authorization_for_refresh: Optional[str] = None):
        auth_to_drop = drop_authorization_for_refresh or self._authorization_id

        if not auth_to_drop:
            self.warning("No authorization ID provided; skipping deletion.")
            return

        discovery_engine_url = "https://discoveryengine.googleapis.com/v1alpha"
        headers = {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self._project_number,
        }

        url = (
            f"{discovery_engine_url}/projects/{self._project_id}/locations/global/authorizations"
            f"?authorizationId={auth_to_drop}"
        )

        r = self._http.delete(url, headers=headers, timeout=60)

        if r.status_code < 400:
            if drop_authorization_for_refresh:
                self.info(f"Authorization {drop_authorization_for_refresh} deleted successfully for refresh.")
                return True
            
            self.info("Authorization deleted successfully.")
            self._authorization_id = None
            self._update_in_agent_space()
            return True

        with open(self.log_filename, 'a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
            f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - Failed to delete authorization with status {r.status_code} {r.reason}\n")
            f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - URL: {r.url}\n")
            f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - Response: {r.text}\n")
            if r.headers.get('content-type', '').startswith('application/json'):
                try:
                    error_json = r.json()
                    f.write(f"{timestamp} - ReasoningEngineDeployment - ERROR - Error details: {json.dumps(error_json, indent=2)}\n")
                except:
                    pass
        

        self.error("Failed to delete authorization")
        return False

    def one_deployment_with_everything_on_it(self, skip_engine_step=False):
        read_engine = self._read_engine_deployment_record()

    
        if not skip_engine_step:
            if read_engine and read_engine.get("reasoning_engine_id"):
                self.info("Updating reasoning engine ... ")
                self.update_reasoning_engine(read_engine["reasoning_engine_id"])
                self.info("Done!")
            else:
                self.create_reasoning_engine()
        else:
            if not read_engine or not read_engine.get("reasoning_engine_id"):
                self.warning("Skipping reasoning engine step, but no existing engine found in record.")
                self.warning("Please ensure the reasoning engine exists before proceeding. Ending Agent Space update attempt")

                sys.exit(1)

        needs_auth_reset = False

        if not read_engine or read_engine.get("authorization_id") != self._authorization_id:
            self.warning("Detected change in authorization ID")
            needs_auth_reset = True

        elif read_engine and read_engine.get("scopes") != self._required_scopes:
            self.warning("Detected change in authorization scopes")
            needs_auth_reset = True

        if needs_auth_reset:
            self.info("Resetting authorization...")
            self._drop_authorization()
            self._create_authorization()

        if not read_engine or (read_engine and not read_engine.get("agent_space_id")):
            self.info("Creating agent space ... ")
            self._deploy_to_agent_space()
        else:
            self._update_in_agent_space()


    def _ensure_vertex_inited(self):
        """Initialize Vertex AI once and reuse to avoid repeated heavy init calls."""
        if not self._vertex_inited:
            vertexai.init()
            self._vertex_inited = True
        
    
    def find_engine_by_name(self, engine_name: str) -> Optional[str]:
        engines = list(agent_engines.list(filter=f'display_name="{engine_name}"'))
        if not engines:
            return None
        if len(engines) > 1:
            raise RuntimeError(f"Multiple engines found with display_name='{engine_name}'. Use unique names/labels.")
        eng = engines[0]
        if not isinstance(eng, AgentEngine) or not hasattr(eng, "resource_name"):
            raise RuntimeError("Unexpected engine object; missing AgentEngine/resource_name.")
        return eng.resource_name

        
    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Goog-User-Project": str(self._project_number),
        }
    
    def find_authorization_by_id(self, authorization_id: str) -> Optional[str]:
        name = f"projects/{self._project_id}/locations/global/authorizations/{authorization_id}"
        url = f"{DISCOVERY_ENGINE_URL}/{name}"
        r = self._http.get(url, headers=self._get_headers(), timeout=60)

        if r.status_code == 404:
            return None
        
        self.info(r.json())
        self.info(r.text)

        if r.status_code == 403:
            self.warning("Access denied")
            return None
        else:
            r.raise_for_status()
        
        return r.json().get("name", name)

    def find_agent_space_agents_by_display(self, display_name: str) -> Optional[dict]:
        base = (
            f"{DISCOVERY_ENGINE_URL}/projects/{self._project_id}/locations/global/"
            f"collections/default_collection/engines/{self._agent_space_engine}/"
            f"assistants/default_assistant/agents"
        )

        headers = self._get_headers()
        page = None
        matches =[]

        while True:
            url = base + (f"?pageToken={page}" if page else "")
            r = self._http.get(url, headers=headers, timeout=60)
            r.raise_for_status()
            data = r.json()

            for a in data.get("agents", []):
                if a.get("displayName") != display_name:
                    continue
                full = a.get("name", "")
                matches.append({
                    "id": full.split("/")[-1] if full else "",
                    "display_name": a.get("displayName", ""),
                    "full_name": full,
                    "labels": a.get("labels", {}),
                })

            page = data.get("nextPageToken")
            if not page:
                break

        if not matches:
            return None
        if len(matches) > 1:
            raise RuntimeError(
                f"Found {len(matches)} agents with displayName='{display_name}'. "
                "Provide an ID or labels (e.g., env/app/agent) to disambiguate."
            )
        
        return matches[0]
    
    def patch_agent_space_metadata_and_auth(
        self,
        agent_id: str,
        new_display_name: Optional[str] = None,
        new_description: Optional[str] = None,
        new_reasoning_engine: Optional[str] = None,
        new_authorizations: Optional[list[str]] = None,
        icon_uri: Optional[str] = None,
    ) -> dict:
        """
        Safely patch metadata (displayName, description) and linkage fields
        (reasoningEngine, authorizations) for an existing Agent Space agent.
        Preserves all other required adkAgentDefinition fields.
        """
        url = (
            f"{DISCOVERY_ENGINE_URL}/projects/{self._project_id}/locations/global/"
            f"collections/default_collection/engines/{self._agent_space_engine}/"
            f"assistants/default_assistant/agents/{agent_id}"
        )

        agent_updates_body = {
            "displayName": new_display_name,
            "description": new_description,
            "adk_agent_definition": {
                "tool_settings": {
                    "tool_description": new_description
                },
                "provisioned_reasoning_engine":{
                    "reasoning_engine": new_reasoning_engine
                }, 
                "authorizations": new_authorizations
            }
        }

        if icon_uri:
            agent_updates_body["icon"] = {"uri": icon_uri}

        self.info(agent_updates_body)

        headers = self._get_headers()

        update_mask = ["displayName", "description", "adk_agent_definition.tool_settings.tool_description", 
                       "adk_agent_definition.provisioned_reasoning_engine.reasoning_engine", "adk_agent_definition.authorizations", 'icon.uri']
        params = {"update_mask": ",".join(update_mask)}
        resp = self._http.patch(url, headers=headers, params=params, json=agent_updates_body, timeout=60)

        return resp.json()

    
    def one_githhub_deployment_to_go_with_skip(self):
        return self.one_github_deployment_to_go(skip_engine=True)

    def update_authorization_scopes(self, auth_id: str, scopes: list, oauth_client_id: str) -> dict:
        """Patch the scopes for a specific authorization by ID, updating the authorizationUri as well."""
        scopes_str = " ".join(scopes)
        authorization_uri = (
            "https://accounts.google.com/o/oauth2/auth"
            "?response_type=code"
            f"&client_id={oauth_client_id}"
            f"&scope={scopes_str}"
            "&access_type=offline&prompt=consent"
        )
        payload = {
            "serverSideOauth2": {
                "authorizationUri": authorization_uri
            }
        }
        url = f"{DISCOVERY_ENGINE_URL}/projects/{self._project_id}/locations/global/authorizations/{auth_id}?update_mask=server_side_oauth2.authorization_uri"
        headers = {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self._project_number,
        }
        r = self._http.patch(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()
    
    def detect_scope_change(self, auth_full_name, want_scopes) -> Optional[bool]:
        auth_url = f"{DISCOVERY_ENGINE_URL}/{auth_full_name}"
        hdrs = self._get_headers().copy()

        if "Authorization" in hdrs:
            hdrs["Authorization"] = "Bearer ***"
        
        self.info(f"[AUTH] GET {auth_url} headers={json.dumps(hdrs)}")
        r = self._http.get(auth_url, headers=self._get_headers(), timeout=60)
        self.info(f"[AUTH] GET status={r.status_code} ct={r.headers.get('content-type','')}")
        
        try:
            self.info(f"[AUTH] GET body={json.dumps(r.json(), indent=2)[:4000]}")
        except Exception:
            self.info(f"[AUTH] GET text={(r.text or '')[:1000]}")
        r.raise_for_status()

        data = r.json() or {}
        existing_uri = (((data.get("serverSideOauth2") or {}).get("authorizationUri")) or "")
        self.info(f"[AUTH] existing authorizationUri={existing_uri!r}")
        existing_scopes = set()
        
        if existing_uri:
            parsed = urlparse(existing_uri)
            qs = parse_qs(parsed.query)
            scope_str = (qs.get("scope", [""])[0] or "")
            existing_scopes = set(scope_str.split())

        self.info(
            f"[AUTH] scopes existing={sorted(existing_scopes)} want={sorted(want_scopes)} "
            f"missing={sorted(want_scopes - existing_scopes)} extra={sorted(existing_scopes - want_scopes)}"
        )

        if existing_scopes != want_scopes:
            return True

    def one_github_deployment_to_go(self, skip_engine=False):
        """
        CI-friendly deploy:
        - Engine: create or update by display_name.
        - Authorization: create if missing; patch if scopes changed.
        - Agent Space: create if missing; patch if found (by displayName under engine).
        """
        self.info("Starting GitHub deployment...")
        self.info(
            f"[CFG] project_id={self._project_id} project_number={self._project_number} "
            f"location={self._project_location} engine_name={self._reasoning_engine_name} "
            f"agent_space_engine={self._agent_space_engine} auth_id={self._authorization_id} "
            f"scopes={self._required_scopes} staging_bucket={self._staging_bucket}"
        )

        self._cicd_deploy = True
        delete_old_authorization = False
        self.info(f"[INIT] vertexai.init(project={self._project_id}, location={self._project_location}, staging_bucket={self._staging_bucket})")
        vertexai.init(
            project=self._project_id,
            location=self._project_location,
            staging_bucket=self._staging_bucket,
        )

        self.info(f"[ENGINE] Resolving by display_name={self._reasoning_engine_name}")
        engine_rn = self.find_engine_by_name(self._reasoning_engine_name)
        self.info(f"[ENGINE] find_engine_by_name -> {engine_rn}")

        if not skip_engine:
            if not engine_rn:
                self.info(f"[ENGINE] '{self._reasoning_engine_name}' not found. Creating...")
                self.create_reasoning_engine()
                rec_after_create = self._read_engine_deployment_record()
                self.info(f"[ENGINE] record after create -> {json.dumps(rec_after_create, indent=2)}")
                engine_rn = rec_after_create.get("reasoning_engine_id") or self.find_engine_by_name(self._reasoning_engine_name)
                self.info(f"[ENGINE] post-create resolution -> {engine_rn}")
                if not engine_rn:
                    self.error("[ENGINE] Creation did not yield a resource name.")
                    raise RuntimeError("Engine creation failed.")
            else:
                self.info(f"[ENGINE] '{self._reasoning_engine_name}' exists. Updating...")
                self.update_reasoning_engine(engine_rn)

        self.info(f"[ENGINE] final engine_rn={engine_rn}")

        auth_full_name = None
        if self._authorization_id:
            want_scopes = set(self._required_scopes or [])
            self.info(f"[AUTH] id={self._authorization_id} want_scopes={sorted(want_scopes)}")
            auth_full_name = self.find_authorization_by_id(self._authorization_id)
            self.info(f"[AUTH] find_authorization_by_id -> {auth_full_name}")

            if auth_full_name and self.detect_scope_change(auth_full_name, want_scopes):
                self.info(f"[AUTH] Scopes changed; patching authorization {self._authorization_id}...")
                delete_old_authorization = auth_full_name
                self._authorization_id = self._generate_authorization_id()
                auth_full_name = None

            if not auth_full_name:
                self.info(f"[AUTH] '{self._authorization_id}' not found. Creating...")
                ok = self._create_authorization()
                self.info(f"[AUTH] _create_authorization -> {ok}")
                auth_full_name = self.find_authorization_by_id(self._authorization_id)
                self.info(f"[AUTH] post-create resolve -> {auth_full_name}")

                if not ok or not auth_full_name:
                    self.error("[AUTH] Creation failed or did not resolve.")

                    raise RuntimeError("Authorization creation failed.")
        else:
            self.info("[AUTH] No authorization_id configured; skipping authorization step.")

        self.info(f"[AGENT] Resolving by display_name={self._agent_space_name}")
        existing_agent = self.find_agent_space_agents_by_display(self._agent_space_name)
        self.info(f"[AGENT] find_agent_space_agents_by_display -> {json.dumps(existing_agent, indent=2)}")

        if not existing_agent:
            headers, payload = self._get_agent_space_payload(engine_rn)
            create_url = self._get_agent_space_agent_url_new()
            self.info(f"[AGENT] POST {create_url}")
            cr = self._http.post(create_url, headers=headers, json=payload, timeout=90)
            self.info(f"[AGENT] POST status={cr.status_code}")
            self.info(f"[AGENT] POST ct={cr.headers.get('content-type','')}")
            self.info(f"[AGENT] POST body={(cr.text or '')[:4000]}")
            cr.raise_for_status()
            agent_name = (cr.json() or {}).get("name")
            if agent_name:
                self._write_engine_deployment({"agent_space_id": agent_name})
                self.info(f"[AGENT] Created: {agent_name}")
            else:
                self.warning("[AGENT] Created but response missing name. Verify in console.")
        else:
            self.info(f"[AGENT] '{self._agent_space_name}' exists. Patching metadata and auth only...")
            patched = self.patch_agent_space_metadata_and_auth(
                agent_id=existing_agent["id"],
                new_display_name=self._agent_space_name,
                new_description=self._agent_space_description,
                new_reasoning_engine=engine_rn,
                new_authorizations=[
                    f"projects/{self._project_number}/locations/global/authorizations/{self._authorization_id}"
                ] if self._authorization_id else None,
                icon_uri=self._icon_uri,
            )
            self.info(f"[AGENT] PATCH result -> {json.dumps(patched, indent=2)[:2000]}")


        if delete_old_authorization:
            self.info(f"[AUTH] Deleting old authorization {delete_old_authorization}...")
            self._delete_authorization(delete_old_authorization)

        self.info("GitHub deployment completed successfully.")
