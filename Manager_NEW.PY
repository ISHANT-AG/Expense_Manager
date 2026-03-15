import json
import os
import csv
import datetime

class ExpenseManager:
    def __init__(self, filename="expense_data_final.json"):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        default_data = {
            "wallet_balance": 0.0,      
            "investments": {            
                "Axis Liquid Fund": 0.0,
                "HDFC Flexi Cap": 0.0,
                "Small Cap Fund": 0.0,
            }, 
            "pending_income": [], 
            "transactions": [], 
            "assets": [],       
            "liabilities": []   
        }
        
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                try:
                    loaded_data = json.load(file)
                    for key in default_data:
                        if key not in loaded_data:
                            loaded_data[key] = default_data[key]
                    return loaded_data
                except:
                    return default_data
        else:
            return default_data

    def save_data(self):
        with open(self.filename, 'w') as file:
            json.dump(self.data, file, indent=4)

    # --- CORE FUNCTIONS ---
    def add_transaction(self, amount, category, t_type):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if t_type == "income":
            self.data["wallet_balance"] += amount
        elif t_type == "expense":
            self.data["wallet_balance"] -= amount

        transaction = {
            "date": timestamp,
            "type": t_type,
            "amount": amount,
            "category": category
        }
        self.data["transactions"].append(transaction)
        self.save_data()
        print(f"\n✅ Recorded {t_type}: ₹{amount} ({category})")

    # --- PENDING INCOME ---
    def add_pending_income(self, source, amount):
        entry = {"source": source, "amount": amount, "date": datetime.datetime.now().strftime("%Y-%m-%d")}
        self.data["pending_income"].append(entry)
        self.save_data()
        print(f"\n⏳ Added to Pending: ₹{amount} from {source}. (Wallet not changed)")

    def claim_pending_income(self):
        if not self.data["pending_income"]:
            print("\n🤷‍♂️ No pending payments.")
            return

        print("\n--- ⏳ PENDING PAYMENTS ---")
        for i, item in enumerate(self.data["pending_income"], 1):
            print(f"{i}. {item['source']} | ₹{item['amount']} | Due since: {item['date']}")
        
        try:
            choice = int(input("\nSelect Payment Source (0 to cancel): "))
            if choice == 0: return
            
            if 1 <= choice <= len(self.data["pending_income"]):
                index = choice - 1
                item = self.data["pending_income"][index]
                
                print(f"\nTotal Due from {item['source']}: ₹{item['amount']}")
                received = float(input("Enter Amount Received: "))

                if received <= 0:
                    print("❌ Amount must be positive.")
                    return

                if received >= item['amount']:
                    actual_amt = item['amount']
                    self.data["pending_income"].pop(index) 
                    print(f"🎉 Full payment cleared for {item['source']}!")
                else:
                    actual_amt = received
                    item['amount'] -= actual_amt 
                    print(f"✅ Partial payment accepted. Remaining Due: ₹{item['amount']}")

                self.add_transaction(actual_amt, f"Received: {item['source']}", "income")
            else:
                print("❌ Invalid selection.")
        except ValueError: print("❌ Invalid input.")

    # --- INVESTMENTS (BUY & SELL FIXED) ---
    def invest_money(self, fund_name, amount):
        if amount > self.data["wallet_balance"]:
            print(f"\n❌ Error: Not enough money in Wallet (Avail: ₹{self.data['wallet_balance']})")
            return

        # Double withdrawal fix: Let add_transaction handle the wallet subtraction
        if fund_name not in self.data["investments"]:
            self.data["investments"][fund_name] = 0.0
        self.data["investments"][fund_name] += amount

        self.add_transaction(amount, f"Invested in {fund_name}", "expense") 
        print(f"\n🚀 Success! Transferred ₹{amount} from Wallet to {fund_name}.")

    def sell_investment(self, fund_name, amount):
        if fund_name not in self.data["investments"]:
            print(f"❌ Error: You don't have a fund named '{fund_name}'.")
            return
        
        current_val = self.data["investments"][fund_name]
        if amount > current_val:
            print(f"❌ Error: You only have ₹{current_val} in {fund_name}.")
            return

        # Double deposit fix: Let add_transaction handle the wallet addition
        self.data["investments"][fund_name] -= amount
        
        if self.data["investments"][fund_name] == 0:
            del self.data["investments"][fund_name]

        self.add_transaction(amount, f"Sold/Redeemed: {fund_name}", "income")
        print(f"\n💵 Success! Redeemed ₹{amount} from {fund_name} to Wallet.")

    def view_portfolio(self):
        print("\n" + "="*40)
        print(" 📈 YOUR INVESTMENT PORTFOLIO")
        print("="*40)
        total_inv = 0
        print(f"{'Fund Name':<25} | {'Invested Value'}")
        print("-" * 40)
        for fund, amount in self.data["investments"].items():
            print(f"{fund:<25} | ₹ {amount:,.2f}")
            total_inv += amount
        print("-" * 40)
        return total_inv

    # --- NET WORTH ---
    def show_net_worth(self):
        wallet = self.data['wallet_balance']
        investments = sum(self.data['investments'].values())
        lending = sum(p['amount'] for p in self.data['assets'])
        pending_inc = sum(p['amount'] for p in self.data['pending_income'])
        borrowing = sum(p['amount'] for p in self.data['liabilities'])
        
        net_worth = wallet + investments + lending - borrowing

        print("\n" + "="*40)
        print(" 💎 FINAL NET WORTH BREAKDOWN")
        print("="*40)
        print(f"💵 Wallet (Liquid Cash):   ₹ {wallet:,.2f}")
        print(f"📈 Investments (Assets):   ₹ {investments:,.2f}")
        print(f"🤝 Money Lended (Assets):  ₹ {lending:,.2f}")
        print(f"💳 Money Borrowed (Liab):  ₹ {borrowing:,.2f}")
        print("-" * 40)
        print(f"✅ TOTAL ACTUAL WEALTH:    ₹ {net_worth:,.2f}")
        print(f"⏳ (In Pipeline: ₹{pending_inc:,.2f} Expected)")
        print("="*40)

    # --- LENDING ---
    def lend_money(self, name, amount):
        self.add_transaction(amount, f"Lent to {name}", "expense")
        self.data["assets"].append({"name": name, "amount": amount, "date": datetime.datetime.now().strftime("%Y-%m-%d")})
        self.save_data()

    def receive_repayment(self, name, amount):
        found = False
        for person in self.data["assets"]:
            if person["name"].lower() == name.lower():
                if amount > person["amount"]:
                    print(f"❌ Error: They only owe you ₹{person['amount']}.")
                    return
                
                self.add_transaction(amount, f"Repayment from {name}", "income")
                person["amount"] -= amount
                
                if person["amount"] <= 0:
                    self.data["assets"].remove(person)
                    print(f"🎉 {name} has fully paid you back!")
                else:
                    print(f"✅ Balance updated. They still owe ₹{person['amount']}.")
                
                self.save_data()
                return
        if not found: print(f"❌ Error: {name} is not in your lending list.")

    # --- BORROWING ---
    def borrow_money(self, name, amount):
        self.add_transaction(amount, f"Borrowed from {name}", "income")
        self.data["liabilities"].append({"name": name, "amount": amount})
        self.save_data()
    
    def return_money(self, name, amount):
        found = False
        for person in self.data["liabilities"]:
            if person["name"].lower() == name.lower():
                if amount > person["amount"]:
                    print(f"❌ Error: You only owe {name} ₹{person['amount']}.")
                    return
                
                self.add_transaction(amount, f"Returned to {name}", "expense")
                person["amount"] -= amount
                
                if person["amount"] <= 0:
                    self.data["liabilities"].remove(person)
                    print(f"🎉 Great! You have paid off {name}.")
                else:
                    print(f"✅ Payment recorded. You still owe {name} ₹{person['amount']}.")
                
                self.save_data()
                return
        if not found: print(f"❌ Error: You don't have a record of owing {name}.")

    def view_history(self):
        print("\n" + "="*40)
        print(" 📜 TRANSACTION HISTORY")
        print("="*40)
        for t in self.data['transactions']:
            print(f"{t['date'][0:10]} | {t['type'].upper():<10} | {t['category']:<20} | ₹{t['amount']}")

    def export_to_csv(self):
        if not self.data['transactions']:
            print("⚠️ No data to export.")
            return
        filename = "expense_report.csv"
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Type", "Category", "Amount (₹)"])
                for t in self.data['transactions']:
                    writer.writerow([t['date'], t['type'].upper(), t['category'], t['amount']])
            print(f"\n✅ Data successfully exported to '{filename}'")
        except PermissionError:
            print(f"\n❌ Error: Please close '{filename}' if it is open and try again.")

    # --- RESET DATA (FIXED TO KEEP INVESTMENTS) ---
    def reset_data(self):
        confirm = input("\n⚠️  ARE YOU SURE? This will clear monthly expenses but keep your investments safe. (type 'yes'): ")
        if confirm.lower() == 'yes':
            # Save the current investments before wiping
            safe_investments = self.data.get("investments", {})
            
            self.data = {
                "wallet_balance": 0.0, 
                "investments": safe_investments, # Restoring untouched investments
                "pending_income": [], 
                "transactions": [], 
                "assets": [], 
                "liabilities": []
            }
            self.save_data()
            print("\n♻️  Monthly Data Reset. Your investments remain untouched.")
        else:
            print("\n❌ Cancelled.")

