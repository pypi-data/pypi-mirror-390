"""Model pruning"""

import torch
import torch.nn as nn
import torch.nn.utils.prune as prune

from minilin.utils import setup_logger

logger = setup_logger(__name__)


class Pruner:
    """
    Model pruning to reduce parameters.
    """
    
    def __init__(self):
        pass
    
    def prune(
        self,
        model: nn.Module,
        amount: float = 0.3,
        method: str = "l1_unstructured"
    ) -> nn.Module:
        """
        Prune model parameters.
        
        Args:
            model: Model to prune
            amount: Fraction of parameters to prune (0-1)
            method: Pruning method ('l1_unstructured', 'random_unstructured')
            
        Returns:
            Pruned model
        """
        logger.info(f"Pruning model with amount: {amount}, method: {method}")
        
        try:
            # Apply pruning to all Conv2d and Linear layers
            for name, module in model.named_modules():
                if isinstance(module, (nn.Conv2d, nn.Linear)):
                    if method == "l1_unstructured":
                        prune.l1_unstructured(module, name='weight', amount=amount)
                    elif method == "random_unstructured":
                        prune.random_unstructured(module, name='weight', amount=amount)
                    
                    # Make pruning permanent
                    prune.remove(module, 'weight')
            
            logger.info("Pruning successful")
            return model
            
        except Exception as e:
            logger.warning(f"Pruning failed: {e}, returning original model")
            return model
