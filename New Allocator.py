import yfinance as yf
import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CrisisAllocator:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("OpenAI API key is required for CrisisAllocator.")
        self.llm = ChatOpenAI(model="gpt-4o", api_key=api_key, temperature=0.3)
        self.template = """
        As a Crisis Portfolio AI, analyze the current situation:
        Geopolitical tension: {geo_risk}/10
        Inflation rate: {inflation}%
        Election risk: {election_risk}/10
        Market volatility (VIX): {vix}
        
        Current asset performance:
        {asset_performance}
        
        Generate allocation recommendations (%):
        - Defense (e.g. LMT, RTX)
        - Gold (e.g. GLD)
        - ESG (e.g. ICLN, ESGU)
        - Crypto (e.g. BTC-USD, ETH-USD)
        - Cash
        
        Output ONLY in JSON format. Ensure all percentage values sum to 100 or very close (e.g., 99-101 due to rounding):
        {{ "defense": 0, "gold": 0, "esg": 0, "crypto": 0, "cash": 0, "reasoning": "A concise explanation for the allocation, max 150 chars" }}
        """
        self.prompt = PromptTemplate.from_template(self.template)
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def get_asset_performance(self):
        tickers = ["^GSPC", "GLD", "ICLN", "BTC-USD", "^VIX", "LMT", "NOC", "ESGU", "SLV", "ETH-USD"] 
        try:
            data = yf.download(tickers, period="1d", interval="1m", progress=False)
            if data.empty or 'Close' not in data:
                logging.warning("Could not fetch 1m interval data, trying 1d.")
                data = yf.download(tickers, period="1d", progress=False)
                if data.empty or 'Close' not in data:
                    logging.error(f"Failed to download data for {tickers} after multiple attempts.")
                    return {}
                return data["Close"].iloc[-1].to_dict()
            return data["Close"].iloc[-1].to_dict()
        except Exception as e:
            logging.error(f"Error fetching asset performance: {e}")
            return {}
    
    def allocate(self, geo_risk, inflation, election_risk):
        assets_data = self.get_asset_performance()
        vix = assets_data.get("^VIX", 20)
        
        asset_performance_str = "\n".join([f"{k}: {v:.2f}" if isinstance(v, (int, float)) else f"{k}: {v}" for k, v in assets_data.items()])

        try:
            response = self.chain.invoke(
                {
                    "geo_risk": geo_risk,
                    "inflation": inflation,
                    "election_risk": election_risk,
                    "vix": vix,
                    "asset_performance": asset_performance_str
                }
            )
            json_output = json.loads(response['text'])
            total_percent = sum(json_output.get(k, 0) for k in ["defense", "gold", "esg", "crypto", "cash"])
            if not (99 <= total_percent <= 101):
                logging.warning(f"AI allocation percentages do not sum to 100% (total: {total_percent}). Attempting to normalize.")
                if total_percent > 0:
                    for key in ["defense", "gold", "esg", "crypto", "cash"]:
                        json_output[key] = round(json_output.get(key, 0) / total_percent * 100)
            
            return json_output
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from AI response: {e}. Response: {response.get('text')}")
            return {"error": "AI response not in valid JSON format."}
        except Exception as e:
            logging.error(f"Error during AI allocation: {e}")
            return {"error": f"An unexpected error occurred during AI allocation: {e}"}
