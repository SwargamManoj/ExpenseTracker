from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

app = Flask(__name__)

try:
    expenses = pd.read_csv('expenses.csv')
except FileNotFoundError:
    expenses = pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount'])

CATEGORIES = ["Food", "Transport", "Entertainment", "Health", "Bills", "Education", "Shopping", "Other"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        category = request.form['category']
        description = request.form['description']
        amount = request.form['amount']
        date = datetime.now().strftime('%Y-%m-%d')
        new_expense = pd.DataFrame([[date, category, description, float(amount)]], 
                                   columns=['Date', 'Category', 'Description', 'Amount'])
        global expenses
        expenses = pd.concat([expenses, new_expense], ignore_index=True)
        expenses.to_csv('expenses.csv', index=False)
        return redirect(url_for('index'))
    return render_template('add.html', categories=CATEGORIES)

@app.route('/view')
def view_expenses():
    expenses_list = expenses.to_dict('records')  # Convert DataFrame to a list of dictionaries for easier template rendering
    total_expenses = expenses['Amount'].sum()  # Calculate total expenses
    return render_template('view.html', expenses=expenses_list, total_expenses=total_expenses)

@app.route('/analyze')
def analyze_expenses():
    category_data = expenses.groupby('Category')['Amount'].sum()
    category_data.plot(kind='pie', title='Expenses by Category', autopct='%1.1f%%')
    plt.ylabel('')
    plt.savefig('static/analysis.png')
    plt.close()
    return render_template('analyse.html')

@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    global expenses  # Use the global DataFrame
    if expense_id in expenses.index:
        expenses = expenses.drop(expense_id)  # Drop the row with the specified index
        expenses.reset_index(drop=True, inplace=True)  # Reset index after deletion to avoid gaps
    return redirect(url_for('view_expenses'))


if __name__ == '__main__':
    app.run(debug=True)
