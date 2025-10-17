import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import joblib
import os
from collections import Counter

class MLPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.confidence_threshold = 0.6  # Minimum confidence for strong signals
        self.load_or_train_model()

    def load_or_train_model(self):
        """
        Load existing model or train a new one if not found.
        """
        model_path = 'trading_model.pkl'
        scaler_path = 'trading_scaler.pkl'
        features_path = 'trading_features.pkl'

        if os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(features_path):
            try:
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.feature_names = joblib.load(features_path)
                print("Model, scaler, and features loaded successfully.")
            except Exception as e:
                print(f"Error loading model: {e}")
                self.train_model()
        else:
            print("Model files incomplete, training new model...")
            self.train_model()

    def train_model(self):
        """
        Train enhanced ML model with advanced features and ensemble methods.
        """
        # Generate more sophisticated synthetic trading data
        np.random.seed(42)
        n_samples = 100000  # Increased sample size for better accuracy

        # Enhanced features including trend strength, volatility, momentum
        features = {
            'rsi': np.random.uniform(10, 90, n_samples),
            'macd': np.random.normal(0, 2, n_samples),
            'macd_signal': np.random.normal(0, 1.5, n_samples),
            'sma': np.random.uniform(30, 300, n_samples),
            'ema': np.random.uniform(30, 300, n_samples),
            'volume': np.random.uniform(1000, 500000, n_samples),
            'bb_upper': np.random.uniform(80, 400, n_samples),
            'bb_lower': np.random.uniform(20, 200, n_samples),
            'bb_middle': np.random.uniform(50, 300, n_samples),
            'stoch_k': np.random.uniform(10, 90, n_samples),
            'stoch_d': np.random.uniform(10, 90, n_samples),
            'adx': np.random.uniform(10, 50, n_samples),  # Trend strength
            'cci': np.random.normal(0, 100, n_samples),  # Commodity Channel Index
            'williams_r': np.random.uniform(-100, 0, n_samples),  # Williams %R
            'mfi': np.random.uniform(10, 90, n_samples),  # Money Flow Index
            'roc': np.random.normal(0, 5, n_samples),  # Rate of Change
            'volatility': np.random.uniform(0.5, 5.0, n_samples),  # Price volatility
            'trend_strength': np.random.uniform(0, 1, n_samples),  # Trend strength indicator
            'momentum': np.random.normal(0, 10, n_samples),  # Momentum indicator
        }

        df = pd.DataFrame(features)

        # Enhanced target logic with multiple conditions for higher accuracy
        buy_conditions = (
            (df['rsi'] < 35) & (df['macd'] > df['macd_signal']) & (df['trend_strength'] > 0.6) & (df['momentum'] > 1) |
            (df['stoch_k'] < 25) & (df['stoch_d'] < 25) & (df['momentum'] > 2) & (df['volatility'] < 2.0) |
            (df['cci'] < -100) & (df['williams_r'] < -80) & (df['adx'] > 25) |
            (df['mfi'] < 30) & (df['volume'] > df['volume'].quantile(0.8)) & (df['roc'] > 1) |
            (df['rsi'] < 30) & (df['bb_middle'] > df['sma']) & (df['trend_strength'] > 0.7)
        )

        sell_conditions = (
            (df['rsi'] > 65) & (df['macd'] < df['macd_signal']) & (df['trend_strength'] < 0.4) & (df['momentum'] < -1) |
            (df['stoch_k'] > 75) & (df['stoch_d'] > 75) & (df['momentum'] < -2) & (df['volatility'] < 2.0) |
            (df['cci'] > 100) & (df['williams_r'] > -20) & (df['adx'] > 25) |
            (df['mfi'] > 70) & (df['volume'] > df['volume'].quantile(0.8)) & (df['roc'] < -1) |
            (df['rsi'] > 70) & (df['bb_middle'] < df['sma']) & (df['trend_strength'] < 0.3)
        )

        df['target'] = 0  # Hold by default
        df.loc[buy_conditions, 'target'] = 1   # Buy
        df.loc[sell_conditions, 'target'] = -1  # Sell

        # Split data
        X = df.drop('target', axis=1)
        y = df['target']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Create ensemble model with multiple algorithms for higher accuracy
        rf = RandomForestClassifier(n_estimators=300, max_depth=15, random_state=42, class_weight='balanced')

        # Train ensemble
        self.model = rf
        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Enhanced Model Accuracy: {accuracy:.4f}")
        print("Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['Sell', 'Hold', 'Buy']))

        # Save model and scaler
        joblib.dump(self.model, 'trading_model.pkl')
        joblib.dump(self.scaler, 'trading_scaler.pkl')
        joblib.dump(list(X.columns), 'trading_features.pkl')
        self.feature_names = list(X.columns)

    def predict(self, indicators_dict):
        """
        Enhanced prediction with confidence scoring and trend analysis.
        """
        if self.model is None:
            return 'hold'

        # If feature_names is None, use basic prediction
        if self.feature_names is None:
            # Simple rule-based prediction as fallback
            rsi = indicators_dict.get('rsi', 50)
            macd = indicators_dict.get('macd', 0)
            if rsi < 30 and macd > 0:
                return 'buy'
            elif rsi > 70 and macd < 0:
                return 'sell'
            else:
                return 'hold'

        # Prepare input data with enhanced features
        enhanced_indicators = self._enhance_indicators(indicators_dict)
        input_data = pd.DataFrame([enhanced_indicators])

        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in input_data.columns:
                input_data[feature] = 0  # Default value

        # Reorder columns to match training data
        input_data = input_data[self.feature_names]

        # Scale input
        if self.scaler:
            input_data_scaled = self.scaler.transform(input_data)
        else:
            input_data_scaled = input_data.values

        # Get prediction probabilities for confidence
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(input_data_scaled)[0]
            confidence = max(probabilities)

            # Get prediction
            prediction = self.model.predict(input_data_scaled)[0]

            # Apply confidence threshold
            if confidence < self.confidence_threshold:
                return 'hold'  # Not confident enough

            if prediction == 1:
                return 'buy'
            elif prediction == -1:
                return 'sell'
            else:
                return 'hold'
        else:
            # Fallback for models without predict_proba
            prediction = self.model.predict(input_data_scaled)[0]
            if prediction == 1:
                return 'buy'
            elif prediction == -1:
                return 'sell'
            else:
                return 'hold'

    def _enhance_indicators(self, indicators_dict):
        """
        Enhance indicators with additional calculated features and trend analysis.
        """
        enhanced = indicators_dict.copy()

        # Add default values for missing indicators
        defaults = {
            'macd_signal': enhanced.get('macd', 0) * 0.8,  # Approximate signal line
            'bb_middle': (enhanced.get('bb_upper', 0) + enhanced.get('bb_lower', 0)) / 2,
            'adx': 25,  # Default trend strength
            'cci': 0,   # Default CCI
            'williams_r': -50,  # Default Williams %R
            'mfi': 50,  # Default MFI
            'roc': 0,   # Default ROC
            'volatility': 2.0,  # Default volatility
            'trend_strength': 0.5,  # Default trend strength
            'momentum': enhanced.get('macd', 0),  # Use MACD as momentum proxy
        }

        for key, value in defaults.items():
            if key not in enhanced:
                enhanced[key] = value

        # Calculate additional features if possible
        if 'bb_upper' in enhanced and 'bb_lower' in enhanced and 'sma' in enhanced:
            # Bollinger Band position
            bb_range = enhanced['bb_upper'] - enhanced['bb_lower']
            if bb_range > 0:
                bb_position = (enhanced['sma'] - enhanced['bb_lower']) / bb_range
                enhanced['bb_position'] = bb_position

        # Advanced trend analysis features
        rsi = enhanced.get('rsi', 50)
        macd = enhanced.get('macd', 0)
        macd_signal = enhanced.get('macd_signal', 0)
        volume = enhanced.get('volume', 100000)
        volatility = enhanced.get('volatility', 2.0)

        # Trend strength calculation
        trend_indicators = []
        if abs(macd - macd_signal) > volatility * 0.1:
            trend_indicators.append(1)
        if rsi > 60 or rsi < 40:
            trend_indicators.append(1)
        if volume > 200000:  # High volume
            trend_indicators.append(1)

        enhanced['trend_strength'] = min(1.0, len(trend_indicators) / 3.0)

        # Momentum calculation
        momentum_signals = 0
        if macd > macd_signal:
            momentum_signals += 1
        if rsi > 50:
            momentum_signals += 1
        if enhanced.get('roc', 0) > 0:
            momentum_signals += 1

        enhanced['momentum_score'] = momentum_signals / 3.0

        # Market regime detection
        if volatility > 3.0 and volume > 300000:
            enhanced['market_regime'] = 'volatile_high_volume'
        elif volatility < 1.5 and volume < 150000:
            enhanced['market_regime'] = 'calm_low_volume'
        else:
            enhanced['market_regime'] = 'normal'

        return enhanced

    def get_prediction_confidence(self, indicators_dict):
        """
        Get prediction confidence score.
        """
        if self.model is None or not hasattr(self.model, 'predict_proba'):
            return 0.5

        enhanced_indicators = self._enhance_indicators(indicators_dict)
        input_data = pd.DataFrame([enhanced_indicators])

        for feature in self.feature_names:
            if feature not in input_data.columns:
                input_data[feature] = 0

        input_data = input_data[self.feature_names]

        if self.scaler:
            input_data_scaled = self.scaler.transform(input_data)
        else:
            input_data_scaled = input_data.values

        probabilities = self.model.predict_proba(input_data_scaled)[0]
        return max(probabilities)

# Lazy global predictor instance to avoid heavy work at import time
predictor = None

def get_predictor():
    """
    Return a singleton MLPredictor instance. Initialize lazily and handle
    initialization errors gracefully so importing this module won't crash
    the app during deploy.
    """
    global predictor
    if predictor is None:
        try:
            predictor = MLPredictor()
        except Exception as e:
            # Log the error and keep predictor None. The app can continue
            # and fall back to rule-based logic when predictor is unavailable.
            print(f"Error initializing MLPredictor: {e}")
            predictor = None
    return predictor
