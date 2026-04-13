def analyze_prices(history):
    if not history or len(history) < 2:
        return {
            "trend": "Not enough data",
            "latest_price": history[0].price if history else None,
            "average_price": None,
            "suggested_price": None
        }

    prices = [p.price for p in history]

    latest_price = prices[0]
    previous_price = prices[1]

    avg_price = sum(prices) / len(prices)

    # 📈 TREND
    if latest_price > previous_price:
        trend = "Price Increased 📈"
    elif latest_price < previous_price:
        trend = "Price Dropped 📉"
    else:
        trend = "Stable ⚖️"

    # 🔥 SUGGESTED PRICE LOGIC
    if trend == "Price Dropped 📉":
        suggested_price = latest_price + 5   # increase slightly
    elif trend == "Price Increased 📈":
        suggested_price = latest_price - 5   # reduce slightly
    else:
        suggested_price = avg_price

    return {
        "trend": trend,
        "latest_price": latest_price,
        "average_price": round(avg_price, 2),
        "suggested_price": round(suggested_price, 2)
    }