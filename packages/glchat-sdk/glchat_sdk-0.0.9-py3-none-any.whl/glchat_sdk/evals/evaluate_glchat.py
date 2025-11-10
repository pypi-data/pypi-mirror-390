"""GLChat evaluation convenience function.

This module provides a streamlined interface for evaluating GLChat models using the
existing gllm-evals framework. It eliminates the need to manually implement inference
functions by providing a pre-built GLChat integration.

Code Quality Requirement: All functions must enforce maximum 5 lines when possible,
creating separate helper files if functions cannot be broken down further.

Authors:
    Christina Alexandra (christina.alexandra@gdplabs.id)

References:
    NONE
"""

from functools import partial
from typing import Any

from gllm_evals.dataset.dataset import BaseDataset
from gllm_evals.evaluate import evaluate
from gllm_evals.evaluator import BaseEvaluator
from gllm_evals.experiment_tracker.experiment_tracker import BaseExperimentTracker
from gllm_evals.experiment_tracker.simple_experiment_tracker import SimpleExperimentTracker
from gllm_evals.metrics.metric import BaseMetric
from gllm_evals.types import EvaluationResult

from glchat_sdk.evals.config import GLChatConfig
from glchat_sdk.evals.constant import GeneralKeys, GLChatDefaults
from glchat_sdk.evals.inference import glchat_inference


async def evaluate_glchat(
    data: str | BaseDataset,
    config: GLChatConfig,
    evaluators: list[BaseEvaluator | BaseMetric],
    experiment_tracker: BaseExperimentTracker | None = None,
    batch_size: int = 10,
    **kwargs: Any,
) -> EvaluationResult:
    """Evaluate GLChat responses using the gllm-evals framework.

    This convenience function provides a streamlined interface for evaluating GLChat responses
    by automatically handling GLChat inference function creation and resource management.

    Args:
        data (str | BaseDataset): The dataset to evaluate. Can be a dataset name string
            or a BaseDataset instance.
        config (GLChatConfig): GLChat configuration containing API credentials and settings.
        evaluators (list[BaseEvaluator | BaseMetric]): List of evaluators to run on the data.
        experiment_tracker (BaseExperimentTracker | None): Experiment tracker for logging.
            Defaults to SimpleExperimentTracker if not provided.
        batch_size (int): Number of samples to process concurrently. Defaults to 10.
        **kwargs (Any): Additional configuration parameters passed to the evaluation framework.

    Returns:
        EvaluationResult: Evaluation results from all evaluators.

    Raises:
        ValueError: If required configuration is missing.
        Exception: For other errors during evaluation.

    Example:
        >>> from glchat_sdk.evals import evaluate_glchat, GLChatConfig
        >>> from gllm_evals.evaluator.geval_generation_evaluator import GEvalGenerationEvaluator
        >>>
        >>> config = GLChatConfig(
        ...     base_url="https://api.example.com",
        ...     api_key="your-api-key",
        ...     chatbot_id="your-chatbot-id"
        ... )
        >>>
        >>> evaluators = [GEvalGenerationEvaluator(model_credentials="openai-key")]
        >>>
        >>> results = await evaluate_glchat(
        ...     data="my-dataset",
        ...     config=config,
        ...     evaluators=evaluators
        ... )
    """
    # Use SimpleExperimentTracker as default if none provided
    if experiment_tracker is None:
        experiment_tracker = SimpleExperimentTracker(
            project_name=GLChatDefaults.PROJECT_NAME, output_dir=GLChatDefaults.OUTPUT_DIR
        )

    # Create inference function with GLChat integration
    inference_fn = _create_glchat_inference_fn(config)

    # Create tags if not provided
    kwargs = _create_tags_if_not_provided(kwargs)

    # Run evaluation using the existing evaluate function
    try:
        return await evaluate(
            data=data,
            inference_fn=inference_fn,
            evaluators=evaluators,
            experiment_tracker=experiment_tracker,
            batch_size=batch_size,
            **kwargs,
        )
    except Exception as e:
        raise ValueError(f"Failed to evaluate GLChat: {str(e)}") from e


def _create_glchat_inference_fn(config: GLChatConfig) -> Any:
    """Create a GLChat inference function with the given configuration.

    Args:
        config (GLChatConfig): GLChat configuration containing API credentials and settings.

    Returns:
        Any: Partial function that can be used as inference_fn in evaluate()
    """
    # Create a partial function that binds the config
    return partial(
        glchat_inference,
        config=config,
    )


def _create_tags_if_not_provided(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Create tags if not provided.

    Args:
        kwargs (dict[str, Any]): The keyword arguments.

    Returns:
        dict[str, Any]: The keyword arguments with tags.
    """
    if GeneralKeys.TAGS not in kwargs:
        kwargs[GeneralKeys.TAGS] = []

    if not isinstance(kwargs[GeneralKeys.TAGS], list):
        kwargs[GeneralKeys.TAGS] = [kwargs[GeneralKeys.TAGS]]

    if GeneralKeys.EVALUATION_TAG not in kwargs[GeneralKeys.TAGS]:
        kwargs[GeneralKeys.TAGS].append(GeneralKeys.EVALUATION_TAG)
    if GeneralKeys.GLCHAT_TAG not in kwargs[GeneralKeys.TAGS]:
        kwargs[GeneralKeys.TAGS].append(GeneralKeys.GLCHAT_TAG)

    return kwargs
