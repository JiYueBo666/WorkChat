import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
device = "cuda" # the device to load the model onto

model = AutoModelForCausalLM.from_pretrained(
    r"C:\Users\admin\Desktop\project\text-generation-webui\models\Qwen1.5-7B-Chat",
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(r"C:\Users\admin\Desktop\project\text-generation-webui\models\Qwen1.5-7B-Chat")

prompt = "用户输入一个问题，你只需要给出识别到的用户意图。用户的意图包括【绘图、询问、其他】。只需要给出判断的意图。现在，用户输入是：画个苯环"
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

generated_ids = model.generate(
    model_inputs.input_ids,
    max_new_tokens=512
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(response)