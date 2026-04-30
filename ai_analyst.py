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

    def analyze_trends(self, asin, history_df):
        """
        Analyzes price history using either OpenAI or Google Gemini depending on the key.
        """
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
                genai.configure(api_key=self.api_key)
                
                # Try multiple models in case of 404
                models_to_try = ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.0-pro']
                last_error = ""
                
                for model_name in models_to_try:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        return response.text
                    except Exception as e:
                        last_error = str(e)
                        continue
                
                return f"Ошибка Gemini AI: Ни одна из доступных моделей не сработала. {last_error}"
                
            except Exception as e:
                return f"Общая ошибка Gemini AI: {str(e)}"
        
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
            return "Ошибка: Некорректный формат API ключа. Ключ должен начинаться с 'sk-' (OpenAI) или 'AIza' (Gemini)."
