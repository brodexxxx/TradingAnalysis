import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pandas_ta as ta
import yfinance as yf
from datetime import datetime, timedelta

class StockTrendPredictor:
    def __init__(self, symbol):
        self.symbol = symbol
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)

    def fetch_data(self, years=2):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)
        data = yf.download(self.symbol, start=start_date, end=end_date)
        return data

    def prepare_features(self, data):
        # Calculate technical indicators
        data['SMA_20'] = ta.sma(data['Close'], length=20)
        data['SMA_50'] = ta.sma(data['Close'], length=50)
        data['RSI'] = ta.rsi(data['Close'], length=14)
        data['MACD'] = ta.macd(data['Close'])['MACD_12_26_9']
        data['BB_upper'] = ta.bbands(data['Close'])['BBU_20_2.0']
        data['BB_lower'] = ta.bbands(data['Close'])['BBL_20_2.0']

        # Create target: next day trend (1 for up, 0 for down)
        data['Next_Close'] = data['Close'].shift(-1)
        data['Trend'] = (data['Next_Close'] > data['Close']).astype(int)

        # Drop NaN values
        data = data.dropna()

        # Features
        features = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_20', 'SMA_50', 'RSI', 'MACD', 'BB_upper', 'BB_lower']
        X = data[features]
        y = data['Trend']

        return X, y

    def train_model(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model Accuracy: {accuracy:.2f}")
        print(classification_report(y_test, y_pred))

        return accuracy

    def predict_next_day(self, data):
        # Get latest data
        latest = data.iloc[-1]
        features = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_20', 'SMA_50', 'RSI', 'MACD', 'BB_upper', 'BB_lower']
        X_latest = latest[features].values.reshape(1, -1)

        prediction = self.model.predict(X_latest)[0]
        confidence = max(self.model.predict_proba(X_latest)[0])

        trend = "Up" if prediction == 1 else "Down"
        return trend, confidence

    def run(self):
        data = self.fetch_data()
        X, y = self.prepare_features(data)
        accuracy = self.train_model(X, y)
        trend, confidence = self.predict_next_day(data)
        return {
            'symbol': self.symbol,
            'predicted_trend': trend,
            'confidence': confidence,
            'model_accuracy': accuracy
        }
