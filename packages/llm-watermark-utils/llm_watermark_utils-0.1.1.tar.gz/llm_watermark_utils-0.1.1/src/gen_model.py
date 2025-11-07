import time
import torch
from google import genai
from transformers import AutoModelForCausalLM, AutoTokenizer, LogitsProcessor
import os, json, re
from tqdm import tqdm
from loguru import logger
from functools import partial

def export_openai_key():
    """Export OpenAI API key from config.json to environment variable.
    make sure to have a config.json file with the following structure:
    """
    with open("config.json", "r") as f:
        config = json.load(f)
        os.environ["OPENAI_API_KEY"] = config.get("openai", {}).get("api_key", "")
        assert os.environ["OPENAI_API_KEY"], "OpenAI API key is not set in config.json"
        
def build_prompt(question, retrieved_docs: list[str]) -> str:
    """Build a prompt for RAG-style question answering."""
    prompt = "Here is the set of retrieved documents you will use to answer the question:\n<documents>"
    for doc in retrieved_docs:
        prompt += f"\n{doc}"
    prompt += f"</documents>\n Now, here is the question you need to answer: <question>\n{question}\n</question>"
    return prompt

class huggingface_model:
    def __init__(
        self,
        model_name,
        device="auto",
        watermark = None,
        loaded_model=True,
        login=True,
    ):
        self.model_name = model_name
        self.device = device

        if login:
            # Load the Hugging Face API key from config.json, llama 3 and 4 requires authentication
            import json
            if os.path.exists("config.json") is False:
                logger.info("config.json not found. Please create it with your Hugging Face API key.")
                with open("config.json", "w") as f:
                    json.dump({"huggingface": {"api_key": "YOUR_HUGGINGFACE_API_KEY"}}, f, indent=4)
            else:
                with open("config.json", "r") as f:
                    config = json.load(f)
                api_key = config.get("huggingface", {}).get("api_key")
                if api_key:
                    self._login_huggingface(api_key)

        if loaded_model:
            # Load the model and tokenizer from the Hugging Face Hub
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, dtype=torch.bfloat16)
            logger.info(f"Loaded tokenizer for {model_name} on {device}")
            self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map=device,torch_dtype="auto")
            
        # self.load_watermark(watermark, f"./watermark/{watermark}.json") if watermark else None
        self.watermark = watermark
        self.logit_processors = [watermark.logits_processor] if watermark else list()

    def load_watermark(self, watermark):
        self.watermark = watermark
        self.logit_processors.append(watermark.logits_processor)
    
    def _login_huggingface(self, api_key):
        from huggingface_hub import login
        login(token=api_key)

    def generate(
        self,
        messages,
        do_watermark=False,
        **generation_kwargs,
    ) -> str:
        if do_watermark and not self.logit_processors:
            raise ValueError("Logit processors must be provided for watermarking.")
        
        encoded_chat = self.tokenizer.apply_chat_template(
            messages, 
            return_tensors="pt", 
            add_generation_prompt=True, 
            return_dict=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **encoded_chat,
                **generation_kwargs,
                logits_processor=self.logit_processors if do_watermark else None,
            )
        generated = self.tokenizer.decode(outputs[0][encoded_chat["input_ids"].shape[-1]:]).strip()
        torch.cuda.empty_cache()
        return generated
    
    def inject_watermark_batch(self, doc_lst:list[str]) -> list[str]:
        logger.info(f"inject watermark to {len(doc_lst)} documents")
        wm_docs = list()
        for doc in tqdm(doc_lst):
            messages = [
                {"role": "system", "content": "You are a professional rewriter. Your task is to rewrite the user's input without changing its meaning and length. Do not add any additional information or context, just output the article you re-write."},
                {"role": "user", "content": f"re-write this article:{doc}"},
            ]
            res = self.generate(
                messages,
                do_watermark=True,  # Enable watermarking
                max_length=1024
            )
            wm_docs.append(res)
        return wm_docs

    def detect_watermark(self, text):
        assert self.watermark, "Watermarking is not enabled for this model."
        return self.watermark.detect_watermark(text, return_dict=True)
    

