import requests

class APILogic:
    
    @staticmethod
    def fetch_daily_quote():
        """Fetches a random quote from ZenQuotes."""
        try:
            response = requests.get('https://zenquotes.io/api/random', timeout=5)
            response.raise_for_status()
            data = response.json()
            return f'"{data[0]["q"]}" - {data[0]["a"]}'
        except Exception as e:
            print(f"Quote API Error: {e}")
            return None

    @staticmethod
    def fetch_exchange_rates(base_currency="USD"):
        """Fetches latest exchange rates."""
        url = f"https://open.er-api.com/v6/latest/{base_currency}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data and data.get('result') == 'success':
                return data['rates']
            else:
                return None
        except Exception as e:
            print(f"Currency API Error: {e}")
            return None

    @staticmethod
    def calculate_conversion(amount, from_curr, to_curr, rates):
        """Performs the currency conversion math."""
        if not rates:
            raise ValueError("Exchange rates not loaded.")
            
        rate_from_base = rates.get(from_curr)
        rate_to_target = rates.get(to_curr)
        
        if not rate_from_base or not rate_to_target:
            raise ValueError("Currency rate unavailable.")
            
        # Convert to Base (USD) then to Target
        amount_in_usd = amount / rate_from_base
        converted_amount = amount_in_usd * rate_to_target
        return converted_amount