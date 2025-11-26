import json
import os
from transaction import Transaction

class DataHandler:
    FILE_NAME = 'transactions.json'

    def __init__(self):
        self.transactions = []
        self.load_transactions()

    def load_transactions(self):
        """Loads transactions from the JSON file."""
        if os.path.exists(self.FILE_NAME):
            try:
                with open(self.FILE_NAME, 'r') as f:
                    data = json.load(f)
                    self.transactions = [Transaction.from_dict(d) for d in data]
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading data: {e}. Starting with an empty list.")
                self.transactions = []
        else:
            self.transactions = []

    def save_transactions(self):
        """Saves current transactions to the JSON file."""
        try:
            data = [t.to_dict() for t in self.transactions]
            with open(self.FILE_NAME, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Save Error: {e}")
            return False

    def add_transaction(self, type, unit_price, quantity, item_name, note):
        """Creates and adds a transaction object."""
        new_transaction = Transaction(type, unit_price, quantity, item_name, note)
        self.transactions.append(new_transaction)
        self.save_transactions()
        return new_transaction

    def get_current_balance(self):
        """Calculates total balance."""
        return sum(t.get_signed_amount() for t in self.transactions)
    
    def get_all_transactions(self):
        return self.transactions