class gpt_oss(huggingface_model):
    def __init__(
        self,
        model_name = "openai/gpt-oss-20b",
        device="cuda",
        watermark = None,
        loaded_model=True,
        login=True,
    ):
        super().__init__(model_name, device, watermark, loaded_model, login)
    
    def extract_final_text(self, decoded: str) -> str:
        # For gpt-oss, it apply harmony chat template, extract final message from the response
        m = re.search(r"<\|start\|>assistant.*?<\|message\|>(.*?)<\|return\|>", decoded, re.S)
        return m.group(1).strip() if m else decoded.strip()

    def generate(
        self,
        messages,
        do_watermark=False,
        **generation_kwargs,
    ) -> str:
        generated = super().generate(messages, do_watermark, **generation_kwargs)
        return self.extract_final_text(generated)
    

class qwen3(huggingface_model):
    def __init__(
        self,
        model_name = "Qwen/Qwen3-8B",
        device="cuda",
        watermark = None,
        loaded_model=True,
        login=True,
        enable_thinking=False
    ):
        super().__init__(model_name, device, watermark, loaded_model, login)
        self.enable_thinking = enable_thinking
    
    def generate(
        self,
        messages,
        do_watermark=False,
        **generation_kwargs,
    ) -> str:
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=self.enable_thinking # Switches between thinking and non-thinking modes. Default is True.
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **model_inputs,
                **generation_kwargs,
                logits_processor=self.logit_processors if do_watermark else None,
            )
            torch.cuda.empty_cache()
            
        output_ids = outputs[0][len(model_inputs.input_ids[0]):].tolist() 
        

        # parsing thinking content
        try:
            # rindex finding 151668 (</think>)
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0

        thinking_content = self.tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
        content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

        # print("thinking content:", thinking_content)
        # print("content:", content)
        
        return content
    
class gemini(huggingface_model):
    def __init__(self, model_name="gemini-2.5-flash"):
        # We call super().__init__ but disable model loading and HF login,
        # as they are not needed for the API-based Gemini model.
        super().__init__(model_name=model_name, loaded_model=False, login=False)
        
        # Load the Google API key from config.json
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
            api_key = config.get("google", {}).get("api_key")
            if not api_key:
                raise ValueError("API key for Google not found in config.json")
            
            self.client = genai.Client(api_key=config["google"]["api_key"])
            logger.info("Google Generative AI SDK configured successfully.")

        except FileNotFoundError:
            raise FileNotFoundError("config.json not found. Please create it with your Google API key.")
        except json.JSONDecodeError:
            raise ValueError("Could not decode config.json. Please ensure it is valid JSON.")

        # Instantiate the Gemini model
        self.model = partial(self.client.models.generate_content, model=model_name)
        logger.info(f"Gemini model '{self.model_name}' is ready.")

    def generate(
        self,
        messages: list[dict],
        do_watermark: bool = False,
        **generation_kwargs,
    ) -> str:
        if do_watermark:  raise NotImplementedError("Watermarking during generation is not supported by the Gemini API.")
        
        if "max_length" in generation_kwargs:
            generation_kwargs["max_output_tokens"] = generation_kwargs.pop("max_length")
        if "max_new_tokens" in generation_kwargs:
            generation_kwargs["max_output_tokens"] = generation_kwargs.pop("max_new_tokens")
            
        # generation_config = genai.types.GenerationConfig(**generation_kwargs)

        # Convert the message format from 'content' to Gemini's 'parts'
        gemini_messages = []
        for msg in messages:
            # The Gemini API expects the model's role to be 'model', not 'assistant'
            role = "model" if msg["role"] == "assistant" else msg["role"]
            gemini_messages.append({"role": role, "parts": [msg["content"]]})

        try:
            response = self.model(
                contents=str(gemini_messages),
                # config=generation_config
            )
        except Exception as e:
            # tackle with 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'The model is overloaded. Please try again later.', 'status': 'UNAVAILABLE'}}
            # slepp for 30 seconds and retry
            time.sleep(60)
            try:
                response = self.model(
                    contents=str(gemini_messages),
                    # config=generation_config
                )
                return response.text
            except Exception as e:
                logger.error(f"An error occurred during Gemini API call: {e}")
                return f"Error: Failed to generate response. {e}"
        return response.text
    

    
    
if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Answer concisely."},
        {"role": "user", "content": "Who is the president of Japan?"},
    ]
    
    
    gen_model = qwen3(enable_thinking=True)
    generated = gen_model.generate(messages, max_new_tokens=10240)
    print(generated)
    
    
