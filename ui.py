import tkinter as tk
from tkinter import ttk, messagebox
import threading
from data_handler import DataHandler
from logic import APILogic

class FinanceTrackerUI:
    def __init__(self, master):
        self.master = master
        self.data_handler = DataHandler() # Connect to Data
        self.exchange_rates = {}

        master.title("Personal Finance Tracker")
        master.geometry("1000x700")
        master.configure(bg='#f0f4f8')

        # Styling
        self.setup_styles()

        # Layout Frames
        self.create_layout_frames()

        # Build Components
        self.setup_balance_widgets()
        self.setup_quote_widgets()
        self.setup_converter_widgets()
        self.setup_input_widgets()
        self.setup_history_widgets()

        # Initial Refresh
        self.refresh_ui_data()

        # Background Tasks
        self.start_background_threads()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f4f8')
        self.style.configure('TLabel', background='#f0f4f8', font=('Inter', 10))
        self.style.configure('TButton', font=('Inter', 10, 'bold'), padding=10)
        self.style.map('TButton', foreground=[('active', 'white')], background=[('active', '#007bff')])
        
        # Custom styles
        self.style.configure('Quote.TLabel', foreground='#336699', background='#f0f4f8')
        self.style.configure('StatusSuccess.TLabel', foreground='green', background='#f0f4f8')
        self.style.configure('StatusError.TLabel', foreground='red', background='#f0f4f8')
        self.style.configure('ConversionResult.TLabel', foreground='#0056b3', background='#f0f4f8', font=('Inter', 12, 'bold'))
        self.style.configure('PositiveBalance.TLabel', foreground='green', font=('Inter', 16, 'bold'))
        self.style.configure('NegativeBalance.TLabel', foreground='red', font=('Inter', 16, 'bold'))
        self.style.configure('Primary.TButton', background='#007bff', foreground='white')
        self.style.configure('Success.TButton', background='#28a745', foreground='white')
        self.style.configure('Danger.TButton', background='#dc3545', foreground='white')

    def create_layout_frames(self):
        self.top_section = ttk.Frame(self.master, padding="10")
        self.top_section.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        self.left_top_frame = ttk.Frame(self.top_section, padding="10")
        self.left_top_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.balance_frame = ttk.Frame(self.left_top_frame, padding="15", relief=tk.FLAT)
        self.balance_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.quote_frame = ttk.Frame(self.left_top_frame, padding="10", relief=tk.GROOVE)
        self.quote_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.converter_frame = ttk.Frame(self.top_section, padding="15", relief=tk.SUNKEN)
        self.converter_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        
        self.input_frame = ttk.Frame(self.master, padding="20", relief=tk.RAISED) 
        self.input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        self.history_frame = ttk.Frame(self.master, padding="10", relief=tk.SUNKEN)
        self.history_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- Setup Widgets Methods ---
    def setup_balance_widgets(self):
        ttk.Label(self.balance_frame, text="Current Balance:", font=('Inter', 14, 'bold')).pack(side=tk.LEFT, padx=10)
        self.balance_display = ttk.Label(self.balance_frame, text="$0.00", style='PositiveBalance.TLabel', anchor='e')
        self.balance_display.pack(side=tk.RIGHT, padx=10, fill=tk.X, expand=True)

    def setup_quote_widgets(self):
        ttk.Label(self.quote_frame, text="Daily Insight:", font=('Inter', 10, 'italic')).pack(side=tk.LEFT)
        self.quote_label = ttk.Label(self.quote_frame, text="Loading...", font=('Inter', 9), wraplength=400, style='Quote.TLabel')
        self.quote_label.pack(side=tk.LEFT, padx=10)

    def setup_converter_widgets(self):
        ttk.Label(self.converter_frame, text="Currency Converter", font=('Inter', 12, 'bold')).grid(row=0, column=0, columnspan=4, pady=(0, 10))
        
        ttk.Label(self.converter_frame, text="Amount:", font=('Inter', 10)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.convert_amount_entry = ttk.Entry(self.converter_frame, width=10, font=('Inter', 10))
        self.convert_amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        self.from_currency_var = tk.StringVar()
        self.to_currency_var = tk.StringVar()
        
        self.from_currency_menu = ttk.Combobox(self.converter_frame, textvariable=self.from_currency_var, width=8, state="readonly")
        self.from_currency_menu.grid(row=1, column=2, padx=5, pady=5, sticky='ew')
        
        ttk.Label(self.converter_frame, text="to", font=('Inter', 10, 'italic')).grid(row=1, column=3, padx=5, pady=5, sticky='w')
        
        self.to_currency_menu = ttk.Combobox(self.converter_frame, textvariable=self.to_currency_var, width=8, state="readonly")
        self.to_currency_menu.grid(row=2, column=2, padx=5, pady=5, sticky='ew')

        ttk.Button(self.converter_frame, text="Convert", command=self.process_conversion, style='Primary.TButton').grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky='ew')
        
        ttk.Label(self.converter_frame, text="Result:", font=('Inter', 10, 'bold')).grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.convert_result_label = ttk.Label(self.converter_frame, text="--.--", style='ConversionResult.TLabel')
        self.convert_result_label.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky='ew')
        
        self.rate_status_label = ttk.Label(self.converter_frame, text="Loading...", font=('Inter', 8, 'italic'))
        self.rate_status_label.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky='w')

    def setup_input_widgets(self):
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
        
        # Note
        ttk.Label(self.input_frame, text="Note/Details:", font=('Inter', 10, 'bold')).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.note_entry = ttk.Entry(self.input_frame, width=50, font=('Inter', 10))
        self.note_entry.grid(row=1, column=1, columnspan=5, padx=5, pady=5, sticky='ew')
        
        # Buttons
        income_cmd = lambda: self.submit_transaction('income')
        expense_cmd = lambda: self.submit_transaction('expense')
        
        ttk.Button(self.input_frame, text="Add Income (+)", command=income_cmd, style='Success.TButton').grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky='ew')
        ttk.Button(self.input_frame, text="Add Expense (-)", command=expense_cmd, style='Danger.TButton').grid(row=2, column=3, columnspan=3, padx=5, pady=10, sticky='ew')

        self.input_frame.columnconfigure(1, weight=1)
        self.input_frame.columnconfigure(3, weight=1)
        self.input_frame.columnconfigure(5, weight=2)

    def setup_history_widgets(self):
        ttk.Label(self.history_frame, text="Transaction History", font=('Inter', 12, 'bold')).pack(pady=5)
        scrollbar = ttk.Scrollbar(self.history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_tree = ttk.Treeview(self.history_frame, 
                                         columns=('Date', 'Type', 'Item Name', 'Unit Price', 'Quantity', 'Note', 'Amount'), 
                                         show='headings', 
                                         yscrollcommand=scrollbar.set)
        
        # Configure columns (headers and widths)
        cols = [('Date', 100), ('Type', 60), ('Item Name', 150), ('Unit Price', 90), ('Quantity', 50), ('Note', 200), ('Amount', 90)]
        for col, width in cols:
            self.history_tree.heading(col, text=col, anchor=tk.W if col not in ['Unit Price', 'Quantity', 'Amount'] else tk.E)
            self.history_tree.column(col, width=width, anchor=tk.W if col not in ['Unit Price', 'Quantity', 'Amount'] else tk.E)
        
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_tree.yview)
        
        self.history_tree.tag_configure('income', background='#e6ffe6')
        self.history_tree.tag_configure('expense', background='#ffe6e6')

    # --- Interaction Methods ---
    def submit_transaction(self, type):
        try:
            # Gather inputs
            u_price = self.unit_price_entry.get()
            qty = self.quantity_entry.get()
            name = self.item_name_entry.get()
            note = self.note_entry.get()

            # Logic Check
            if type == 'expense' and not name.strip():
                raise ValueError("Item Name is required for expenses.")
            if float(u_price) <= 0 or int(qty) <= 0:
                 raise ValueError("Price and Quantity must be positive.")

            # Send to Data Handler
            self.data_handler.add_transaction(type, u_price, qty, name, note)
            
            # UI Updates
            self.refresh_ui_data()
            self.clear_inputs()
            
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")

    def clear_inputs(self):
        self.unit_price_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.item_name_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)

    def process_conversion(self):
        amt = self.convert_amount_entry.get()
        f_curr = self.from_currency_var.get()
        t_curr = self.to_currency_var.get()
        
        try:
            val = float(amt)
            if val <= 0: raise ValueError
            
            # Call Logic Module
            result = APILogic.calculate_conversion(val, f_curr, t_curr, self.exchange_rates)
            self.convert_result_label.config(text=f"{result:,.2f} {t_curr}", style='ConversionResult.TLabel')
            
        except ValueError as e:
            self.convert_result_label.config(text="Invalid Input", style='StatusError.TLabel')
        except Exception as e:
            print(e)
            self.convert_result_label.config(text="Error", style='StatusError.TLabel')

    # --- UI Refresh & Threads ---
    def refresh_ui_data(self):
        # Update Balance
        bal = self.data_handler.get_current_balance()
        style = 'PositiveBalance.TLabel' if bal >= 0 else 'NegativeBalance.TLabel'
        self.balance_display.config(text=f"${bal:,.2f}", style=style)

        # Update History
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        for t in reversed(self.data_handler.get_all_transactions()):
            self.history_tree.insert('', tk.END, 
                                     values=(t.date.split(' ')[0], t.type.capitalize(), t.item_name, 
                                             f"{t.unit_price:,.2f}", t.quantity, t.note, f"{t.amount:,.2f}"),
                                     tags=(t.type,))

    def start_background_threads(self):
        threading.Thread(target=self._update_quote, daemon=True).start()
        threading.Thread(target=self._update_rates, daemon=True).start()

    def _update_quote(self):
        quote = APILogic.fetch_daily_quote()
        if quote:
            self.master.after(0, lambda: self.quote_label.config(text=quote, style='Quote.TLabel'))
        else:
            self.master.after(0, lambda: self.quote_label.config(text="Could not fetch insight.", style='StatusError.TLabel'))

    def _update_rates(self):
        rates = APILogic.fetch_exchange_rates()
        if rates:
            self.exchange_rates = rates
            currencies = sorted(rates.keys())
            
            def update_dropdowns():
                self.from_currency_menu['values'] = currencies
                self.to_currency_menu['values'] = currencies
                if 'USD' in currencies: self.from_currency_var.set('USD')
                if 'PHP' in currencies: self.to_currency_var.set('PHP')
                self.rate_status_label.config(text="Rates updated.", style='StatusSuccess.TLabel')
            
            self.master.after(0, update_dropdowns)
        else:
            self.master.after(0, lambda: self.rate_status_label.config(text="Rate fetch failed.", style='StatusError.TLabel'))