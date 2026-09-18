from abc import ABC, abstractmethod


class BaseRunner(ABC):
    @abstractmethod
    def run_case(self, task: dict, case: dict) -> dict | None:
        """Run a single case and return results.

        Returns dict with keys:
            answers: {question_name: {"value": ..., "confidence": float}}
            latency_ms: float
            input_tokens: int
            output_tokens: int
        Returns None on unrecoverable failure.
        """
        ...

    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def model_string(self) -> str: ...
