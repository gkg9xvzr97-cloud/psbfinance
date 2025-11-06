import yfinance as yf

# Fetch 5 years of historical data for Apple (AAPL)
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="5y")  # DataFrame with Open, High, Low, Close, Volume
# Example: fetch fundamental info
financials = ticker.financials   # Income statement
actions = ticker.actions         # Dividends, splits
print(hist.head())
from xbbg import blp
from datetime import datetime, timedelta

# Set date range for 1 year back
start_date = (datetime.today() - timedelta(days=365)).strftime('%Y%m%d')
# Fetch dividend history for Apple from Bloomberg (Bloomberg DAPI)
df = blp.bds('AAPL US Equity', 'DVD_HIST', DVD_START_DT=start_date)
print(df.head())
import numpy as np

# Example projected free cash flows (in millions)
cash_flows = np.array([500, 550, 605, 665, 732])  # 5-year forecast
WACC = 0.10      # Weighted Average Cost of Capital (10%)
TGR = 0.02       # Terminal Growth Rate (2%)

# Compute present value of each FCF
pv_fcf = [cf/(1+WACC)**(i+1) for i, cf in enumerate(cash_flows)]
# Terminal value at end of last year
terminal_value = cash_flows[-1] * (1 + TGR) / (WACC - TGR)
pv_terminal = terminal_value / (1+WACC)**len(cash_flows)

enterprise_value = sum(pv_fcf) + pv_terminal
cash = 1000      # e.g. company cash on hand
debt = 500       # e.g. company total debt
equity_value = enterprise_value - debt + cash
shares_outstanding = 100  # in millions
implied_price = equity_value / shares_outstanding

print(f"Implied Share Price (DCF): ${implied_price:.2f}")
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

# Assume hist from yfinance contains a 'Close' column indexed by date
ts = pd.Series(hist['Close'].values, index=hist.index)
result = seasonal_decompose(ts, model='additive', period=252)  # e.g. yearly seasonality (252 trading days)
trend = result.trend
seasonal = result.seasonal
resid = result.resid

# Plot decomposition
plt.figure(figsize=(10,6))
plt.subplot(3,1,1); plt.plot(trend, label='Trend'); plt.legend()
plt.subplot(3,1,2); plt.plot(seasonal, label='Seasonal'); plt.legend()
plt.subplot(3,1,3); plt.plot(resid, label='Residual'); plt.legend()
plt.tight_layout()
plt.show()
import pdfplumber

# Extract text from a PDF file (e.g., an earnings report)
pdf_path = "report.pdf"
all_text = ""
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            all_text += text + "\n"

print(all_text[:200])  # preview
import openai
openai.api_key = "YOUR_OPENAI_API_KEY"

prompt = f"Summarize this financial report:\n{all_text}"
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.5
)
summary = response.choices[0].message.content.strip()
print("AI Summary:\n", summary)
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance_app.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database model for users
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route: User signup
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'], method='sha256')
        new_user = User(username=request.form['username'], password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

# Route: User login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# Protected dashboard page
@app.route('/dashboard')
@login_required
def dashboard():
    # Render main app interface (charts, data, summaries, etc.)
    return render_template('dashboard.html', name=current_user.username)

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    db.create_all()  # create DB tables
    app.run(debug=True)
