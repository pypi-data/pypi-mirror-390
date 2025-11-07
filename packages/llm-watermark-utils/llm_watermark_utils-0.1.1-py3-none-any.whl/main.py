from gen_model import huggingface_model
from assembly_models import assembly_qwen3
def main():
    gen_model:huggingface_model = assembly_qwen3()
    prompt = "Explain the theory of relativity in simple terms."
    messages = [
        {"role": "user", "content": prompt}
    ]

    watermarked_text = gen_model.generate(messages, do_watermark=True, max_new_tokens=200)
    print(watermarked_text)
    print(gen_model.detect_watermark(watermarked_text))
    print("----------")
    non_watermarked_text = gen_model.generate(messages, do_watermark=False, max_new_tokens=200)
    print(non_watermarked_text)
    print(gen_model.detect_watermark(non_watermarked_text))
    print("----------")
    
    


if __name__ == "__main__":
    main()
