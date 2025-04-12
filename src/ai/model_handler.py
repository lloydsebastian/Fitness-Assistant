from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

class FitnessModel:
    def __init__(self):
        self.model_name = os.getenv("MODEL_NAME")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, 
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16
        )
    
    def generate_plan(self, user_data):
        prompt = f"""Generate a detailed 4-week fitness plan for:
        - Age: {user_data['age']}
        - Gender: {user_data['sex']}
        - Height: {user_data['height']}cm
        - Weight: {user_data['weight']}kg
        - Goal: {user_data['goal']}
        
        Include:
        1. Daily workout routines with sets/reps
        2. Rest days
        3. Nutritional guidelines
        4. Progress tracking tips"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            inputs.input_ids,
            max_length=1024,
            temperature=0.7,
            do_sample=True
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)