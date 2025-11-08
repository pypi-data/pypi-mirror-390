import time
from typing import Any, Optional, Type, TypeVar

from dojo_sdk_client.base_dojo_client import BaseDojoClient, TaskStatus
from dojo_sdk_core.tasks import RemoteTaskLoader
from dojo_sdk_core.types import ActionType as DojoActionType
from openenv_core import HTTPEnvClient, StepResult

from .models import DojoAction, DojoObservation

_T = TypeVar("_T", bound="DojoEnvClient")


class _ExecState:
    def __init__(self, exec_id: str):
        self.exec_id = exec_id
        self.step = 1


class DojoEnvClient(HTTPEnvClient[DojoAction, DojoObservation]):
    def __init__(self, task_id: str, api_key: str):
        super().__init__(base_url="")

        self._dojo_client = BaseDojoClient(api_key=api_key)
        self._task_id = task_id
        task_loader = RemoteTaskLoader(dataset_name="chakra-labs/dojo-bench-mini")
        self._task_def = task_loader.load_task(self._task_id)
        self._exec_state: Optional[_ExecState] = None

    @classmethod
    def from_docker_image(cls: Type[_T], image) -> _T:
        raise Exception("Unsupported operation")

    def reset(self) -> StepResult[DojoObservation]:
        # close previous task if it exists
        if self._exec_state:
            self._dojo_client.stop_task_sync(self._exec_state.exec_id)
            self._exec_state = None

        # create task
        exec_id = self._dojo_client.create_task_sync(self._task_id, self._task_def.initial_state)
        self._exec_state = _ExecState(exec_id=exec_id)

        # start task
        self._dojo_client.start_task_sync(self._exec_state.exec_id)

        # wait until started
        status = self._dojo_client.get_task_status_sync(self._exec_state.exec_id)
        while status.status == TaskStatus.QUEUED:
            time.sleep(1)
            status = self._dojo_client.get_task_status_sync(self._exec_state.exec_id)

        return StepResult(
            observation=DojoObservation(task_response=status),
            reward=0.0,
            done=False,
        )

    def step(self, action: DojoAction) -> StepResult[DojoObservation]:
        # submit action
        self._dojo_client.submit_action_sync(
            self._exec_state.exec_id,
            action.action.model_dump(),
            action.reasoning,
            action.raw_response,
        )

        # get state periodically until action has been applied
        status = self._dojo_client.get_task_status_sync(self._exec_state.exec_id)
        while status.status == TaskStatus.RUNNING and status.step == self._exec_state.step:
            time.sleep(1)
            status = self._dojo_client.get_task_status_sync(self._exec_state.exec_id)

        if status.status != TaskStatus.RUNNING:
            raise (f"ERROR: task no longer RUNNING. Current status: {status.status}")

        # run reward function
        reward, _ = self._task_def.load_reward_function()(self._task_def.initial_state, status.state)

        # save score
        self._dojo_client.submit_step_score_sync(self._exec_state.exec_id, self._exec_state.step, reward)

        # check if we are done
        done = action.action.type == DojoActionType.DONE or self._exec_state.step >= self._task_def.max_steps

        self._exec_state.step += 1

        return StepResult(
            observation=DojoObservation(task_response=status),
            reward=reward,
            done=done,
        )

    def state(self) -> Any:
        status = self._dojo_client.get_task_status_sync(self._exec_state.exec_id)
        return status.state

    def close(self) -> None:
        if self._exec_state:
            self._dojo_client.stop_task_sync(self._exec_state.exec_id)
            self._exec_state = None

    def _step_payload(self, action: DojoAction) -> dict:
        pass

    def _parse_result(self, payload: dict) -> StepResult[DojoObservation]:
        pass

    def _parse_state(self, payload: dict) -> Any:
        pass
