this is the initial version for myself usage

example usage:
```python
from llm_watermark import assembly_qwen3, huggingface_model


wm_model: huggingface_model = assembly_qwen3("8B")
prompt = "Write a short story about a robot learning to love."
messages = [{"role": "user", "content": prompt}]

wm_response = wm_model.generate(messages, do_watermark=True, max_new_tokens=256)
print("Watermarked Response:", wm_response)
print(wm_model.detect_watermark(wm_response))
print("----------------")

non_wm_response = wm_model.generate(messages, do_watermark=False, max_new_tokens=256)
print("Non-Watermarked Response:", non_wm_response)
print(wm_model.detect_watermark(non_wm_response))
```