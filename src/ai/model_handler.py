from transformers import AutoTokenizer, AutoModelForCausalLM
from dotenv import load_dotenv
import torch
import os

load_dotenv()

class FitnessModel:
    def __init__(self):
        self.model_name = os.getenv("MODEL_NAME")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, 
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16
        ).to(self.device)
    
    def generate_plan(self, user_data):
        prompt = f"""Generate a detailed 4-week fitness plan as plain text for the following user:
        Age: {user_data['age']}
        Gender: {user_data['sex']}
        Height: {user_data['height']} cm
        Weight: {user_data['weight']} kg
        Goal: {user_data['goal']}

        The plan should include:
    1. Daily workout routines with sets/reps for each day, clearly labeled (e.g., "Day 1:", "Day 2:", etc.)
    2. Clearly indicated rest days.
    3. Nutritional guidelines.
    4. Progress tracking tips.

    Please ensure the response is only plain text without any code formatting or programming syntax.
    """
        inputs = self.tokenizer(prompt, return_tensors="pt")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        outputs = self.model.generate(
            inputs["input_ids"],
            max_length=1024,
            temperature=0.7,
            do_sample=True
        )
        decoded_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        if decoded_output.startswith(prompt):
            decoded_output = decoded_output[len(prompt):]
        return decoded_output.strip()