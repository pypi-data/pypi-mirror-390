"""
Modular reward functions organized by game/application.

This package contains reward validation functions for different dojos,
organized into separate modules for maintainability.
"""

from dojo_sdk_core.dojos.rewards.game_2048 import REWARD_FUNCTIONS_2048
from dojo_sdk_core.dojos.rewards.linear import REWARD_FUNCTIONS_LINEAR
from dojo_sdk_core.dojos.rewards.linkedin import REWARD_FUNCTIONS_LINKEDIN
from dojo_sdk_core.dojos.rewards.minesweeper import REWARD_FUNCTIONS_MINESWEEPER
from dojo_sdk_core.dojos.rewards.salesforce import REWARD_FUNCTIONS_SALESFORCE
from dojo_sdk_core.dojos.rewards.tic_tac_toe import REWARD_FUNCTIONS_TIC_TAC_TOE

# Unified registry of all reward functions
REWARD_FUNCTIONS = {
    **REWARD_FUNCTIONS_2048,
    **REWARD_FUNCTIONS_LINEAR,
    **REWARD_FUNCTIONS_LINKEDIN,
    **REWARD_FUNCTIONS_SALESFORCE,
    **REWARD_FUNCTIONS_TIC_TAC_TOE,
    **REWARD_FUNCTIONS_MINESWEEPER,
}


def get_reward_function(name: str):
    """Get a reward function by name from the unified registry."""
    return REWARD_FUNCTIONS.get(name)


__all__ = ["REWARD_FUNCTIONS", "get_reward_function"]
