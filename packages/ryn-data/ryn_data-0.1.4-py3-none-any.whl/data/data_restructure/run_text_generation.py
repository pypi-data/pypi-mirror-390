import argparse
import csv
import logging
import random
import shutil
import time
from pathlib import Path

# Assuming your project structure allows these imports.
from data.data_restructure.restructure import Restructurer
from data.data_restructure.utils import generate_dataset_info

# Configure logging for the runner script
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def create_dummy_text_dataset(
    base_path: Path, num_samples: int
) -> None:
    """
    Creates a dummy text generation dataset with the expected structure.

    Args:
        base_path: The directory where the dataset's CSV will be created.
        num_samples: The total number of text samples to generate.
    """
    logger.info(
        f"Generating a dummy text dataset with {num_samples} samples at '{base_path}'..."
    )

    base_path.mkdir(parents=True, exist_ok=True)

    headers = ["instruction", "input", "output", "split"]

    # Sample data to pull from
    sample_tasks = [
        ("Summarize the following text.", "Python is a high-level, interpreted, general-purpose programming language. Its design philosophy emphasizes code readability...", "Python is a popular programming language known for readability."),
        ("Translate this to Spanish.", "The weather is beautiful today.", "El tiempo es hermoso hoy."),
        ("What is the main ingredient in guacamole?", "", "Avocado"),
        ("Write a tagline for a coffee shop.", "The perfect place to start your day.", "Your daily grind, perfected."),
    ]
    
    # Define split distribution: 70% train, 15% validation, 15% test
    split_distribution = ["train"] * 70 + ["validation"] * 15 + ["test"] * 15
    
    dataset_rows = []
    for i in range(num_samples):
        instr, inp, outp = random.choice(sample_tasks)
        row = {
            "instruction": instr,
            "input": inp if inp else "", # Ensure empty string for no input
            "output": f"{outp} (Sample {i})", # Make output unique
            "split": random.choice(split_distribution),
        }
        dataset_rows.append(row)

    # Write data.csv
    data_path = base_path / "data.csv"
    with open(data_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(dataset_rows)

    logger.info("Dummy text dataset generation complete.")


def verify_output(output_path: Path) -> bool:
    """
    Performs a basic check to see if the restructuring was successful.
    """
    logger.info(f"Verifying output at '{output_path}'...")
    if not output_path.is_dir():
        logger.error("Output path is not a directory.")
        return False

    # Check for split directories
    expected_splits = ["train", "test", "validation"]
    found_splits = [d.name for d in output_path.iterdir() if d.is_dir()]
    
    if not any(split in found_splits for split in expected_splits):
        logger.error(f"No split directories found in output. Found: {found_splits}")
        return False
        
    # Check for the Spark success marker in at least one split
    if not (output_path / "train" / "_SUCCESS").exists():
        logger.error("'_SUCCESS' file not found in 'train' split. Spark job may have failed.")
        return False

    logger.info(f"Verification successful. Found splits: {found_splits}")
    return True


def main(args):
    """
    Main execution function.
    """
    output_dir = (Path(__file__).parent / "text_generation_test_output").resolve()

    # Clean up previous run's output
    if output_dir.exists():
        logger.warning(f"Removing existing output directory: '{output_dir}'")
        shutil.rmtree(output_dir)
    
    output_dir.mkdir(parents=True)
    
    input_data_path = output_dir / "source_text_dataset"
    output_parquet_path = output_dir / "restructured_text_dataset"

    logger.info(f"Input data will be generated in: {input_data_path}")
    
    # 1. Build the dummy dataset file(s)
    create_dummy_text_dataset(input_data_path, args.num_samples)

    # 2. Run and time the restructuring process
    logger.info("-" * 50)
    logger.info(
        f"Starting restructuring for 'text_generation' task with {args.num_samples} samples..."
    )
    start_time = time.perf_counter()

    try:
        restructurer = Restructurer(task_type="text_generation")
        restructurer.restructure(
            input_path=input_data_path,
            output_path=output_parquet_path,
        )
    except Exception as e:
        logger.error(f"An error occurred during restructuring: {e}", exc_info=True)
        return

    end_time = time.perf_counter()
    duration = end_time - start_time
    logger.info(f"Restructuring completed in {duration:.4f} seconds.")
    logger.info("-" * 50)

    # 3. Verify the output and generate dataset_info.json
    if not verify_output(output_parquet_path):
        logger.error("Restructuring process failed verification.")
    else:
        logger.info("Restructuring process completed and verified successfully.")
        
        logger.info("-" * 50)
        # generate_dataset_info(
        #     output_path=output_parquet_path,
        #     source_input_path=input_data_path, # Path to original data
        #     dataset_name="dummy_text_generation",
        #     task_type="text_generation"
        # )

        print("\n" + "="*60)
        print(f"✅ Success! The output files are saved in: {output_dir.resolve()}")
        print("You can now inspect the Parquet files and 'dataset_info.json'.")
        print("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test runner for Text Generation dataset restructuring.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=5000,
        help="Number of dummy text samples to generate for the test.",
    )
    
    args = parser.parse_args()
    main(args)