
import torch
from torch.utils.data import Dataset
from pathlib import Path
from datasets import load_dataset
from PIL import Image
from typing import Optional, Callable, Tuple,Dict, List

class ImageClassificationDataset(Dataset):
    """
    image classification dataset.

    This dataset reads metadata from a single Parquet file and constructs
    image paths on-the-fly to reduce initialization time and memory usage.

    Args:
        data_dir (str): The root directory where datasets are stored.
        dataset_name (str): The specific name of the dataset folder.
        split (str): The data split to use (e.g., 'train', 'test').
        transform (callable, optional): A function/transform that takes in a PIL image
            and returns a transformed version.
    """
    def __init__(
        self,
        data_dir: str,
        dataset_name: str,
        split: str,
        transform: Optional[Callable] = None
    ):
        self.data_dir = data_dir
        self.dataset_name = dataset_name
        self.split = split
        self.transform = transform

        metadata_path = Path(data_dir) / dataset_name / "metadata.parquet"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found at {metadata_path}")
        
        # Load the entire split into memory once. This is efficient.
        dataset_split = load_dataset("parquet", data_files=str(metadata_path))["train"].filter(lambda x: x['split'] == split)

        
        self.root_dir = Path(data_dir) / dataset_name
        self.relative_paths = dataset_split['file_path']
        self.labels = dataset_split['label']
        
        # Ensure the data is consistent
        assert len(self.relative_paths) == len(self.labels), "Mismatch between number of images and labels."

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        label = self.labels[idx]

        image_path = self.root_dir / self.relative_paths[idx]

        try:
            image = Image.open(image_path).convert("RGB")
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found at {image_path}. "
                                    f"Check if your parquet file paths are correct relative to '{self.root_dir}'.")

        if self.transform:
            image = self.transform(image)

        return image, label

class TextGenerationDataset(Dataset):
    """
    A PyTorch Dataset for loading instruction-response pairs for text generation.
    
    This class reads sharded Parquet files, extracts user instructions and
    assistant responses from a 'messages' column, and stores them for retrieval.
    """
    def __init__(self, data_dir: str, dataset_name: str, split: str):
        """
        Loads and processes the instruction-response data.
        """
        # --- 1. Loading of Instruction and Response Part ---

        # Construct the full path to the directory containing the split's data files
        split_path = Path(data_dir) / dataset_name / split
        if not split_path.exists():
            raise FileNotFoundError(f"Data directory for split '{split}' not found at {split_path}")

        raw_dataset = load_dataset("parquet", data_files=str(split_path)+"/*.parquet",)['train']

        # Initialize lists to hold our processed data
        self.instructions: List[str] = []
        self.responses: List[str] = []
        
        # Iterate through the raw dataset to parse the 'messages' column
        for example in raw_dataset:
            messages = example['messages']
            
            # Ensure the conversation has at least a user and assistant turn
            if len(messages) >= 2 and messages[0]['role'] == 'user' and messages[1]['role'] == 'assistant':
                self.instructions.append(messages[0]['content'])
                self.responses.append(messages[1]['content'])
            # Malformed examples are skipped

    def __len__(self) -> int:
        """
        Returns the total number of instruction-response pairs.
        """
        return len(self.instructions)

    def __getitem__(self, idx: int) -> Dict[str, str]:
        """
        Retrieves the instruction and response at a given index.

        Note: In a full pipeline, you would tokenize the text here or in a
        data collator to prepare it for the model. This example returns
        the raw text for clarity.
        """
        return {
            "instruction": self.instructions[idx],
            "response": self.responses[idx]
        }

# # #print sample image from the dataset
# if __name__ == "__main__":
#     dataset = ImageClassificationDataset(data_dir="downloaded_datasett",dataset_name="microsoft-cats_vs_dogs",split="train")
#     import matplotlib.pyplot as plt

#     image, label = dataset[100]
    
#     #save image
#     plt.imshow(image)
#     plt.title(f"Label: {label}")
#     plt.savefig("sample_image.png")
#     plt.show()

#     text_dataset = TextGenerationDataset(data_dir="/home/mlops/abolfazl/tools/data_platform/ryn/data/data_restructure/text_generation_test_output", dataset_name="restructured_text_dataset", split="validation")

#     sample = text_dataset[10]
#     print("Instruction:", sample["instruction"])
#     print("Response:", sample["response"])

