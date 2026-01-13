import asyncio
from typing import Callable, Union

from uav_assistant.domain.models import OptimizerStep, OptimizerFinal, OptimizerDiagnostic, OptimizerRouteValidation

TraceFn = Callable[[OptimizerStep], None]
TraceQueue = asyncio.Queue[Union[OptimizerStep, OptimizerFinal, OptimizerDiagnostic, OptimizerRouteValidation]]