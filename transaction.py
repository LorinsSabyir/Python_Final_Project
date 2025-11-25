from datetime import datetime

# --- 1. OOP Implementation: Transaction Class ---
class Transaction:
    """Represents a single financial transaction. Amount is calculated from Price * Quantity."""
    def __init__(self, type, unit_price, quantity, item_name, note=""):
        # Validate that price and quantity are positive
        if unit_price <= 0 or quantity <= 0:
            raise ValueError("Unit Price and Quantity must be greater than zero.")
            
        self.type = type.lower()  # 'income' or 'expense'
        self.unit_price = float(unit_price)
        self.quantity = int(quantity)
        self.amount = self.unit_price * self.quantity # Calculated total amount
        
        self.item_name = item_name.strip()
        self.note = note.strip()
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_signed_amount(self):
        """Returns the total amount with the correct sign for balance calculation."""
        return self.amount if self.type == 'income' else -self.amount

    def to_dict(self):
        """Converts the transaction object to a dictionary for JSON saving."""
        return {
            'date': self.date,
            'type': self.type,
            'amount': self.amount, # Total amount
            'unit_price': self.unit_price,
            'quantity': self.quantity,
            'item_name': self.item_name,
            'note': self.note
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a Transaction object from a dictionary loaded from JSON, handling legacy data."""
        
        item_name = data.get('item_name') or data.get('description', 'N/A')
        note = data.get('note', '') 
        
        # Handle new fields (unit_price, quantity). If they don't exist (legacy data),
        # assume the existing 'amount' field was the total (price=amount, quantity=1).
        total_amount = data.get('amount', 0)
        unit_price = data.get('unit_price', total_amount)
        quantity = data.get('quantity', 1)

        # Call the standard constructor
        try:
            transaction = cls(data['type'], unit_price, quantity, item_name, note)
        except ValueError:
            # Fallback for corrupted/invalid data, create with minimal data
            unit_price = total_amount if total_amount > 0 else 1.0
            transaction = cls(data['type'], unit_price, 1, item_name, note)
            
        transaction.date = data.get('date', 'Unknown Date') 
        
        # For legacy records, override calculated amount with saved total amount
        if 'unit_price' not in data and 'quantity' not in data:
             transaction.amount = total_amount
             
        return transaction
