from .pipeline import Pipeline
from .logging_config import setup_logger

logger = setup_logger(__name__)

def main():
    try:
        my_pipeline = Pipeline()
        my_pipeline.run()
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        # print(f"An error occured: {e}")


if __name__ == "__main__":
    main()