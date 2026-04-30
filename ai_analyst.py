import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AIAnalyst:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def analyze_trends(self, asin, history_df):
        """
        Sends price history to AI and gets strategic advice.
        """
        if history_df.empty:
            return "Недостаточно данных для анализа."

        # Prepare a text summary of the data for the AI
        # We take the last 10-20 points to keep the prompt concise
        summary = history_df.tail(20).to_string(index=False)
        
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
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional Amazon business analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Ошибка AI: {str(e)}"
