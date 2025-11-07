"""
Datasets module for MedVision Classification.
"""

import os
import json
import torch
from typing import Dict, Any, Optional, List, Tuple, Union
import pytorch_lightning as pl
from torch.utils.data import Dataset, DataLoader, random_split
from collections import Counter
import torch.distributed as dist

from .medical_dataset import MedicalImageDataset


def get_datamodule(config: Dict[str, Any]) -> pl.LightningDataModule:
    """
    Factory function to create a datamodule based on configuration.
    
    Args:
        config: Dataset configuration dictionary
        
    Returns:
        A LightningDataModule implementation
    """
    dataset_type = config["type"].lower()
    
    if dataset_type == "medical":
        datamodule_class = MedicalDataModule
    elif dataset_type == "custom":
        # Add your custom datamodule implementation here
        raise NotImplementedError(f"Custom dataset type not implemented")
    else:
        raise ValueError(f"Unknown dataset type: {dataset_type}")
    
    return datamodule_class(config)


class MedicalDataModule(pl.LightningDataModule):
    """
    Base DataModule for medical image classification datasets.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the medical data module.
        
        Args:
            config: Dataset configuration
        """
        super().__init__()
        self.config = config
        self.batch_size = config.get("batch_size", 16)
        self.num_workers = config.get("num_workers", min(4, os.cpu_count() or 4))
        self.pin_memory = config.get("pin_memory", True)
        self.data_dir = config.get("data_dir", "./data")
        # self.train_val_split = config.get("train_val_split", [0.8, 0.2])
        self.seed = config.get("seed", 42)
        self.train_transforms = None
        self.val_transforms = None
        self.test_transforms = None
        
        # Initialize datasets
        self.train_dataset = None
        self.val_dataset = None
        self.test_dataset = None
        
        # Class information
        self.num_classes = None
        self.class_names = None
        
    def prepare_data(self):
        """
        Download and prepare data if needed.
        """
        # This method is called once and on only one GPU
        pass
        
    def setup(self, stage: Optional[str] = None):
        """
        Setup datasets based on stage.
        
        Args:
            stage: Current stage (fit, validate, test, predict)
        """
        # Setup transforms
        from ..transforms import get_transforms
        
        # Use new config structure if available, fallback to old structure
        if "train_transforms" in self.config:
            # New structure with explicit transform configs
            self.train_transforms = get_transforms(self.config.get("train_transforms", {}))
            self.val_transforms = get_transforms(self.config.get("val_transforms", {}))
            self.test_transforms = get_transforms(self.config.get("test_transforms", {}))
        else:
            # Fallback: generate transforms from general config
            from ..transforms import get_train_transforms, get_val_transforms
            transforms_config = self.config.get("transforms", {})
            
            self.train_transforms = get_train_transforms(
                image_size=tuple(transforms_config.get("image_size", [224, 224])),
                normalize=transforms_config.get("normalize", True),
                augment=transforms_config.get("augment", True)
            )
            self.val_transforms = get_val_transforms(
                image_size=tuple(transforms_config.get("image_size", [224, 224])),
                normalize=transforms_config.get("normalize", True)
            )
            self.test_transforms = self.val_transforms
        
        # Create datasets based on stage
        if stage == "fit":
            # Only create train and validation datasets for training
            self._setup_train_val_datasets()
            
        elif stage == "test":
            # Only create test dataset for testing
            self._setup_test_dataset()
            # Generate statistics if train/val datasets are also available
            self._generate_dataset_statistics_if_needed()
            
        elif stage == "validate":
            # Only create validation dataset for standalone validation
            self._setup_val_dataset()
            
        elif stage == "predict":
            # For prediction, use test dataset
            self._setup_test_dataset()
            
        elif stage is None:
            # If no stage specified, setup all datasets (for compatibility)
            self._setup_train_val_datasets()
            self._setup_test_dataset()
        
        # Generate dataset statistics after all relevant datasets are created
        self._generate_dataset_statistics_if_needed()
    
    def _setup_train_val_datasets(self):
        """Setup training and validation datasets"""
        # Get image format from config
        image_format = self.config.get("image_format", "*.png")
        
        # Create separate training and validation datasets
        self.train_dataset = MedicalImageDataset(
            data_dir=self.data_dir,
            mode="train",
            transform=self.train_transforms,
            image_format=image_format
        )
        
        self.val_dataset = MedicalImageDataset(
            data_dir=self.data_dir,
            mode="val",
            transform=self.val_transforms,
            image_format=image_format
        )
        
        # Get class information
        self.num_classes = self.train_dataset.num_classes
        self.class_names = self.train_dataset.class_names
    
    def _setup_val_dataset(self):
        """Setup validation dataset only"""
        # Get image format from config
        image_format = self.config.get("image_format", "*.png")
        
        self.val_dataset = MedicalImageDataset(
            data_dir=self.data_dir,
            mode="val",
            transform=self.val_transforms,
            image_format=image_format
        )
        
        # Get class information
        self.num_classes = self.val_dataset.num_classes
        self.class_names = self.val_dataset.class_names
    
    def _setup_test_dataset(self):
        """Setup test dataset"""
        # Get image format from config
        image_format = self.config.get("image_format", "*.png")
        
        self.test_dataset = MedicalImageDataset(
            data_dir=self.data_dir,
            mode="test",
            transform=self.test_transforms,
            image_format=image_format
        )
        
        # Get class information if not already set
        if self.num_classes is None:
            self.num_classes = self.test_dataset.num_classes
            self.class_names = self.test_dataset.class_names
    
    def _generate_dataset_statistics_if_needed(self):
        """Generate dataset statistics if all relevant datasets are available"""
        # Only generate statistics if we have at least training and validation datasets
        # Test dataset is optional
        if self.train_dataset is not None and self.val_dataset is not None:
            self._generate_dataset_statistics()
    
    def _generate_dataset_statistics(self):
        """Generate and save dataset statistics JSON file"""
        # Only generate statistics on the main process (rank 0) to avoid conflicts in multi-GPU setup
        if dist.is_initialized() and dist.get_rank() != 0:
            return
            
        stats_file = os.path.join(self.data_dir, "dataset_statistics.json")
        
        # Check if statistics file already exists
        if os.path.exists(stats_file):
            print(f"Dataset statistics file already exists: {stats_file}")
            return
        
        print("Generating dataset statistics...")
        
        # Collect statistics for each split
        statistics = {
            "data_dir": self.data_dir,
            "num_classes": self.num_classes,
            "class_names": self.class_names,
            "splits": {}
        }
        
        # Training set statistics
        if self.train_dataset is not None:
            train_stats = self._get_dataset_class_distribution(self.train_dataset)
            statistics["splits"]["train"] = train_stats
        
        # Validation set statistics
        if self.val_dataset is not None:
            val_stats = self._get_dataset_class_distribution(self.val_dataset)
            statistics["splits"]["val"] = val_stats
        
        # Test set statistics
        if self.test_dataset is not None:
            test_stats = self._get_dataset_class_distribution(self.test_dataset)
            statistics["splits"]["test"] = test_stats
        
        # Save to JSON file
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(statistics, f, indent=2, ensure_ascii=False)
            print(f"Dataset statistics saved to: {stats_file}")
        except Exception as e:
            print(f"Failed to save dataset statistics: {e}")
    
    def _get_dataset_class_distribution(self, dataset: MedicalImageDataset) -> Dict[str, Any]:
        """Get class distribution statistics for a dataset"""
        # Count samples per class
        class_counts = Counter()
        total_samples = len(dataset)
        
        # Iterate through dataset to count classes
        for i in range(total_samples):
            sample = dataset[i]  # Get sample dictionary
            label = sample["label"]  # Extract label from dictionary
            if isinstance(label, torch.Tensor):
                label = label.item()
            class_counts[label] += 1
        
        # Convert to class name mapping
        class_distribution = {}
        for class_idx, count in class_counts.items():
            class_name = self.class_names[class_idx] if self.class_names and class_idx < len(self.class_names) else f"class_{class_idx}"
            class_distribution[class_name] = {
                "count": count,
                "percentage": round(count / total_samples * 100, 2)
            }
        
        return {
            "total_samples": total_samples,
            "class_distribution": class_distribution,
            "class_counts": dict(class_counts)
        }
            
    def train_dataloader(self):
        """
        Create training dataloader.
        
        Returns:
            Training dataloader
        """
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
            drop_last=True,
        )
    
    def val_dataloader(self):
        """
        Create validation dataloader.
        
        Returns:
            Validation dataloader
        """
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
        )
    
    def test_dataloader(self):
        """
        Create test dataloader.
        
        Returns:
            Test dataloader
        """
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
        )


# Legacy compatibility classes
class MedicalImageDataModule(MedicalDataModule):
    """Legacy alias for MedicalDataModule"""
    
    def __init__(
        self,
        data_dir: str,
        batch_size: int = 16,
        num_workers: int = 4,
        image_size: Tuple[int, int] = (224, 224),
        train_val_test_split: List[float] = [0.7, 0.2, 0.1],
        normalize: bool = True,
        augment: bool = True,
        seed: int = 42,
        **kwargs
    ):
        # Convert legacy parameters to new config format
        config = {
            "type": "medical",
            "data_dir": data_dir,
            "batch_size": batch_size,
            "num_workers": num_workers,
            "pin_memory": True,
            "train_val_split": train_val_test_split[:2],  # Only use train/val split
            "seed": seed,
            "transforms": {
                "image_size": image_size,
                "normalize": normalize,
                "augment": augment,
            }
        }
        super().__init__(config)
