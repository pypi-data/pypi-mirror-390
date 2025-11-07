from gen_model import gpt_oss, qwen3
from gen_model import gemini

from watermark.auto_watermark import AutoWatermark
from watermark.transformers_config import TransformersConfig


def assembly_gpt_oss(size="20b", watermark_scheme = "KGW"):
    assert size in ["20b", "120b"], "The size for the gpt oss model should be chosen from 20b or 120b"
    gen_model = gpt_oss(f"openai/gpt-oss-{size}")
    
    transformers_config = TransformersConfig(
        model=gen_model.model,
        tokenizer=gen_model.tokenizer,
        vocab_size=201088,
        device="cuda",
        max_new_tokens=1024,
        min_length=32,
        do_sample=True,
        no_repeat_ngram_size=4
    )
    Watermark = AutoWatermark.load(watermark_scheme, algorithm_config=f'watermark/{watermark_scheme}.json',transformers_config=transformers_config)
    
    gen_model.load_watermark(Watermark)
    
    return gen_model
    
def assembly_qwen3(size="8B", watermark_scheme = "KGW", enable_thinking=False):
    assert size in ["4B",  "8B", "14B", "32B"], "The size for the qwen3 model should be chosen from 8B or 14B"
    gen_model = qwen3(f"Qwen/Qwen3-{size}", enable_thinking=enable_thinking)
    
    transformers_config = TransformersConfig(
        model=gen_model.model,
        tokenizer=gen_model.tokenizer,
        vocab_size=151936,
        device="cuda",
        max_new_tokens=1024,
        min_length=32,
        do_sample=True,
        no_repeat_ngram_size=4
    )
    Watermark = AutoWatermark.load(watermark_scheme, algorithm_config=f'watermark/{watermark_scheme}.json',transformers_config=transformers_config)
    
    gen_model.load_watermark(Watermark)
    
    return gen_model

def assembly_gemini(model_name="gemini-2.5-flash", watermark_scheme = "KGW"):
    pesudo_model = qwen3(f"Qwen/Qwen3-4B", enable_thinking=False)
    
    transformers_config = TransformersConfig(
        model=pesudo_model.model,
        tokenizer=pesudo_model.tokenizer,
        vocab_size=151936,
        device="cuda",
        max_new_tokens=1024,
        min_length=32,
        do_sample=True,
        no_repeat_ngram_size=4
    )
    Watermark = AutoWatermark.load(watermark_scheme, algorithm_config=f'watermark/{watermark_scheme}.json',transformers_config=transformers_config)
    
    gen_model = gemini(model_name=model_name)
    Watermark = AutoWatermark.load(watermark_scheme, algorithm_config=f'watermark/{watermark_scheme}.json',transformers_config=transformers_config)
    
    gen_model.load_watermark(Watermark)
    return gen_model