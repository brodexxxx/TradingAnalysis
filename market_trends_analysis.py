import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import yfinance as yf
from datetime import datetime, timedelta

# Fetch data from Yahoo Finance for past 6 years
def fetch_data(symbol, years=6):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365)
    data = yf.download(symbol, start=start_date, end=end_date, interval='1d')
    return data

# Load datasets
sensex = fetch_data('^BSESN')
banknifty = fetch_data('^NSEBANK')
vix = fetch_data('^INDIAVIX')
crude = fetch_data('CL=F')
nifty = fetch_data('^NSEI')

# Plot trends
def plot_trend(df, title, col='Close'):
    plt.figure(figsize=(10,5))
    plt.plot(df.index, df[col], label=title)
    plt.title(title + " Trend (Past 6 Years)")
    plt.xlabel("Year")
    plt.ylabel("Index Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{title}.png")
    plt.close()

for name, data in zip(["Sensex", "Bank Nifty", "India VIX", "Crude Oil", "Nifty50"],
                      [sensex, banknifty, vix, crude, nifty]):
    plot_trend(data, name)

# Combine into a single PDF
pdf = FPDF()
for chart in ["Sensex", "Bank Nifty", "India VIX", "Crude Oil", "Nifty50"]:
    pdf.add_page()
    pdf.image(f"{chart}.png", x=10, y=20, w=180)
pdf.output("Market_Trends_Analysis.pdf")
