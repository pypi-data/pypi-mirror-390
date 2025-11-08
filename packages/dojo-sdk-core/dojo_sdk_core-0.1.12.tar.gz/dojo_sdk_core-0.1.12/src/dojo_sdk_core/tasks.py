"""Task definition and loading system."""

import string
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional

from datasets import load_dataset

from .dojos import Dojo
from .dojos.dojos_loader import load_dojos
from .dojos.rewards import get_reward_function
from .models import TaskDefinition


class TaskLoader(ABC):
    """Abstract base class for task loaders."""

    @abstractmethod
    def load_task(self, task_path: str) -> TaskDefinition:
        """Load a task definition from a JSON file."""
        pass

    @abstractmethod
    def load_dojo_tasks(self, dojo_name: str) -> List[TaskDefinition]:
        """Load all tasks from a benchmark directory."""
        pass

    @abstractmethod
    def list_tasks(self, category: Optional[str] = None) -> dict[str, TaskDefinition]:
        """List all available tasks."""
        pass


class PyTaskLoader:
    """Loads tasks from python-based task registry"""

    @staticmethod
    def _register_all(bms: list[Dojo]) -> dict[string, Dojo]:
        result = {}
        for bm in bms:
            result[bm.get_id()] = bm

        return result

    def __init__(self):
        self.benchmarks_by_name = PyTaskLoader._register_all(load_dojos())

    def load_task(self, benchmark_task_path: str) -> TaskDefinition:
        split_path = benchmark_task_path.split("/")
        benchmark_name = split_path[0]
        task_id = split_path[1]
        tasks = self.load_benchmark_tasks(benchmark_name)
        for task in tasks:
            if task.id == task_id:
                return task
        raise ValueError(f"Task {task_id} not found in benchmark {benchmark_name}")

    def load_benchmark_tasks(self, benchmark_name: str) -> List[TaskDefinition]:
        return self.benchmarks_by_name[benchmark_name].get_tasks_list()

    def list_tasks(self, category: Optional[str] = None) -> dict[str, TaskDefinition]:
        raise NotImplementedError("List tasks not implemented")


class RemoteTaskLoader:
    """Loads tasks from a Hugging Face dataset."""

    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        self.dataset = None
        self.tasks_cache = None

    def _load_dataset(self):
        """Lazy load the HF dataset."""
        if self.dataset is None:
            self.dataset = load_dataset(self.dataset_name)["train"]
            print(f"✓ Loaded {len(self.dataset)} tasks from HF dataset {self.dataset_name}")
        return self.dataset

    def _import_reward_function(
        self, function_name: str
    ) -> Optional[Callable[[dict[str, Any], dict[str, Any]], tuple[float, str]]]:
        """Import a reward function by name from the centralized rewards module."""
        if not function_name or function_name == "":
            return None

        return get_reward_function(function_name)

    def _get_all_tasks(self) -> List[TaskDefinition]:
        """Load all tasks from HF dataset and convert to TaskDefinition objects."""
        if self.tasks_cache is None:
            dataset = self._load_dataset()
            tasks = []

            for row in dataset:
                # Use the clean constructor that handles HF-specific parsing
                task = TaskDefinition.from_hf_row(row, reward_function_importer=self._import_reward_function)
                tasks.append(task)

            self.tasks_cache = tasks
            print(f"✓ Converted {len(tasks)} HF tasks to TaskDefinition objects")

        return self.tasks_cache

    def load_task(self, task_path: str) -> TaskDefinition:
        """Load a specific task by dojo/task_id path."""
        # Parse task_path like "action-tester/must-click"
        if "/" not in task_path:
            raise ValueError(f"Invalid task path format: {task_path}. Expected 'dojo/task_id'")

        dojo_name, task_id = task_path.split("/", 1)

        all_tasks = self._get_all_tasks()

        # Find task by task_id (dojo info is embedded in the task path, not metadata)
        for task in all_tasks:
            if task.id == task_id:
                return task

        raise ValueError(f"Task {task_id} not found in dojo {dojo_name}")

    def list_tasks(self, category: Optional[str] = None) -> dict[str, TaskDefinition]:
        raise NotImplementedError("List tasks not implemented")
