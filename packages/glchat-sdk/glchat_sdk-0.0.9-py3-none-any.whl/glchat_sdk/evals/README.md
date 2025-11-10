# GLChat Evaluation Module

## Installation

⚠️ **Note**: This evaluation module is currently **private** and requires special access. To use the evaluation functionality, you need to install the package with the `evals` extra.

### Using Poetry

```bash
# Add the private repository
poetry source add --priority=explicit gen-ai https://glsdk.gdplabs.id/gen-ai/simple

# Configure authentication
poetry config http-basic.gen-ai oauth2accesstoken "$(gcloud auth print-access-token)"

# Install with evals dependency group (uses Poetry's dependency groups with source configuration)
poetry install --with evals
```

### Using pip

The private repository requires authentication.

```bash
# Install using Google Cloud access token
pip install glchat-sdk[evals] --extra-index-url https://oauth2accesstoken:$(gcloud auth print-access-token)@glsdk.gdplabs.id/gen-ai/simple
```


## What is `evaluate_glchat`?

`evaluate_glchat` is a convenience function that provides a streamlined interface for evaluating GLChat models using the existing `gllm-evals` framework. It eliminates the need to manually implement inference functions by providing a pre-built GLChat integration.

### Key Features

- **Simplified Evaluation**: Automatically handles GLChat inference function creation and resource management
- **Multiple Evaluators**: Support for various evaluation metrics and frameworks
- **Experiment Tracking**: Built-in support for Langfuse and simple experiment tracking
- **File Attachments**: AWS S3 integration for handling file attachments in conversations
- **Flexible Configuration**: Environment variable fallback and comprehensive configuration options

### What is it for?

The `evaluate_glchat` function is designed for:

1. **Model Performance Assessment**: Evaluate how well GLChat's responses perform on specific datasets
2. **Quality Assurance**: Run automated evaluations to ensure model quality and consistency
3. **A/B Testing**: Compare different model configurations or chatbot settings
4. **Research & Development**: Conduct systematic evaluations for model improvement
5. **Production Monitoring**: Track model performance over time in production environments

