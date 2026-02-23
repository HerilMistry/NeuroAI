"""
MedGemma integration for NeuroDegenRx.

This module provides local inference for MedGemma models (e.g., MedGemma-2B, MedGemma-7B) to enable advanced biomedical text analysis.

Example use case: Drug mechanism summarization, literature evidence extraction, or pathway annotation.
"""
import os
from typing import List, Optional


try:
    from vllm import LLM, SamplingParams
except ImportError:
    raise ImportError("Please install vllm for MedGemma integration.")

# Default model name (can be changed to MedGemma-2B, MedGemma-7B, etc.)
MEDGEMMA_MODEL_NAME = os.environ.get("MEDGEMMA_MODEL_NAME", "medgemma/medgemma-2b")

class MedGemmaInference:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or MEDGEMMA_MODEL_NAME
        self.llm = LLM(model=self.model_name)

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        sampling_params = SamplingParams(max_tokens=max_tokens)
        outputs = self.llm.generate([prompt], sampling_params)
        return outputs[0].outputs[0].text.strip()

# Example utility: Summarize drug mechanism using MedGemma

def summarize_drug_mechanism(drug_name: str, description: str) -> str:
    """
    Use MedGemma to generate a concise mechanism summary for a drug.
    """
    prompt = f"Summarize the mechanism of action for the drug '{drug_name}': {description}"
    medgemma = MedGemmaInference()
    return medgemma.generate(prompt, max_tokens=256)
