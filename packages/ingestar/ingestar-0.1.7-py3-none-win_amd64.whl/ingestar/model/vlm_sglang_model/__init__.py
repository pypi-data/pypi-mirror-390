from sglang.srt.configs.model_config import multimodal_model_archs
from sglang.srt.models.registry import ModelRegistry

from sglang.srt.managers.multimodal_processor import (
    PROCESSOR_MAPPING as PROCESSOR_MAPPING,
)

from .. import vlm_hf_model as _
from .image_processor import Ingestar2ImageProcessor
from .model import Ingestar2QwenForCausalLM

ModelRegistry.models[Ingestar2QwenForCausalLM.__name__] = Ingestar2QwenForCausalLM
PROCESSOR_MAPPING[Ingestar2QwenForCausalLM] = Ingestar2ImageProcessor
multimodal_model_archs.append(Ingestar2QwenForCausalLM.__name__)
