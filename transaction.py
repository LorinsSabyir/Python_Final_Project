import datetime

class Transaction:
    def __init__(self, type, unit_price, quantity, item_name, note, date=None):
        self.type = type
        self.unit_price = float(unit_price)
        self.quantity = int(quantity)
        self.item_name = item_name
        self.note = note
        self.amount = self.unit_price * self.quantity
        
        if date:
            self.date = date
        else:
            self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_signed_amount(self):
        """Returns positive for income, negative for expense."""
        if self.type == 'income':
            return self.amount
        else:
            return -self.amount

    def to_dict(self):
        """Converts object to dictionary for JSON saving."""
        return {
            'type': self.type,
            'unit_price': self.unit_price,
            'quantity': self.quantity,
            'item_name': self.item_name,
            'note': self.note,
            'date': self.date
        }

    @classmethod
    def from_dict(cls, data):
        """Creates object from dictionary (loading from JSON)."""
        return cls(
            data['type'],
            data['unit_price'],
            data['quantity'],
            data['item_name'],
            data['note'],
            data.get('date')
        )