To learn more details, you can visit [here](https://gdplabs.gitbook.io/sdk/tutorials/evaluation/getting-started).

## Example Usage

### Simple Example

Here's a minimal example to get started quickly:

```python
import asyncio
from glchat_sdk.evals import evaluate_glchat, GLChatConfig
from glchat_sdk.evals.simple_glchat_qa_dataset import load_simple_glchat_qa_dataset
from gllm_evals.evaluator.geval_generation_evaluator import GEvalGenerationEvaluator

async def simple_evaluation():
    """Simple GLChat evaluation example."""
    
    # Basic configuration
    config = GLChatConfig(
        base_url="https://your-glchat-api.com",  # can also be in env var `GLCHAT_BASE_URL`
        api_key="your-api-key",  # recommended to be put in env var `GLCHAT_API_KEY`
        chatbot_id="your-chatbot-id",
        username="your-username"
    )
    
    # Run evaluation with a default simple evaluator - results will be generated in CSV
    results = await evaluate_glchat(
        data=load_simple_glchat_qa_dataset(),
        evaluators=[GEvalGenerationEvaluator(model_credentials="your-openai-key")],
        config=config
    )
    
    print(f"Results: {results}")

if __name__ == "__main__":
    asyncio.run(simple_evaluation())
```

### Complete Example

Here's a comprehensive example with all features:

```python
import asyncio
import json
import os

from langfuse import get_client
from gllm_evals.evaluator.geval_generation_evaluator import GEvalGenerationEvaluator
from glchat_sdk.evals import evaluate_glchat, GLChatConfig
from glchat_sdk.evals.simple_glchat_qa_dataset import load_simple_glchat_qa_dataset
from gllm_evals.experiment_tracker.langfuse_experiment_tracker import LangfuseExperimentTracker
from gllm_evals.experiment_tracker.simple_experiment_tracker import SimpleExperimentTracker


async def main():
    """Main function demonstrating GLChat evaluation."""
    
    # Configure GLChat connection
    config = GLChatConfig(
        base_url="https://your-glchat-api.com",  # can also be in env var `GLCHAT_BASE_URL`
        api_key="your-api-key",  # recommended to be put in env var `GLCHAT_API_KEY`
        chatbot_id="general-purpose",
        username="your-username",
        
        # Optional configuration
        model_name="GPT 4.1 Mini",
        enable_pii=False,
        search_type="normal",
        expiry_days=1,  # Expiry for shared conversation. For testing purpose, set to 1 day. Set to None for no expiry.
        
        # If attachment is used, set the following fields
        s3_bucket="your-s3-bucket",
        s3_prefix="glchat",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_region=os.getenv("AWS_REGION"),
    )
    
    # Run evaluation with multiple evaluators
    results = await evaluate_glchat(
        data=load_simple_glchat_qa_dataset(),
        evaluators=[
            GEvalGenerationEvaluator(
                model_credentials=os.getenv("OPENAI_API_KEY")
            )
        ],
        config=config,
        experiment_tracker=LangfuseExperimentTracker(
            langfuse_client=get_client()
        )  # To use LangfuseExperimentTracker, make sure environment variables such as `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST` are already set
    )
    
    print(f"Results: {json.dumps(results, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration Options

### Required Parameters

- `base_url`: GLChat API base URL (can use `GLCHAT_BASE_URL` environment variable)
- `api_key`: GLChat API key (can use `GLCHAT_API_KEY` environment variable)
- `chatbot_id`: GLChat chatbot identifier
- `username`: GLChat username for the given chatbot identifier

### Optional Parameters

- `model_name`: Specific model to use for evaluation
- `enable_pii`: Enable PII anonymization/deanonymization (default: `False`)
- `search_type`: Search type configuration (options: `normal`, `search`, `web`, `deep_research`, `essentials_deep_research`, `comprehensive_deep_research`)
- `include_states`: Whether to include states in the response (default: `True`)
- `expiry_days`: Number of days for shared conversation expiry (default: `None` for no expiry)

### AWS S3 Configuration (for file attachments)

- `s3_bucket`: S3 bucket for file attachments
- `s3_prefix`: S3 prefix/directory for files
- `aws_access_key_id`: AWS access key
- `aws_secret_access_key`: AWS secret key
- `aws_region`: AWS region

## Environment Variables

You can use environment variables to avoid hardcoding sensitive information:

```bash
export GLCHAT_BASE_URL="https://your-glchat-api.com"
export GLCHAT_API_KEY="your-api-key"
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export AWS_REGION="us-east-1"
export OPENAI_API_KEY="your-openai-key"  # For evaluators

# Optional: Langfuse experiment tracking configuration
export LANGFUSE_PUBLIC_KEY=""
export LANGFUSE_SECRET_KEY=""
export LANGFUSE_HOST="https://langfuse.obrol.id"
```

If you do not have any Langfuse configuration, you can visit [this guide](https://gdplabs.gitbook.io/sdk/tutorials/evaluation/experiment-tracker#new-user-configuration) to create a new one.

## Available Datasets

The module includes a simple QA dataset for testing:

```python
from glchat_sdk.evals.simple_glchat_qa_dataset import load_simple_glchat_qa_dataset

# Load the built-in dataset
dataset = load_simple_glchat_qa_dataset()
```

You can also use custom datasets by implementing the `BaseDataset` interface from the `gllm-evals` framework.

## Experiment Tracking

The evaluation supports two experiment tracking options:

1. **LangfuseExperimentTracker**: For advanced experiment tracking and visualization
2. **SimpleExperimentTracker**: For local file-based tracking

Results are automatically saved and can be analyzed for model performance insights.

## Dependencies

The evaluation module requires the following additional dependencies (installed with `[evals]` extra):
- `gllm-core-binary>=0.3.0,<0.4.0`
- `gllm-evals-binary>=0.0.24,<0.0.25`
- `langfuse>=3.2.1,<4.0.0`
- `aioboto3>=15.2.0,<16.0.0`
- `pytest-asyncio>=0.23.6,<0.24.0`
