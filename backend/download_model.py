from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "Qwen/Qwen2.5-0.5B-Instruct"

print(f"🚀 Starting download for {model_name}...")
print("This may take a while depending on your internet connection.")

try:
    print("Downloading Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    print("Downloading Model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )
    print("✅ Download complete! You can now start the server.")
except Exception as e:
    print(f"❌ Error downloading model: {e}")
