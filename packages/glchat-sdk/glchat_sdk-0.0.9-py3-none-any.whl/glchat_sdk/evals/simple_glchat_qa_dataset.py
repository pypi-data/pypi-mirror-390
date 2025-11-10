"""Simple QA Dataset for Demonstrations.

This module provides a simple QA dataset for quick demonstrations and testing.
The dataset is loaded from a local CSV file when requested via the load function.

Authors:
    Christina Alexandra (christina.alexandra@gdplabs.id)

References:
    NONE
"""

from pathlib import Path

from gllm_evals.dataset.dict_dataset import DictDataset


def load_simple_glchat_qa_dataset() -> DictDataset:
    """Load the simple GLChat QA dataset from the local CSV file.

    The dataset contains question-answer pairs with generated responses and contexts,
    suitable for RAG evaluation and testing.

    Returns:
        DictDataset: The loaded simple GLChat QA dataset.
            
    Raises:
        FileNotFoundError: If the CSV file doesn't exist.
        ValueError: If the CSV file is empty or malformed.
    """
    current_dir = Path(__file__).parent
    csv_path = current_dir / "dataset_example" / "glchat_qa_data.csv"
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Simple GLChat QA dataset CSV file not found at {csv_path}")
    
    try:
        return DictDataset.from_csv(str(csv_path))
    except (FileNotFoundError, ValueError) as e:
        raise
    except Exception as e:
        raise ValueError(f"Error loading simple QA dataset: {e}") from e


# Export the function for lazy loading
__all__ = ["load_simple_glchat_qa_dataset"] 