def main():
    manager = ExpenseManager()
    while True:
        print("\n" + "="*35)
        print(" 💰 ISHANT'S FINANCE MANAGER")
        print("="*35)
        
        print(f"💵 Wallet: ₹{manager.data['wallet_balance']:,.2f}")
        if manager.data['pending_income']:
            print(f"⏳ Pending: ₹{sum(i['amount'] for i in manager.data['pending_income']):,.2f}")
        print("-" * 35)

        print("1. ➕ Add Income")
        print("2. ➖ Add Expense")
        print("3. 📈 INVESTMENTS (Buy/Sell)") 
        print("4. ⏳ PENDING INCOME")
        print("5. 📊 Portfolio & Net Worth")
        print("6. 📜 History")
        print("7. 🟢 LENDING (Give/Receive)") 
        print("8. 🔴 BORROWING (Take/Return)") 
        print("9. 📤 Export Data")
        print("10. ♻️  RESET")
        print("11. ❌ Exit")
        
        choice = input("\nOption: ")

        if choice == '1': manager.add_transaction(float(input("Amount: ")), input("Source: "), "income")
        elif choice == '2': manager.add_transaction(float(input("Amount: ")), input("Category: "), "expense")
        elif choice == '3':
            print("\n--- 📈 INVESTMENT MANAGER ---")
            print("1. ➕ Invest Money (Buy)")
            print("2. ➖ Sell Investment (Redeem)")
            sub = input("Select: ")
            funds = list(manager.data["investments"].keys())
            if sub == '1':
                print("\nSelect Fund:")
                for i, f in enumerate(funds, 1): print(f"{i}. {f}")
                print(f"{len(funds) + 1}. ➕ Add New Fund")
                try:
                    sel = int(input("Select: "))
                    if 1 <= sel <= len(funds): fund_name = funds[sel-1]
                    elif sel == len(funds) + 1: fund_name = input("Enter New Fund Name: ").strip()
                    else: print("❌ Invalid."); continue
                    if fund_name:
                        manager.invest_money(fund_name, float(input(f"Amount: ")))
                except ValueError: print("❌ Invalid Input.")
            elif sub == '2':
                print("\nSelect Fund to SELL:")
                for i, f in enumerate(funds, 1): print(f"{i}. {f} (₹{manager.data['investments'][f]})")
                try:
                    sel = int(input("Select: "))
                    if 1 <= sel <= len(funds):
                        manager.sell_investment(funds[sel-1], float(input(f"Amount: ")))
                except ValueError: print("❌ Invalid Input.")

        elif choice == '4':
            if input("1. Add Due | 2. Receive: ") == '1':
                manager.add_pending_income(input("Who owes you? "), float(input("Amount: ")))
            else: manager.claim_pending_income()
        elif choice == '5': 
            manager.view_portfolio()
            manager.show_net_worth()
        elif choice == '6': manager.view_history()
        elif choice == '7':
            print("\n--- 🟢 LENDING MANAGER ---")
            print("1. Lend Money (Give)")
            print("2. Receive Repayment (Get Back)")
            sub = input("Select: ")
            if sub == '1': manager.lend_money(input("Name: "), float(input("Amount: ")))
            elif sub == '2':
                for p in manager.data['assets']: print(f" - {p['name']}: ₹{p['amount']}")
                manager.receive_repayment(input("Who paid? "), float(input("Amount: ")))
        elif choice == '8':
            print("\n--- 🔴 BORROWING MANAGER ---")
            print("1. Borrow Money (Take)")
            print("2. Return Money (Pay Back)")
            sub = input("Select: ")
            if sub == '1': manager.borrow_money(input("Name: "), float(input("Amount: ")))
            elif sub == '2':
                for p in manager.data['liabilities']: print(f" - {p['name']}: ₹{p['amount']}")
                manager.return_money(input("Who are you paying? "), float(input("Amount: ")))
        elif choice == '9': manager.export_to_csv()
        elif choice == '10': manager.reset_data()
        elif choice == '11': break

if __name__ == "__main__":
    main()