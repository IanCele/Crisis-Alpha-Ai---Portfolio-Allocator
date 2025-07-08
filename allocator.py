from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import yfinance as yf

class CrisisAllocator:
    def __init__(self, openai_api_key):
        self.llm = ChatOpenAI(model="gpt-4-1106-preview", api_key=openai_api_key, temperature=0.2)
        
    def get_market_snapshot(self):
        """Get real-time market data for context"""
        tickers = ["^GSPC", "GLD", "ICLN", "BTC-USD", "^VIX", "LMT", "NOC"]
        data = yf.download(tickers, period="1d", progress=False)
        return data['Close'].iloc[-1].to_dict()
    
    def generate_allocation(self, crisis_params, market_data):
        template = """
        As Chief Investment Officer of AlphaCrisis AI, analyze this crisis scenario:
        {crisis_summary}
        
        Current market snapshot:
        {market_data}
        
        Recommended allocation (%):
        - Defense stocks: __DEFENSE__%
        - Gold: __GOLD__%
        - ESG assets: __ESG__%
        - Cryptocurrency: __CRYPTO__%
        - Cash: __CASH__%
        
        Investment thesis (max 100 words): __THESIS__
        """
        prompt = PromptTemplate(
            template=template,
            input_variables=["crisis_summary", "market_data"]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run({
            "crisis_summary": crisis_params,
            "market_data": str(market_data)
        })
        
        # Parse structured output
        return self._parse_response(response)
    
    def _parse_response(self, text):
        """Convert text response to structured data"""
        # GPT-4 now outputs parsable format
        return {
            "defense": float(text.split("__DEFENSE__%")[0].split()[-1]),
            "gold": float(text.split("__GOLD__%")[0].split()[-1]),
            "esg": float(text.split("__ESG__%")[0].split()[-1]),
            "crypto": float(text.split("__CRYPTO__%")[0].split()[-1]),
            "cash": float(text.split("__CASH__%")[0].split()[-1]),
            "thesis": text.split("__THESIS__")[1].strip()
        }
