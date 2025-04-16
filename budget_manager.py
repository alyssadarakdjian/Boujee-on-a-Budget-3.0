import json
import os
from datetime import datetime
import re
import time
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

class BudgetManager:
    def __init__(self, data_file="data/transactions.json"):
        self.data_file = data_file
        self.transactions = []
        self.budget_limit = 0
        self.categories = ["Food", "Rent", "Transport", "Entertainment", "Utilities", "Other"]

        # Ensure data folder exists
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                data = json.load(f)
                self.transactions = data.get("transactions", [])
                self.budget_limit = data.get("budget_limit", 0)

    def save(self):
        with open(self.data_file, "w") as f:
            json.dump({
                "transactions": self.transactions,
                "budget_limit": self.budget_limit
            }, f, indent=4)

    def reset(self):
        self.transactions = []
        self.budget_limit = 0
        self.save()

    def set_budget(self, amount):
        self.budget_limit = amount
        self.save()

    def log_expense(self, user_input, category):
        amount_match = re.search(r"-?\$?(\d+(\.\d{1,2})?)", user_input)
        if not amount_match:
            return "Could not understand the expense amount."

        amount = float(amount_match.group(1))
    
    # Prevent negative expenses
        if "-" in user_input or amount <= 0:
            return "Expense amount must be a positive number."

        expense = {
            "amount": amount,
            "category": category.lower(),
            "description": user_input,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.transactions.append(expense)
        self.save()

        return f"Logged: ${amount:.2f} for '{category}'."


    def get_summary(self):
        summary = {}
        total_spent = 0.0
        for t in self.transactions:
            total_spent += t["amount"]
            summary[t["category"]] = summary.get(t["category"], 0) + t["amount"]

        report = [f"💸 Total Spent: ${total_spent:.2f}"]

        for cat, amt in summary.items():
            report.append(f" - {cat.title()}: ${amt:.2f}")

        if self.budget_limit:
            remaining = self.budget_limit - total_spent
            report.append(f"🎯 Budget Limit: ${self.budget_limit:.2f}")
            report.append(f"✅ Remaining Budget: ${remaining:.2f}")
            if remaining < 0:
                report.append("⚠️ You have exceeded your budget!")

        return "\n".join(report)

    def get_expenses_log(self):
        if not self.transactions:
            return "No expenses recorded yet."
        return "\n".join(
            [f"[{t['date']}] ${t['amount']:.2f} - {t['category'].title()}\n  -> {t['description']}"
             for t in self.transactions]
        )

    def import_csv(self, file_path):
        try:
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                expense = {
                    "amount": float(row["amount"]),
                    "category": row["category"],
                    "description": row.get("description", ""),
                    "date": row.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                }
                self.transactions.append(expense)

            self.save()
            return f"Imported {len(df)} records successfully!"

        except Exception as e:
            return f"Error importing CSV: {e}"

    def cluster_expenses(self):
        if not self.transactions:
            return "No expenses to cluster."

        df = pd.DataFrame(self.transactions)

        if df.shape[0] < 2:
            return "Not enough data to perform clustering."

        X = df[['amount']]
        kmeans = KMeans(n_clusters=3, random_state=42)
        df['cluster'] = kmeans.fit_predict(X)

        cluster_summary = df.groupby('cluster')['amount'].agg(['count', 'sum']).reset_index()

        result = "Expense Clusters:\n"
        for _, row in cluster_summary.iterrows():
            result += f"Cluster {int(row['cluster'])}: {row['count']} expenses, Total: ${row['sum']:.2f}\n"

        return result

    def plot_expenses(self):
        if not self.transactions:
            return None

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        os.makedirs("plots", exist_ok=True)

        df = pd.DataFrame(self.transactions)
        category_summary = df.groupby('category')['amount'].sum()

        plt.figure(figsize=(8, 6))
        bars = category_summary.plot(kind='bar', color='pink', edgecolor='black')
        plt.title('Spending by Category', fontsize=16, color='hotpink')
        plt.xlabel('Category', fontsize=12, color='deeppink')
        plt.ylabel('Total Spent ($)', fontsize=12, color='deeppink')
        plt.xticks(rotation=45, color='black')
        plt.yticks(color='black')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        for p in bars.patches:
            plt.annotate(f"${p.get_height():.2f}",
                         (p.get_x() + p.get_width() / 2., p.get_height()),
                         ha='center', va='bottom', fontsize=10, color='black')

        plt.tight_layout()
        plot_path = f"plots/spending_plot_{timestamp}.png"
        plt.savefig(plot_path)
        plt.close()

        return plot_path

    def plot_clusters(self):
        if not self.transactions:
            return None

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        os.makedirs("plots", exist_ok=True)

        df = pd.DataFrame(self.transactions)

        if df.shape[0] < 2:
            return None

        X = df[['amount']]
        kmeans = KMeans(n_clusters=3, random_state=42)
        df['cluster'] = kmeans.fit_predict(X)

        plt.figure(figsize=(8, 6))
        colors = ['hotpink', 'deeppink', 'lightpink']
        for cluster in df['cluster'].unique():
            cluster_data = df[df['cluster'] == cluster]
            plt.scatter(
                cluster_data.index,
                cluster_data['amount'],
                label=f'Cluster {cluster}',
                color=colors[cluster],
                edgecolor='black',
                s=80,
                alpha=0.7
            )

        plt.title('Expense Clusters (by Amount)', fontsize=16, color='hotpink')
        plt.xlabel('Transaction Index', fontsize=12, color='deeppink')
        plt.ylabel('Amount Spent ($)', fontsize=12, color='deeppink')
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        cluster_plot_path = f"plots/cluster_plot_{timestamp}.png"
        plt.savefig(cluster_plot_path)
        plt.close()

        return cluster_plot_path

    def export_to_excel(self):
        if not self.transactions:
            return "No transactions to export."

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        os.makedirs("plots", exist_ok=True)

        df = pd.DataFrame(self.transactions)

        summary_df = df.groupby('category')['amount'].sum().reset_index()
        summary_df.columns = ['Category', 'Total Spent']

        X = df[['amount']]
        if df.shape[0] >= 2:
            kmeans = KMeans(n_clusters=3, random_state=42)
            df['cluster'] = kmeans.fit_predict(X)
            cluster_df = df[['amount', 'category', 'cluster', 'description', 'date']]
        else:
            cluster_df = df.copy()
            cluster_df['cluster'] = 'N/A'

        excel_path = f"plots/budget_report_{timestamp}.xlsx"
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            summary_df.to_excel(writer, sheet_name='Spending Summary', index=False)
            cluster_df.to_excel(writer, sheet_name='Cluster Assignments', index=False)

        return excel_path
    
    
    