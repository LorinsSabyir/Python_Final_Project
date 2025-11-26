# 📊 Personal Accounting App (Python GUI)

**Group Final Project para sa subject na IT415 - Application Development and Emerging Technologies**

Kini ang among simple na **Personal Accounting App** na gihimo gamit ang **Python** ug **Tkinter**. Gidisenyo ni para madali ninyo ma-monitor ang inyong mga kita (**income**) ug mga gasto (**expenses**). Ang code ani, gi-organize gyud namo gamit ang **MVC (Model-View-Controller)** pattern.

---

## 🚀 Mga Features (Ang mga Pwede Ninyong Himoon)

* **Easy I-add ang Income & Expense:** Easy ra kaayo i-record ang inyong mga transactions. Makita pud ninyo ang Quantity ug Unit Price sa inyong mga gipamalit.
* **Dili gyud Mawala ang Data:** Automatic na ma-save ang tanang transactions sa file na `transactions.json`. Dili gyud ni mawala bisan i-close ninyo ang app.
* **Live Currency Converter:** Naa ni built-in na converter (e.g., USD to PHP) na naggamit og **API** para updated ang rates.
* **Daily Quotes:** Pag-abri ninyo sa app, naa dayon mogawas na random motivational quote gikan sa ZenQuotes API.
* **Transaction History:** Makita ninyo ang history sa tanang transactions, naka-color-code (Green para sa kita, Red para sa gasto).

---

## 📂 Project Structure (Ang mga Files)

Gi-separate gyud namo ang code para dili mag-gukod-gukod ang code (MVC Approach):

1.  **`main.py`** - Ang *Entry Point*. Ang una gyud na i-run.
2.  **`ui.py` (View)** - Ang itsura ug tanang widgets (Buttons, Labels, Window).
3.  **`logic.py` (Controller/Logic)** - Ang utok sa app. Dinhi naggikan ang API calls ug ang computation sa kwarta.
4.  **`data_handler.py` (Data)** - Ang module na tig-save ug tig-load sa data gikan sa JSON file.
5.  **`transaction.py` (Model)** - Ang porma sa data, ang blueprint sa usa ka transaction.

---

## 🛠️ Mga Kinahanglanon (Requirements)

Kinahanglan jud naa moy **Python 3.x** na naka-install ug kailangan pud og internet.

I-install lang ni na library para sa API:

```bash
pip install requests