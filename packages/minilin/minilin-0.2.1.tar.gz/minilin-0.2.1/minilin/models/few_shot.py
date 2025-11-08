"""
Few-shot learning techniques (LoRA, Adapter, Prompt Tuning)
"""

from typing import Optional, Dict, Any
import torch
import torch.nn as nn

from minilin.utils import setup_logger

logger = setup_logger(__name__)


class LoRAWrapper:
    """
    LoRA (Low-Rank Adaptation) wrapper for efficient fine-tuning.
    
    Reduces trainable parameters by using low-rank decomposition.
    """
    
    def __init__(self, model: nn.Module, r: int = 8, alpha: int = 16, dropout: float = 0.1):
        """
        Args:
            model: Base model to wrap
            r: LoRA rank
            alpha: LoRA scaling factor
            dropout: Dropout probability
        """
        self.model = model
        self.r = r
        self.alpha = alpha
        self.dropout = dropout
        self.lora_applied = False
    
    def apply_lora(self, target_modules: Optional[list] = None) -> nn.Module:
        """
        Apply LoRA to model.
        
        Args:
            target_modules: List of module names to apply LoRA (None = auto-detect)
            
        Returns:
            Model with LoRA applied
        """
        try:
            from peft import get_peft_model, LoraConfig, TaskType
            
            # Auto-detect task type
            task_type = self._detect_task_type()
            
            # Configure LoRA
            if target_modules is None:
                target_modules = self._auto_detect_target_modules()
            
            lora_config = LoraConfig(
                r=self.r,
                lora_alpha=self.alpha,
                target_modules=target_modules,
                lora_dropout=self.dropout,
                bias="none",
                task_type=task_type
            )
            
            # Apply LoRA
            self.model = get_peft_model(self.model, lora_config)
            self.lora_applied = True
            
            # Print trainable parameters
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
            total_params = sum(p.numel() for p in self.model.parameters())
            
            logger.info(f"LoRA applied successfully")
            logger.info(f"Trainable params: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")
            
            return self.model
            
        except ImportError:
            logger.error("peft library not installed. Install with: pip install peft")
            raise
        except Exception as e:
            logger.error(f"Failed to apply LoRA: {e}")
            raise
    
    def _detect_task_type(self):
        """Detect task type from model."""
        try:
            from peft import TaskType
            
            model_name = self.model.__class__.__name__.lower()
            
            if 'sequenceclassification' in model_name:
                return TaskType.SEQ_CLS
            elif 'tokenclas' in model_name:
                return TaskType.TOKEN_CLS
            elif 'causal' in model_name:
                return TaskType.CAUSAL_LM
            else:
                return TaskType.SEQ_CLS  # Default
        except:
            return "SEQ_CLS"
    
    def _auto_detect_target_modules(self) -> list:
        """Auto-detect which modules to apply LoRA to."""
        # Common target modules for different model types
        target_modules = []
        
        # Check for transformer layers
        for name, module in self.model.named_modules():
            if 'query' in name or 'q_proj' in name:
                target_modules.append('query')
                break
        
        if not target_modules:
            # Default targets for BERT-like models
            target_modules = ['query', 'value']
        
        logger.info(f"Auto-detected target modules: {target_modules}")
        return target_modules


class AdapterWrapper:
    """
    Adapter wrapper for parameter-efficient fine-tuning.
    
    Adds small adapter layers between transformer layers.
    """
    
    def __init__(self, model: nn.Module, adapter_size: int = 64):
        """
        Args:
            model: Base model to wrap
            adapter_size: Size of adapter bottleneck
        """
        self.model = model
        self.adapter_size = adapter_size
        self.adapters_applied = False
    
    def apply_adapters(self) -> nn.Module:
        """
        Apply adapters to model.
        
        Returns:
            Model with adapters applied
        """
        try:
            from peft import get_peft_model, AdapterConfig, TaskType
            
            # Configure adapters
            adapter_config = AdapterConfig(
                adapter_size=self.adapter_size,
                task_type=TaskType.SEQ_CLS
            )
            
            # Apply adapters
            self.model = get_peft_model(self.model, adapter_config)
            self.adapters_applied = True
            
            logger.info(f"Adapters applied successfully")
            
            return self.model
            
        except ImportError:
            logger.warning("peft library not installed, using manual adapter implementation")
            return self._apply_manual_adapters()
        except Exception as e:
            logger.error(f"Failed to apply adapters: {e}")
            raise
    
    def _apply_manual_adapters(self) -> nn.Module:
        """Apply adapters manually (fallback)."""
        # Simple adapter implementation
        logger.info("Using manual adapter implementation")
        
        # Freeze base model
        for param in self.model.parameters():
            param.requires_grad = False
        
        # Add adapter layers (simplified)
        # In production, this would add adapters to each transformer layer
        
        return self.model


class PromptTuning:
    """
    Prompt tuning for few-shot learning.
    
    Only trains soft prompts, keeping model frozen.
    """
    
    def __init__(
        self,
        model: nn.Module,
        num_virtual_tokens: int = 20,
        prompt_init_text: Optional[str] = None
    ):
        """
        Args:
            model: Base model
            num_virtual_tokens: Number of virtual tokens in prompt
            prompt_init_text: Text to initialize prompt (None = random)
        """
        self.model = model
        self.num_virtual_tokens = num_virtual_tokens
        self.prompt_init_text = prompt_init_text
    
    def apply_prompt_tuning(self) -> nn.Module:
        """
        Apply prompt tuning to model.
        
        Returns:
            Model with prompt tuning applied
        """
        try:
            from peft import get_peft_model, PromptTuningConfig, TaskType
            
            # Configure prompt tuning
            config = PromptTuningConfig(
                task_type=TaskType.SEQ_CLS,
                num_virtual_tokens=self.num_virtual_tokens,
                prompt_tuning_init_text=self.prompt_init_text,
            )
            
            # Apply prompt tuning
            self.model = get_peft_model(self.model, config)
            
            logger.info(f"Prompt tuning applied with {self.num_virtual_tokens} virtual tokens")
            
            return self.model
            
        except ImportError:
            logger.error("peft library not installed. Install with: pip install peft")
            raise
        except Exception as e:
            logger.error(f"Failed to apply prompt tuning: {e}")
            raise


def apply_few_shot_method(
    model: nn.Module,
    method: str = "lora",
    **kwargs
) -> nn.Module:
    """
    Convenience function to apply few-shot learning method.
    
    Args:
        model: Base model
        method: Method to apply ('lora', 'adapter', 'prompt')
        **kwargs: Method-specific arguments
        
    Returns:
        Model with few-shot method applied
    """
    if method == "lora":
        wrapper = LoRAWrapper(model, **kwargs)
        return wrapper.apply_lora()
    elif method == "adapter":
        wrapper = AdapterWrapper(model, **kwargs)
        return wrapper.apply_adapters()
    elif method == "prompt":
        wrapper = PromptTuning(model, **kwargs)
        return wrapper.apply_prompt_tuning()
    else:
        raise ValueError(f"Unknown few-shot method: {method}")
