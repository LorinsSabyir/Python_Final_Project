import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import requests
import threading
from transaction import Transaction

# --- 2. OOP Implementation: FinanceTrackerApp Class (Main Application Logic) ---
class FinanceTrackerApp:
    """The main application class that handles GUI and data logic."""
    
    FILE_NAME = 'transactions.json'
    
    def __init__(self, master):
        self.master = master
        master.title("Personal Finance Tracker")
        master.geometry("1000x700")
        master.configure(bg='#f0f4f8')

        self.transactions = []
        self.load_transactions()
        self.exchange_rates = {}
        
        # Styling configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f4f8')
        self.style.configure('TLabel', background='#f0f4f8', font=('Inter', 10))
        self.style.configure('TButton', font=('Inter', 10, 'bold'), padding=10)
        self.style.map('TButton', 
                       foreground=[('active', 'white')],
                       background=[('active', '#007bff')])
                       
        # Custom styles for text colors (to avoid TclError: unknown option "-fg")
        self.style.configure('Quote.TLabel', foreground='#336699', background='#f0f4f8')
        self.style.configure('StatusSuccess.TLabel', foreground='green', background='#f0f4f8')
        self.style.configure('StatusError.TLabel', foreground='red', background='#f0f4f8')
        self.style.configure('ConversionResult.TLabel', foreground='#0056b3', background='#f0f4f8', font=('Inter', 12, 'bold'))
        self.style.configure('PositiveBalance.TLabel', foreground='green', font=('Inter', 16, 'bold'))
        self.style.configure('NegativeBalance.TLabel', foreground='red', font=('Inter', 16, 'bold'))


        # --- Setup UI Frames ---
        self.top_section = ttk.Frame(master, padding="10")
        self.top_section.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Left side of top section: Balance & Quote
        self.left_top_frame = ttk.Frame(self.top_section, padding="10")
        self.left_top_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.balance_frame = ttk.Frame(self.left_top_frame, padding="15", relief=tk.FLAT)
        self.balance_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.quote_frame = ttk.Frame(self.left_top_frame, padding="10", relief=tk.GROOVE)
        self.quote_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # Right side of top section: Currency Converter
        self.converter_frame = ttk.Frame(self.top_section, padding="15", relief=tk.SUNKEN)
        self.converter_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        
        # Input Frame (below top section)
        self.input_frame = ttk.Frame(master, padding="20", relief=tk.RAISED) 
        self.input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # History Frame (bottom)
        self.history_frame = ttk.Frame(master, padding="10", relief=tk.SUNKEN)
        self.history_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- Build UI Components ---
        self.setup_balance_widgets()
        self.setup_quote_widgets()
        self.setup_converter_widgets()
        self.setup_input_widgets()
        self.setup_history_widgets()
        
        # Initial data refresh
        self.update_balance_display()
        self.update_history_display()
        
        # Fetch initial API data in separate threads
        threading.Thread(target=self.fetch_daily_quote).start()
        threading.Thread(target=self.fetch_exchange_rates).start()
        
    # --- Data Persistence (File Handling) Methods ---
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
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save transactions to file: {e}")

    # --- Core Logic Methods ---
    def get_current_balance(self):
        """Calculates and returns the total current balance."""
        return sum(t.get_signed_amount() for t in self.transactions)

    def add_transaction(self, type, unit_price_str, quantity_str, item_name, note):
        """Processes and adds a new transaction using unit price and quantity."""
        try:
            unit_price = float(unit_price_str)
            quantity = int(quantity_str)
            
            if unit_price <= 0 or quantity <= 0:
                raise ValueError("Price and Quantity must be positive numbers.")
            
            # Ensure an item name is provided for expenses
            if type == 'expense' and not item_name.strip():
                 raise ValueError("Item Name is required for expenses.")

            # Total amount is calculated inside the Transaction class
            new_transaction = Transaction(type, unit_price, quantity, item_name, note)
            self.transactions.append(new_transaction)
            self.save_transactions()
            self.update_balance_display()
            self.update_history_display()
            self.clear_input_fields()
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def clear_input_fields(self):
        """Clears the entry widgets after a successful submission."""
        self.unit_price_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.item_name_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)

    # --- API Integration Methods (Non-Blocking) ---
    def fetch_daily_quote(self):
        """Fetches a random financial/motivational quote from the ZenQuotes API."""
        self.quote_label.config(text="Fetching daily insight...")
        try:
            response = requests.get('https://zenquotes.io/api/random', timeout=5)
            response.raise_for_status() 
            data = response.json()
            
            quote_text = data[0]['q']
            quote_author = data[0]['a']
            
            formatted_quote = f'"{quote_text}" - {quote_author}'
            self.quote_label.config(text=formatted_quote, style='Quote.TLabel')
            
        except requests.RequestException as e:
            print(f"Quote API Error: Could not fetch quote. {e}")
            self.quote_label.config(text="Could not fetch daily insight (API failed).", style='StatusError.TLabel')
    
    def fetch_exchange_rates(self):
        """Fetches latest exchange rates using ExchangeRate-API (Base USD)."""
        self.rate_status_label.config(text="Fetching rates...", style='TLabel')
        API_URL = "https://open.er-api.com/v6/latest/USD"
        try:
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('result') == 'success':
                self.exchange_rates = data['rates']
                currencies = sorted(self.exchange_rates.keys())
                self.from_currency_menu['values'] = currencies
                self.to_currency_menu['values'] = currencies
                
                # Set defaults (PHP requested by user)
                if 'USD' in currencies: self.from_currency_var.set('USD')
                if 'PHP' in currencies: self.to_currency_var.set('PHP')
                
                self.rate_status_label.config(text="Rates updated successfully.", style='StatusSuccess.TLabel')
            else:
                raise Exception(f"API result not successful: {data.get('error-type', 'Unknown Error')}")

        except requests.RequestException as e:
            self.rate_status_label.config(text="Error fetching rates (Network/API).", style='StatusError.TLabel')
            print(f"Currency API Error: {e}")
        except Exception as e:
            self.rate_status_label.config(text="Error processing rates.", style='StatusError.TLabel')
            print(f"Currency Processing Error: {e}")

    def convert_currency(self):
        """Converts the amount based on selected currencies and fetched rates."""
        amount_str = self.convert_amount_entry.get()
        from_currency = self.from_currency_var.get()
        to_currency = self.to_currency_var.get()
        
        if not self.exchange_rates:
            messagebox.showwarning("Converter Warning", "Exchange rates not loaded. Please wait or check your connection.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
            
            # 1. Convert source currency to base currency (USD)
            rate_from_base = self.exchange_rates.get(from_currency)
            if not rate_from_base:
                raise ValueError(f"Rate for {from_currency} not available.")
            
            amount_in_usd = amount / rate_from_base
            
            # 2. Convert from base currency (USD) to target currency
            rate_to_target = self.exchange_rates.get(to_currency)
            if not rate_to_target:
                raise ValueError(f"Rate for {to_currency} not available.")
                
            converted_amount = amount_in_usd * rate_to_target
            
            result_text = f"{converted_amount:,.2f} {to_currency}"
            self.convert_result_label.config(text=result_text, style='ConversionResult.TLabel')
            
        except ValueError as e:
            self.convert_result_label.config(text="Invalid amount or currency selected.", style='StatusError.TLabel')
        except Exception as e:
            self.convert_result_label.config(text="Conversion error.", style='StatusError.TLabel')
            print(f"Conversion runtime error: {e}")


    # --- GUI Setup Methods ---
    def setup_converter_widgets(self):
        """Sets up the widgets for the Currency Converter feature."""
        
        ttk.Label(self.converter_frame, text="Currency Converter", font=('Inter', 12, 'bold')).grid(row=0, column=0, columnspan=4, pady=(0, 10))

        # Inputs
        ttk.Label(self.converter_frame, text="Amount:", font=('Inter', 10)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.convert_amount_entry = ttk.Entry(self.converter_frame, width=10, font=('Inter', 10))
        self.convert_amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # Currency Dropdowns
        self.from_currency_var = tk.StringVar(self.converter_frame)
        self.to_currency_var = tk.StringVar(self.converter_frame)
        
        self.from_currency_menu = ttk.Combobox(self.converter_frame, textvariable=self.from_currency_var, width=8, state="readonly")
        self.from_currency_menu.grid(row=1, column=2, padx=5, pady=5, sticky='ew')
        self.from_currency_menu['values'] = ['USD', 'PHP', 'EUR', 'JPY'] # Placeholder values
        
        ttk.Label(self.converter_frame, text="to", font=('Inter', 10, 'italic')).grid(row=1, column=3, padx=5, pady=5, sticky='w')
        
        self.to_currency_menu = ttk.Combobox(self.converter_frame, textvariable=self.to_currency_var, width=8, state="readonly")
        self.to_currency_menu.grid(row=2, column=2, padx=5, pady=5, sticky='ew')
        self.to_currency_menu['values'] = ['USD', 'PHP', 'EUR', 'JPY'] # Placeholder values

        # Convert Button
        ttk.Button(self.converter_frame, text="Convert", command=self.convert_currency, style='Primary.TButton').grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky='ew')
        
        # Result Display
        ttk.Label(self.converter_frame, text="Result:", font=('Inter', 10, 'bold')).grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.convert_result_label = ttk.Label(self.converter_frame, text="--.--", style='ConversionResult.TLabel')
        self.convert_result_label.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky='ew')
        
        # Status Label
        self.rate_status_label = ttk.Label(self.converter_frame, text="Loading...", font=('Inter', 8, 'italic'))
        self.rate_status_label.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky='w')
        
        # Configure grid expansion
        self.converter_frame.columnconfigure(1, weight=1)
        self.converter_frame.columnconfigure(2, weight=1)
        self.style.configure('Primary.TButton', background='#007bff', foreground='white')


    def setup_input_widgets(self):
        """Sets up the widgets for adding new transactions, using Unit Price and Quantity."""
        
        # Row 0: Unit Price, Quantity, and Item Name
        
        # Unit Price
        ttk.Label(self.input_frame, text="Unit Price ($):", font=('Inter', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.unit_price_entry = ttk.Entry(self.input_frame, width=12, font=('Inter', 10))
        self.unit_price_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Quantity
        ttk.Label(self.input_frame, text="Quantity:", font=('Inter', 10, 'bold')).grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.quantity_entry = ttk.Entry(self.input_frame, width=8, font=('Inter', 10))
        self.quantity_entry.grid(row=0, column=3, padx=5, pady=5, sticky='ew')

        # Item Name
        ttk.Label(self.input_frame, text="Item Name:", font=('Inter', 10, 'bold')).grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.item_name_entry = ttk.Entry(self.input_frame, width=20, font=('Inter', 10))
        self.item_name_entry.grid(row=0, column=5, padx=5, pady=5, sticky='ew')
        
        # Row 1: Note/Details
        ttk.Label(self.input_frame, text="Note/Details:", font=('Inter', 10, 'bold')).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.note_entry = ttk.Entry(self.input_frame, width=50, font=('Inter', 10))
        self.note_entry.grid(row=1, column=1, columnspan=5, padx=5, pady=5, sticky='ew')
        
        # Row 2: Action Buttons
        income_cmd = lambda: self.add_transaction('income', 
                                                  self.unit_price_entry.get(), 
                                                  self.quantity_entry.get(),
                                                  self.item_name_entry.get(), 
                                                  self.note_entry.get())
        
        expense_cmd = lambda: self.add_transaction('expense', 
                                                   self.unit_price_entry.get(), 
                                                   self.quantity_entry.get(),
                                                   self.item_name_entry.get(), 
                                                   self.note_entry.get())
        
        ttk.Button(self.input_frame, text="Add Income (+)", 
                   command=income_cmd,
                   style='Success.TButton').grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky='ew')
        
        ttk.Button(self.input_frame, text="Add Expense (-)", 
                   command=expense_cmd,
                   style='Danger.TButton').grid(row=2, column=3, columnspan=3, padx=5, pady=10, sticky='ew')
                   
        # Custom button styles for color
        self.style.configure('Success.TButton', background='#28a745', foreground='white') # Green
        self.style.configure('Danger.TButton', background='#dc3545', foreground='white') # Red

        # Make input frame columns expandable
        self.input_frame.columnconfigure(1, weight=1)
        self.input_frame.columnconfigure(3, weight=1)
        self.input_frame.columnconfigure(5, weight=2) # Item Name can take more space


    def setup_balance_widgets(self):
        """Sets up the balance display area."""
        ttk.Label(self.balance_frame, text="Current Balance:", font=('Inter', 14, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self.balance_display = ttk.Label(self.balance_frame, text="$0.00", style='PositiveBalance.TLabel', anchor='e')
        self.balance_display.pack(side=tk.RIGHT, padx=10, fill=tk.X, expand=True)

        self.balance_frame.columnconfigure(1, weight=1)

    def setup_quote_widgets(self):
        """Sets up the daily quote display."""
        ttk.Label(self.quote_frame, text="Daily Insight:", font=('Inter', 10, 'italic')).pack(side=tk.LEFT)
        self.quote_label = ttk.Label(self.quote_frame, text="Loading...", font=('Inter', 9), wraplength=400, style='Quote.TLabel')
        self.quote_label.pack(side=tk.LEFT, padx=10)

    
    def setup_history_widgets(self):
        """Sets up the Treeview widget for transaction history, now showing Price and Quantity."""
        
        ttk.Label(self.history_frame, text="Transaction History", font=('Inter', 12, 'bold')).pack(pady=5)
        
        # Create a scrollbar
        scrollbar = ttk.Scrollbar(self.history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create the Treeview, updated columns
        self.history_tree = ttk.Treeview(self.history_frame, 
                                         columns=('Date', 'Type', 'Item Name', 'Unit Price', 'Quantity', 'Note', 'Amount'), 
                                         show='headings', 
                                         yscrollcommand=scrollbar.set)
        
        self.history_tree.heading('Date', text='Date', anchor=tk.W)
        self.history_tree.heading('Type', text='Type', anchor=tk.W)
        self.history_tree.heading('Item Name', text='Item Name', anchor=tk.W)
        self.history_tree.heading('Unit Price', text='Unit Price ($)', anchor=tk.E)
        self.history_tree.heading('Quantity', text='Qty', anchor=tk.E)
        self.history_tree.heading('Note', text='Note/Details', anchor=tk.W)
        self.history_tree.heading('Amount', text='Total ($)', anchor=tk.E)
        
        # Define column widths (adjusted for new columns)
        self.history_tree.column('Date', width=100, anchor=tk.W)
        self.history_tree.column('Type', width=60, anchor=tk.W)
        self.history_tree.column('Item Name', width=150, anchor=tk.W)
        self.history_tree.column('Unit Price', width=90, anchor=tk.E)
        self.history_tree.column('Quantity', width=50, anchor=tk.E)
        self.history_tree.column('Note', width=200, anchor=tk.W)
        self.history_tree.column('Amount', width=90, anchor=tk.E)
        
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_tree.yview)

        # Add tags for row colors (Visual/Interactive Element)
        self.history_tree.tag_configure('income', background='#e6ffe6') # Light Green
        self.history_tree.tag_configure('expense', background='#ffe6e6') # Light Red

    # --- GUI Update Methods ---
    def update_balance_display(self):
        """Calculates and updates the balance display text and color."""
        balance = self.get_current_balance()
        balance_text = f"${balance:,.2f}"
        
        new_style = 'PositiveBalance.TLabel' if balance >= 0 else 'NegativeBalance.TLabel'
        
        self.balance_display.config(text=balance_text, style=new_style)

    def update_history_display(self):
        """Clears and re-populates the transaction history Treeview."""
        
        # Clear existing entries
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Insert new entries (in reverse chronological order)
        for t in reversed(self.transactions):
            # Format amounts as currency strings
            amount_str = f"{t.amount:,.2f}"
            unit_price_str = f"{t.unit_price:,.2f}"
            
            # Determine the display tag for color coding
            tag = t.type
            
            # Updated values list for the Treeview
            self.history_tree.insert('', tk.END, 
                                     values=(t.date.split(' ')[0], 
                                             t.type.capitalize(), 
                                             t.item_name,
                                             unit_price_str, 
                                             t.quantity,
                                             t.note,      
                                             amount_str),
                                     tags=(tag,))


if __name__ == '__main__':
    # Initialize the main Tkinter window
    root = tk.Tk()
    
    # Run the application
    app = FinanceTrackerApp(root)
    
    # Start the Tkinter event loop
    root.mainloop()