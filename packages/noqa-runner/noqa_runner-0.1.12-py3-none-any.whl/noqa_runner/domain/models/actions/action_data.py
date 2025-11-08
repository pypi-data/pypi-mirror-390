from __future__ import annotations

from typing import Union

from pydantic import BaseModel, Field

from noqa_runner.domain.models.actions.activate_app import ActivateApp
from noqa_runner.domain.models.actions.background_app import BackgroundApp
from noqa_runner.domain.models.actions.input_text import InputText
from noqa_runner.domain.models.actions.open_url import OpenUrl
from noqa_runner.domain.models.actions.restart_app import RestartApp
from noqa_runner.domain.models.actions.scroll import Scroll
from noqa_runner.domain.models.actions.stop import Stop
from noqa_runner.domain.models.actions.tap import Tap
from noqa_runner.domain.models.actions.terminate_app import TerminateApp
from noqa_runner.domain.models.actions.wait import Wait
from noqa_runner.domain.models.state.condition import Condition


class ActionData(BaseModel):
    """Response schema for mobile actions"""

    action: Union[
        Tap,
        InputText,
        # Swipe,
        Scroll,
        Wait,
        Stop,
        ActivateApp,
        BackgroundApp,
        TerminateApp,
        RestartApp,
        OpenUrl,
    ] = Field(discriminator="name")
    reasoning: str = Field(
        description="Explanation of your decision and reasoning for this action"
    )
    conditions_updates: list[Condition] = Field(
        default=[], description="List of test condition updates"
    )
