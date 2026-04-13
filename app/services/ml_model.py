from sklearn.linear_model import LinearRegression
import numpy as np


def train_model(history):
    if len(history) < 3:
        return None

    prices = []
    profits = []

    for p in history:
        if p.competitor and p.price:
            prices.append([p.price])
            profit = p.price - (p.price * 0.9)  # assume competitor 10% less
            profits.append(profit)

    if len(prices) < 3:
        return None

    model = LinearRegression()
    model.fit(prices, profits)

    return model


def predict_profit(model, price):
    if model is None:
        return None

    predicted = model.predict([[price]])
    return round(predicted[0], 2)