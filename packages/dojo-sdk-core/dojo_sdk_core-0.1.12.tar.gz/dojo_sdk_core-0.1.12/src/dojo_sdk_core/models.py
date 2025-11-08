import json
from pathlib import Path
from typing import Any, Callable, Optional

from pydantic import BaseModel, Field


class SettingsConfig(BaseModel):
    """Settings configuration."""

    anthropic_api_key: str = Field("", description="Anthropic API key")
    openai_api_key: str = Field("", description="OpenAI API key")
    openai_api_url: str = Field("", description="OpenAI API URL")
    dojo_websocket_endpoint: str = Field("", description="Dojo websocket endpoint")
    dojo_http_endpoint: str = Field("", description="Dojo http endpoint")
    posthog_api_key: str = Field("", description="PostHog API key")
    engine: str = Field("docker", description="Engine to use")
    browserbase_concurrent_limit: int = Field(1, description="Concurrent limit for BrowserBase engine")


class EnvironmentConfig(BaseModel):
    """Environment configuration."""

    type: str = Field(..., description="Environment type (e.g., 'spa')")
    path: str = Field(..., description="Path to environment file")


class InstructionsConfig(BaseModel):
    """Task instructions configuration."""

    user_prompt: str = Field(..., description="Prompt to show to the agent")
    success_criteria: str = Field(..., description="What constitutes success")


class TaskDefinition(BaseModel):
    """Complete task definition."""

    id: str = Field(..., description="Unique task identifier")
    name: str = Field(..., description="Human-readable task name")
    description: str = Field(..., description="Task description")
    environment: EnvironmentConfig = Field(..., description="Environment configuration")
    initial_state: dict[str, Any] = Field(..., description="Initial state for the environment")
    instructions: InstructionsConfig = Field(..., description="Task instructions")
    reward_function: Optional[Callable[[dict[str, Any], dict[str, Any]], tuple[float, str]]] = Field(
        None,
        description="Reward function to be used if valid_target_states is not provided",
    )
    valid_target_states: Optional[list[dict[str, Any]]] = Field(
        None,
        description="List of valid target states for binary reward (1 if reached, 0 otherwise)",
    )
    max_steps: int = Field(default=10, description="Maximum number of steps allowed")
    timeout_seconds: int = Field(default=60, description="Task timeout in seconds")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def model_post_init(self, __context: Any) -> None:
        """Validate that either reward_function or valid_target_states is provided."""
        if not self.reward_function and not self.valid_target_states:
            raise ValueError("Either reward_function or valid_target_states must be provided")
        if self.reward_function and self.valid_target_states:
            raise ValueError("Cannot specify both reward_function and valid_target_states")

    def get_environment_path(self, base_path: Optional[Path] = None) -> Path:
        """Get absolute path to environment file."""
        if base_path is None:
            base_path = Path.cwd()
        return base_path / self.environment.path

    def load_reward_function(
        self,
    ) -> Callable[[dict[str, Any], dict[str, Any]], tuple[float, str]]:
        """Load and return the reward function."""
        if self.valid_target_states:
            # Return built-in binary reward function
            return self._create_binary_reward_function()

        if not self.reward_function:
            raise ValueError("No reward function or valid_target_states specified")

        return self.reward_function

    def _create_binary_reward_function(
        self,
    ) -> Callable[[dict[str, Any], dict[str, Any]], tuple[float, str]]:
        """Create a binary reward function based on valid_target_states."""

        def binary_reward_function(initial_state: dict[str, Any], final_state: dict[str, Any]) -> tuple[float, str]:
            """Binary reward function that checks if final_state matches any valid target state."""
            if not self.valid_target_states:
                return 0.0, "No valid target states defined"

            for i, target_state in enumerate(self.valid_target_states):
                if self._states_match(final_state, target_state):
                    return 1.0, f"Reached valid target state {i + 1}"

            return 0.0, "Did not reach any valid target state"

        return binary_reward_function

    def _states_match(self, state1: dict[str, Any], state2: dict[str, Any]) -> bool:
        """Check if two states match by comparing all key-value pairs."""
        # Check that state1 contains all key-value pairs from state2
        for key, value in state2.items():
            if key not in state1:
                return False
            if state1[key] != value:
                return False
        return True

    @classmethod
    def from_hf_row(
        cls, row: dict[str, Any], reward_function_importer: Optional[Callable[[str], Optional[Callable]]] = None
    ) -> "TaskDefinition":
        """
        Create a TaskDefinition from a HuggingFace dataset row.

        This handles the stringified JSON fields and optional reward function importing
        that's specific to the HF dataset format.

        Args:
            row: Dictionary representing a row from the HF dataset
            reward_function_importer: Optional function to import reward functions by name

        Returns:
            TaskDefinition instance
        """
        # Parse stringified JSON fields
        initial_state = json.loads(row["initial_state"])
        environment = json.loads(row["environment"])
        instructions = json.loads(row["instructions"])
        metadata = json.loads(row["metadata"])

        # Handle valid_target_states (may be empty string)
        valid_target_states = None
        if row["valid_target_states"] and row["valid_target_states"].strip():
            valid_target_states = json.loads(row["valid_target_states"])

        # Handle reward_function (may be empty string)
        reward_function = None
        if row["reward_function"] and row["reward_function"].strip():
            if reward_function_importer:
                reward_function = reward_function_importer(row["reward_function"])
            else:
                # Store function name as string if no importer provided
                # This allows the caller to handle importing later
                pass

        return cls(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            environment=environment,
            initial_state=initial_state,
            instructions=instructions,
            reward_function=reward_function,
            valid_target_states=valid_target_states,
            max_steps=row["max_steps"],
            timeout_seconds=row["timeout_seconds"],
            metadata=metadata,
        )
