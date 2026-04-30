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
        """Dynamically find the best available Gemini model that supports generateContent"""
        try:
            genai.configure(api_key=self.api_key)
            available_models = genai.list_models()
            
            # Filter models that support 'generateContent'
            supported_models = [
                m.name for m in available_models 
                if 'generateContent' in m.supported_generation_methods
            ]
            
            if not supported_models:
                return None
            
            # Prefer flash models for speed, otherwise take the first one
            for m in supported_models:
                if 'flash' in m.lower():
                    return m
            return supported_models[0]
            
        except Exception:
            return None

    def analyze_trends(self, asin, history_df):
        if not self.api_key:
            return "Ошибка: API ключ не найден в настройках (Secrets)."

        if not history_df.empty:
            summary = history_df.tail(20).to_string(index=False)
        else:
            summary = "No data available."

        prompt = f"""
        You are an expert Amazon FBA Strategy Consultant. 
        Analyze the following price history for ASIN: {asin}.
        
        Data (timestamp and price):
        {summary}
        
        Please provide:
        1. Trend Analysis: Is the price stable, decreasing, or volatile?
        2. Forecast: What is likely to happen in the next 7 days?
        3. Advertising Strategy (PPC): Should I increase or decrease my ad spend? 
           - If the competitor's price is rising or they are unstable, suggest increasing bids.
           - If there is a heavy price war, suggest cautious spending.
        4. Opportunity: Is there a gap in the market right now?
        
        Answer in Russian, be concise and professional. Use bullet points.
        """

        if self.api_key.startswith("AIza"):
            try:
                model_name = self.get_best_gemini_model()
                if not model_name:
                    return "Ошибка Gemini AI: Не найдено ни одной поддерживаемой модели для вашего ключа."
                
                model = genai.GenerativeModel(model_name=model_name)
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                return f"Ошибка при работе с Gemini: {str(e)}"
        
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
                return f"Ошибка OpenAI AI: {str(e)}"
        else:
            return "Ошибка: Некорректный формат API ключа."
