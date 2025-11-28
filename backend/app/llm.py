import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread

class LLMService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.tokenizer = None
        return cls._instance

    def load_model(self):
        if self.model is not None:
            print("⚡ Using cached model")
            return

        print("🚀 Loading Qwen2.5-0.5B-Instruct...")
        # Optimize for CPU
        torch.set_num_threads(8)
        
        model_name = "Qwen/Qwen2.5-0.5B-Instruct"
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            device_map="cpu"
        )
        self.model.eval() # Ensure model is in eval mode
        print("✅ Model loaded successfully!")

    def generate_stream(self, query, context_results):
        if self.model is None:
            self.load_model()

        # Prepare context from search results
        context_text = "\n".join([f"[{i+1}] {r['title']}: {r['snippet']}" for i, r in enumerate(context_results)])
        
        prompt = f"""You are Perceive AI, a helpful search assistant. 
Answer the user's query based ONLY on the provided search results. 
Cite sources using [1], [2], etc.
Keep the answer concise (under 150 words).

Search Results:
{context_text}

User Query: {query}
Answer:"""

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        generation_kwargs = dict(model_inputs, streamer=streamer, max_new_tokens=512)
        
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        for new_text in streamer:
            yield new_text
