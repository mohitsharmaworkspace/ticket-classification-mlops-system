#!/usr/bin/env python3

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ml_pipeline.model_training import MLPModelTrainer
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    try:
        logger.info("=" * 60)
        logger.info("Starting Initial Model Training")
        logger.info("=" * 60)
        
        trainer = MLPModelTrainer(experiment_name="initial_training")
        
        logger.info("Running training pipeline with default data...")
        results = trainer.run_training_pipeline()
        
        logger.info("=" * 60)
        logger.info("Training Complete!")
        logger.info("=" * 60)
        logger.info(f"Metrics: {results['metrics']}")
        logger.info(f"Model Info: {results['model_info']}")
        logger.info("\nTrained model saved to: models/trained/mlp_classifier.pth")
        logger.info("The API will now use the trained MLP model for predictions.")
        
        return 0
        
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
