# SIMPLE FIX - Replace Cell 3 (Model Loading)

from unsloth import FastLanguageModel
from transformers import AutoTokenizer
import torch

max_seq_length = 2048
dtype = None
load_in_4bit = True

# Load model with FastLanguageModel
model, _ = FastLanguageModel.from_pretrained(
    model_name = "unsloth/gemma-3n-E4B-it",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# Use regular Gemma tokenizer (not Gemma3N)
tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")

print("✅ Model and tokenizer loaded")