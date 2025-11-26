import tkinter as tk
from ui import FinanceTrackerUI

if __name__ == '__main__':
    root = tk.Tk()
    app = FinanceTrackerUI(root)
    root.mainloop()