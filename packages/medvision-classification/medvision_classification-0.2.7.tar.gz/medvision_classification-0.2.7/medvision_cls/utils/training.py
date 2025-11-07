"""
Training module for MedVision Classification
"""

import os
import json
import torch
import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger, WandbLogger
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint, LearningRateMonitor
from pathlib import Path
from typing import Dict, Any, Optional
from pytorch_lightning.utilities import rank_zero_only
import logging

from .helpers import setup_logging, load_config, create_output_dirs

# @rank_zero_only
def _save_results_and_export_onnx(
    trainer: pl.Trainer,
    model: pl.LightningModule,
    data_module: pl.LightningDataModule,
    config: Dict[str, Any],
    callbacks: list,
    logger: logging.Logger
) -> None:
    """Save training results and export to ONNX (rank-zero only)"""
    # Save training results
    train_results = trainer.logged_metrics
    test_results = trainer.test(model, data_module, ckpt_path="best")

    save_metrics = config["training"].get("save_metrics", True)
    final_metrics = {}

    if save_metrics:
        # Extract best checkpoint callback
        best_ckpt_cb = None
        for cb in callbacks:
            if isinstance(cb, ModelCheckpoint):
                best_ckpt_cb = cb
                break

        # Extract train/val/test metrics
        train_val_metrics = {
            k: float(v) for k, v in train_results.items()
            if isinstance(v, torch.Tensor) and (k.startswith("val/") or k.startswith("train/"))
        }

        test_metrics = {
            k: float(v) for k, v in test_results[0].items()
        } if test_results else {}

        # Summarize results
        final_metrics = {
            "train_val_metrics": train_val_metrics,
            "test_metrics": test_metrics,
            "best_model_path": best_ckpt_cb.best_model_path if best_ckpt_cb else None,
            "best_model_score": float(best_ckpt_cb.best_model_score) if best_ckpt_cb and best_ckpt_cb.best_model_score is not None else None,
            "monitor": config.get("training", {}).get("model_checkpoint", {}).get("monitor", "val/accuracy"),
        }

    # ONNX Export after training - convert all saved top-k models
    onnx_config = config.get("onnx", {})
    convert_to_onnx = onnx_config.get("export_onnx", True)
    converted_models = []
    onnx_dir = None

    if convert_to_onnx:
        try:
            from .onnx_export import convert_models_to_onnx
            from ..models.lightning_module import ClassificationLightningModule

            if best_ckpt_cb:
                # Convert all saved models
                converted_models, onnx_dir = convert_models_to_onnx(
                    checkpoint_callback=best_ckpt_cb,
                    model_class=ClassificationLightningModule,
                    config=config,
                    datamodule=data_module
                )

                if converted_models:
                    logger.info(f"ONNX conversion completed: {len(converted_models)} models saved to {onnx_dir}")
                else:
                    logger.warning("ONNX conversion failed: no models converted")
            else:
                logger.warning("ONNX conversion skipped: no checkpoint callback found")

        except Exception as e:
            logger.error(f"ONNX conversion failed: {e}")    # Summarize and save final results
    if save_metrics:
        # Add ONNX conversion info
        if convert_to_onnx and converted_models:
            final_metrics["onnx_conversion"] = {
                "converted_count": len(converted_models),
                "onnx_directory": onnx_dir,
                "models": converted_models
            }

        # Save JSON file
        result_path = os.path.join(config.get("training", {}).get("output_dir", "outputs"), "results.json")
        os.makedirs(os.path.dirname(result_path), exist_ok=True)
        with open(result_path, "w") as f:
            json.dump(final_metrics, f, indent=4)

        logger.info(f"Training results saved to: {result_path}")

        # Merge dataset_statistics.json into outputs/results.json
        dataset_stats_path = os.path.join(config.get("data", {}).get("data_dir", ""), "dataset_statistics.json")

        if os.path.exists(dataset_stats_path):
            with open(dataset_stats_path, "r") as f:
                dataset_stats = json.load(f)

            final_metrics["dataset_statistics"] = dataset_stats

            with open(result_path, "w") as f:
                json.dump(final_metrics, f, indent=4)


