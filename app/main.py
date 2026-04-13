from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine, SessionLocal
from app.models.product import Base, Product
from app.schemas.product import ProductCreate

import pandas as pd
from sklearn.linear_model import LinearRegression
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from fastapi.responses import FileResponse
import matplotlib.pyplot as plt

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Create tables
Base.metadata.create_all(bind=engine)


# ✅ Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Home
@app.get("/")
def home():
    return {"message": "Sentinel-Sales API Running 🚀"}


# ✅ GET all products
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


# ✅ POST product
@app.post("/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(
        name=product.name,
        price=product.price,
        competitor=product.competitor
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product added successfully ✅",
        "data": {
            "id": new_product.id,
            "name": new_product.name,
            "price": new_product.price,
            "competitor": new_product.competitor
        }
    }


# ✅ GET latest
@app.get("/products/latest")
def get_latest_product(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.created_at.desc()).first()


# ✅ GET history
@app.get("/products/history")
def get_product_history(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.created_at.desc()).all()


# 🔥 ML ANALYSIS
@app.get("/products/analysis")
def price_analysis(name: str, db: Session = Depends(get_db)):
    history = db.query(Product)\
        .filter(Product.name == name)\
        .order_by(Product.created_at.asc())\
        .all()

    if len(history) < 5:
        return {
            "trend": "Not enough data",
            "latest_price": None,
            "suggested_price": None,
            "profit": None,
            "insight": "Add more data 📊"
        }

    df = pd.DataFrame([{"price": p.price} for p in history])
    df = df.tail(20).reset_index(drop=True)
    df["time"] = range(len(df))

    X = df[["time"]]
    y = df["price"]

    model = LinearRegression()
    model.fit(X, y)

    predicted_price = model.predict([[len(df)]])[0]
    latest_price = df["price"].iloc[-1]

    trend = "UP 📈" if predicted_price > latest_price else "DOWN 📉"

    profit = predicted_price - latest_price

    change_percent = ((predicted_price - latest_price) / latest_price) * 100

    if change_percent > 5:
        insight = f"Increase price by {round(change_percent,1)}% 🚀"
    elif change_percent < -5:
        insight = f"Decrease price by {abs(round(change_percent,1))}% ⚠️"
    else:
        insight = "Maintain current price 👍"

    return {
        "trend": trend,
        "latest_price": round(latest_price, 2),
        "suggested_price": round(predicted_price, 2),
        "profit": round(profit, 2),
        "insight": insight
    }


# 🔥 PDF REPORT (UPDATED 🚀)
@app.get("/products/report")
def generate_report(name: str, db: Session = Depends(get_db)):
    history = db.query(Product).filter(Product.name == name).all()

    if len(history) < 2:
        return {"error": "Not enough data"}

    history = history[-20:]
    prices = [p.price for p in history]

    latest_price = prices[-1]

    # 🔥 ML
    df = pd.DataFrame({"price": prices})
    df["time"] = range(len(df))

    model = LinearRegression()
    model.fit(df[["time"]], df["price"])

    predicted_price = model.predict([[len(df)]])[0]
    profit = predicted_price - latest_price

    # 🧠 Insight
    change_percent = ((predicted_price - latest_price) / latest_price) * 100

    if change_percent > 5:
        insight = f"Increase price by {round(change_percent,1)}%"
    elif change_percent < -5:
        insight = f"Decrease price by {abs(round(change_percent,1))}%"
    else:
        insight = "Maintain current price"

    # 📊 Graph
    graph_path = generate_graph(history, name)

    # 📄 PDF
    file_name = f"{name}_report.pdf"
    doc = SimpleDocTemplate(file_name)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph(f"<b>Sentinel-Sales Report</b>", styles["Title"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"<b>Product:</b> {name}", styles["Heading2"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Latest Price: ₹{round(latest_price,2)}", styles["Normal"]))
    content.append(Paragraph(f"Predicted Price (ML): ₹{round(predicted_price,2)}", styles["Normal"]))
    content.append(Paragraph(f"Expected Profit: ₹{round(profit,2)}", styles["Normal"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Insight: {insight}", styles["Normal"]))
    content.append(Spacer(1, 15))

    # 📈 GRAPH IMAGE
    content.append(Image(graph_path, width=400, height=200))
    content.append(Spacer(1, 15))

    strategy = "Increase Price 🚀" if profit > 0 else "Reduce Price 🔥"
    content.append(Paragraph(f"Strategy: {strategy}", styles["Normal"]))

    doc.build(content)

    return FileResponse(file_name, media_type='application/pdf', filename=file_name)


# 📊 GRAPH FUNCTION
def generate_graph(history, name):
    prices = [p.price for p in history[-10:]]
    labels = list(range(1, len(prices) + 1))

    plt.figure()
    plt.plot(labels, prices, marker='o')
    plt.title(f"{name} Price Trend")
    plt.xlabel("Time")
    plt.ylabel("Price")

    image_path = f"{name}_graph.png"
    plt.savefig(image_path)
    plt.close()

    return image_path