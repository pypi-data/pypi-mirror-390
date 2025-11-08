"""
Knowledge distillation for model compression
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple
from tqdm import tqdm

from minilin.utils import setup_logger

logger = setup_logger(__name__)


class DistillationLoss(nn.Module):
    """
    Combined loss for knowledge distillation.
    
    Combines:
    - Hard loss (cross-entropy with true labels)
    - Soft loss (KL divergence with teacher predictions)
    """
    
    def __init__(
        self,
        temperature: float = 3.0,
        alpha: float = 0.5
    ):
        """
        Args:
            temperature: Temperature for softening probabilities
            alpha: Weight for soft loss (1-alpha for hard loss)
        """
        super().__init__()
        self.temperature = temperature
        self.alpha = alpha
        self.ce_loss = nn.CrossEntropyLoss()
    
    def forward(
        self,
        student_logits: torch.Tensor,
        teacher_logits: torch.Tensor,
        labels: torch.Tensor
    ) -> Tuple[torch.Tensor, dict]:
        """
        Calculate distillation loss.
        
        Args:
            student_logits: Student model predictions
            teacher_logits: Teacher model predictions
            labels: True labels
            
        Returns:
            Total loss and loss components dict
        """
        # Hard loss (student vs true labels)
        hard_loss = self.ce_loss(student_logits, labels)
        
        # Soft loss (student vs teacher)
        soft_student = F.log_softmax(student_logits / self.temperature, dim=-1)
        soft_teacher = F.softmax(teacher_logits / self.temperature, dim=-1)
        soft_loss = F.kl_div(soft_student, soft_teacher, reduction='batchmean')
        soft_loss = soft_loss * (self.temperature ** 2)
        
        # Combined loss
        total_loss = self.alpha * soft_loss + (1 - self.alpha) * hard_loss
        
        loss_dict = {
            'total': total_loss.item(),
            'hard': hard_loss.item(),
            'soft': soft_loss.item()
        }
        
        return total_loss, loss_dict


class KnowledgeDistiller:
    """
    Knowledge distillation trainer.
    
    Trains a small student model to mimic a large teacher model.
    """
    
    def __init__(
        self,
        teacher_model: nn.Module,
        student_model: nn.Module,
        temperature: float = 3.0,
        alpha: float = 0.5,
        device: Optional[torch.device] = None
    ):
        """
        Args:
            teacher_model: Pre-trained teacher model
            student_model: Student model to train
            temperature: Distillation temperature
            alpha: Weight for soft loss
            device: Device to use
        """
        self.teacher = teacher_model
        self.student = student_model
        self.temperature = temperature
        self.alpha = alpha
        
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
        
        # Move models to device
        self.teacher.to(self.device)
        self.student.to(self.device)
        
        # Freeze teacher
        self.teacher.eval()
        for param in self.teacher.parameters():
            param.requires_grad = False
        
        # Loss function
        self.criterion = DistillationLoss(temperature, alpha)
        
        logger.info(f"Knowledge distiller initialized on {self.device}")
        logger.info(f"Temperature: {temperature}, Alpha: {alpha}")
    
    def distill(
        self,
        train_loader,
        val_loader,
        epochs: int = 5,
        learning_rate: float = 2e-5,
        save_path: Optional[str] = None
    ) -> dict:
        """
        Perform knowledge distillation.
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Number of epochs
            learning_rate: Learning rate
            save_path: Path to save best model
            
        Returns:
            Training metrics
        """
        optimizer = torch.optim.AdamW(self.student.parameters(), lr=learning_rate)
        
        best_val_loss = float('inf')
        metrics = {
            'train_losses': [],
            'val_losses': [],
            'train_hard_losses': [],
            'train_soft_losses': []
        }
        
        for epoch in range(epochs):
            logger.info(f"Epoch {epoch + 1}/{epochs}")
            
            # Train
            train_metrics = self._train_epoch(train_loader, optimizer)
            metrics['train_losses'].append(train_metrics['total'])
            metrics['train_hard_losses'].append(train_metrics['hard'])
            metrics['train_soft_losses'].append(train_metrics['soft'])
            
            # Validate
            val_loss = self._validate_epoch(val_loader)
            metrics['val_losses'].append(val_loss)
            
            logger.info(
                f"Train Loss: {train_metrics['total']:.4f} "
                f"(Hard: {train_metrics['hard']:.4f}, Soft: {train_metrics['soft']:.4f}), "
                f"Val Loss: {val_loss:.4f}"
            )
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                if save_path:
                    torch.save(self.student.state_dict(), save_path)
                    logger.info(f"Saved best model to {save_path}")
        
        metrics['best_val_loss'] = best_val_loss
        logger.info("Distillation complete!")
        
        return metrics
    
    def _train_epoch(self, train_loader, optimizer) -> dict:
        """Train for one epoch."""
        self.student.train()
        
        total_loss = 0
        total_hard = 0
        total_soft = 0
        num_batches = 0
        
        for batch in tqdm(train_loader, desc="Distilling"):
            # Move batch to device
            batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                    for k, v in batch.items()}
            
            # Get teacher predictions (no gradient)
            with torch.no_grad():
                teacher_outputs = self.teacher(**batch)
                teacher_logits = teacher_outputs.logits
            
            # Get student predictions
            student_outputs = self.student(**batch)
            student_logits = student_outputs.logits
            
            # Calculate distillation loss
            loss, loss_dict = self.criterion(
                student_logits,
                teacher_logits,
                batch['labels']
            )
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss_dict['total']
            total_hard += loss_dict['hard']
            total_soft += loss_dict['soft']
            num_batches += 1
        
        return {
            'total': total_loss / num_batches,
            'hard': total_hard / num_batches,
            'soft': total_soft / num_batches
        }
    
    def _validate_epoch(self, val_loader) -> float:
        """Validate for one epoch."""
        self.student.eval()
        total_loss = 0
        num_batches = 0
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Validating"):
                batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                        for k, v in batch.items()}
                
                # Get predictions
                teacher_outputs = self.teacher(**batch)
                student_outputs = self.student(**batch)
                
                # Calculate loss
                loss, _ = self.criterion(
                    student_outputs.logits,
                    teacher_outputs.logits,
                    batch['labels']
                )
                
                total_loss += loss.item()
                num_batches += 1
        
        return total_loss / num_batches
    
    def get_compression_ratio(self) -> dict:
        """Calculate compression ratio."""
        teacher_params = sum(p.numel() for p in self.teacher.parameters())
        student_params = sum(p.numel() for p in self.student.parameters())
        
        return {
            'teacher_params': teacher_params,
            'student_params': student_params,
            'compression_ratio': teacher_params / student_params,
            'size_reduction': 1 - (student_params / teacher_params)
        }


def distill_model(
    teacher_model: nn.Module,
    student_model: nn.Module,
    train_loader,
    val_loader,
    **kwargs
) -> Tuple[nn.Module, dict]:
    """
    Convenience function for knowledge distillation.
    
    Args:
        teacher_model: Teacher model
        student_model: Student model
        train_loader: Training data
        val_loader: Validation data
        **kwargs: Additional arguments for distiller
        
    Returns:
        Trained student model and metrics
    """
    distiller = KnowledgeDistiller(teacher_model, student_model, **kwargs)
    metrics = distiller.distill(train_loader, val_loader, **kwargs)
    
    compression_info = distiller.get_compression_ratio()
    logger.info(f"Compression ratio: {compression_info['compression_ratio']:.2f}x")
    logger.info(f"Size reduction: {compression_info['size_reduction']:.1%}")
    
    return student_model, metrics
