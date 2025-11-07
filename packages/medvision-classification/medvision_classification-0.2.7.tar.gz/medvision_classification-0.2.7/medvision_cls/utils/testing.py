"""
Testing module for MedVision Classification
"""

import torch
import pytorch_lightning as pl
from typing import Dict, Any, Optional
import os
import json
import logging

from .helpers import setup_logging, load_config, create_output_dirs


def test_model(
    config_file: str,
    checkpoint_path: str,
    debug: bool = False,
    output_dir: Optional[str] = None
):
    """
    Test a trained classification model
    
    Args:
        config_file: Path to configuration file
        checkpoint_path: Path to model checkpoint
        debug: Enable debug mode
        save_predictions: Whether to save predictions
        output_dir: Directory to save outputs
    """
    # Import here to avoid circular imports
    from ..models import ClassificationLightningModule
    from ..datasets import get_datamodule
    
    # Load configuration
    config = load_config(config_file)
    
    # Setup logging
    setup_logging(debug=debug)
    logger = logging.getLogger(__name__)

    # Create output directories
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = config.get("outputs", {}).get("output_dir", "outputs/test")
        create_output_dirs({"output_dir": output_dir})

    # Set seed
    pl.seed_everything(config.get("seed", 42))
    
    # Setup data module
    data_config = config.get("data", {})
    data_module = get_datamodule(data_config)
    
    # Setup data module for testing
    data_module.setup("test")
    
    # Load model from checkpoint
    model = ClassificationLightningModule.load_from_checkpoint(
        checkpoint_path,
        model_config=config.get("model", {}),
        loss_config=config.get("model", {}).get("loss", {}),
        optimizer_config=config.get("model", {}).get("optimizer", {}),
        scheduler_config=config.get("model", {}).get("scheduler", {}),
        metrics_config=config.get("model", {}).get("metrics", {})
    )
    
    # Setup trainer for testing
    test_config = config.get("test", {})
    trainer = pl.Trainer(
        accelerator=test_config.get("accelerator", "gpu"),
        devices=test_config.get("devices", 1),
        precision=test_config.get("precision", 16),
        logger=False,
        enable_progress_bar=True,
        enable_model_summary=False,
    )
    
    # Run test
    test_results = trainer.test(model, data_module)
    
    logger.info("Testing finished.")

    # Save test results
    save_metrics = config.get("training", {}).get("save_metrics", True)
    if save_metrics and test_results:
        result_path = os.path.join(output_dir, "results.json")
        
        test_metrics = {k: float(v) for k, v in test_results[0].items()}
        
        final_metrics = {
            "test_metrics": test_metrics,
            "checkpoint_path": checkpoint_path,
        }
        
        with open(result_path, "w") as f:
            json.dump(final_metrics, f, indent=4)
            
        logger.info(f"✅ Test results saved to: {result_path}")
