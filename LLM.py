import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
device = "cuda" # the device to load the model onto

model = AutoModelForCausalLM.from_pretrained(
    r"C:\Users\admin\Desktop\project\text-generation-webui\models\Qwen1.5-14B-Chat-GPTQ-Int8",
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(r"C:\Users\admin\Desktop\project\text-generation-webui\models\Qwen1.5-14B-Chat-GPTQ-Int8")

prompt = "什么是苯环？"
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(device)


start=time.time()
generated_ids = model.generate(
    model_inputs.input_ids,
    max_new_tokens=512
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(response)
end=time.time()

during=end-start

token_len=len(response)

print(during)
print(token_len)