def validate_config(config: Dict[str, Any]) -> None:
    """Validate training configuration"""
    required_keys = ["model", "data", "training"]
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")
    
    # Validate model config
    model_config = config["model"]
    if "num_classes" not in model_config:
        raise ValueError("model.num_classes is required")
    
    # Validate data config
    data_config = config["data"]
    if "data_dir" not in data_config:
        raise ValueError("data.data_dir is required")
    
    # Validate training config
    training_config = config["training"]
    if "max_epochs" not in training_config:
        raise ValueError("training.max_epochs is required")
    
    # Check task_dim
    task_dim = config.get("task_dim", "")
    if task_dim not in ["2d", "3d"]:
        raise ValueError("task_dim must be either '2d' or '3d'")


def setup_callbacks(config: Dict[str, Any]) -> list:
    """Setup training callbacks"""
    callbacks = []
    
    # Get callbacks from training config
    training_config = config.get("training", {})
    
    # Early stopping
    if "early_stopping" in training_config:
        es_config = training_config["early_stopping"]
        callbacks.append(EarlyStopping(
            monitor=es_config.get("monitor", "val/val_loss"),
            patience=es_config.get("patience", 10),
            mode=es_config.get("mode", "min"),
            verbose=True
        ))
    
    if "model_checkpoint" in training_config:
        mc_config = training_config["model_checkpoint"]
        
        output_dir = config.get("training", {}).get("output_dir", "outputs")
        checkpoint_dir = os.path.join(output_dir, "checkpoints")
        monitor_metric = mc_config.get("monitor", "val/accuracy")

        callbacks.append(ModelCheckpoint(
            dirpath=checkpoint_dir,
            monitor=monitor_metric,
            mode=mc_config.get("mode", "max"),
            save_top_k=mc_config.get("save_top_k", 1),
            filename=f"{config['training'].get('experiment_name')}",
            verbose=True
        ))   
    
    callbacks.append(LearningRateMonitor(logging_interval="epoch"))
    
    return callbacks

def train_model(
    config_file: str,
    resume_checkpoint: Optional[str] = None,
    debug: bool = False
):
    """
    Train a classification model
    
    Args:
        config_file: Path to configuration file
        resume_checkpoint: Path to checkpoint to resume from
        debug: Enable debug mode
    """
    # Import here to avoid circular imports
    from ..models import ClassificationLightningModule
    from ..datasets import get_datamodule
    
    # Load configuration
    config = load_config(config_file)
    
    # Validate configuration
    validate_config(config)
    
    # Setup logging
    setup_logging(debug=debug)
    logger = logging.getLogger(__name__)
    
    # Set seed
    pl.seed_everything(config.get("seed", 42))
    
    # Create output directories
    create_output_dirs(config.get("outputs", {}))
    
    # Setup data module
    data_config = config.get("data", {})
    data_module = get_datamodule(data_config)
    
    # Setup model
    model_config = config.get("model", {})

    model = ClassificationLightningModule(
        model_config=model_config,
        loss_config=model_config.get("loss", {}),
        optimizer_config=model_config.get("optimizer", {}),
        scheduler_config=model_config.get("scheduler", {}),
        metrics_config=model_config.get("metrics", {})
    )
    
    # Setup callbacks
    callbacks = setup_callbacks(config)
    
    # Setup logger
    tb_logger = TensorBoardLogger(
        save_dir=config.get("logging", {}).get("output_dir", "outputs/logs"),
        name="medvision_cls",
        version=config["training"].get("version", None),
    )
    
    # Setup trainer
    training_config = config.get("training", {})

    # Setup export onnx
    onnx_config = config.get("onnx", {})
    
    # Check if model is 3D to determine deterministic setting
    task_dim = config.get("task_dim", "")

    if task_dim == "":
        return "Error: task_dim is not set in the config file."


    trainer = pl.Trainer(
        max_epochs=training_config.get("max_epochs", 100),
        accelerator=training_config.get("accelerator", "gpu"),
        devices=training_config.get("devices", -1),
        precision=training_config.get("precision", 16),
        log_every_n_steps=config.get("logging", {}).get("log_every_n_steps", 10),
        check_val_every_n_epoch=training_config.get("check_val_every_n_epoch", 1),
        gradient_clip_val=training_config.get("gradient_clip_val", 1.0),
        callbacks=callbacks,
        logger=tb_logger,
        enable_progress_bar=True
    )
    
    # Start training
    trainer.fit(model, data_module)

    # Save results and export ONNX (only on rank 0)
    _save_results_and_export_onnx(trainer, model, data_module, config, callbacks, logger)

    return trainer, model






