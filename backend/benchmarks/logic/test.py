from scrap_llm.services.llm.experiment_manager import ExperimentManager
from scrap_llm.services.llm.llm_manager import LLMManager
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main function to run the experiment manager test."""
    try:
        # Initialize the experiment manager with correct model name
        experiment_manager = ExperimentManager(
            llm_manager_extractor=LLMManager(
                models=[
                    "gpt-4o-mini"
                ],  # Fixed model name from gpt-4.1-mini to gpt-4o-mini
                prompt_args="product_urls",
                action="extracting_chat",
                output_schema=None,
            )
        )

        # Get experiments from the dataset
        logger.info("Fetching experiments from dataset 'test'...")
        experiments = await experiment_manager.get_experiments("extraction_dataset")

        # logger.info(f"Found {len(experiments)} experiments in dataset")

        # # Print experiment details
        # for i, experiment in enumerate(experiments):
        #     logger.info(f"Experiment {i+1}: ID={experiment.id}")

        return experiments

    except Exception as e:
        logger.error(f"Error running experiment manager test: {e}")
        raise


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
