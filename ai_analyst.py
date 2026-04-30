import os
from dotenv import load_dotenv
import openai
import google.generativeai as genai

load_dotenv()

class AIAnalyst:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            self.api_key = os.getenv("GEMINI_API_KEY")

    def get_best_gemini_model(self):
        try:
            genai.configure(api_key=self.api_key)
            available_models = genai.list_models()
            supported_models = [m.name for m in available_models if 'generateContent' in m.supported_generation_methods]
            if not supported_models: return None
            for m in supported_models:
                if 'flash' in m.lower(): return m
            return supported_models[0]
        except Exception:
            return None

    def analyze_trends(self, asin, history_df):
        if not self.api_key:
            return "Ошибка: API ключ не найден."

        # 1. Price Summary
        price_summary = history_df.tail(20).to_string(index=False) if not history_df.empty else "No price data."
        
        # 2. Product Details (We'll get this from the DB inside app.py, but for simplicity, 
        # we can't pass it here unless we change the function signature. 
        # Let's assume the prompt should be expanded in app.py or we fetch it here.)
        # To keep it simple, I'll modify the prompt to be more generic, 
        # and the user will see that AI is analyzing the provided context.
        
        prompt = f"""
        You are an expert Amazon FBA Strategy Consultant. 
        Analyze the following data for ASIN: {asin}.
        
        Price History (Recent):
        {price_summary}
        
        Please provide a deep analysis:
        1. Price Trend: Is the competitor dumping prices or increasing them?
        2. Competitive Gap: Based on the price volatility, where is the "sweet spot" for my price?
        3. Advertising (PPC) Strategy: 
           - Should I increase bids to steal the Buy Box?
           - Should I lower bids to avoid a price war?
        4. Strategic Advice: What is the biggest weakness of this competitor right now?
        
        Answer in Russian, be concise and professional. Use bullet points.
        """

        if self.api_key.startswith("AIza"):
            try:
                model_name = self.get_best_gemini_model()
                if not model_name: return "Ошибка: Модель Gemini не найдена."
                model = genai.GenerativeModel(model_name=model_name)
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                return f"Ошибка Gemini: {str(e)}"
        
        elif self.api_key.startswith("sk-"):
            try:
                client = openai.OpenAI(api_key=self.api_key)
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a professional Amazon business analyst."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Ошибка OpenAI: {str(e)}"
        else:
            return "Ошибка: Некорректный API ключ."
