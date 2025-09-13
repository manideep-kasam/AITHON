from flask import Flask, request, jsonify
import datetime
import random

app = Flask(__name__)

# In-memory storage (you can later replace with DB)
transactions = []
goals = {}
budget_limits = {
    "Food": 2000,
    "Books": 1500,
    "Travel": 1000,
    "Other": 1000
}

# Auto categorization keywords
categories = {
    "Food": ["pizza", "burger", "meal", "lunch", "dinner", "snacks"],
    "Books": ["book", "pen", "notebook", "stationery"],
    "Travel": ["bus", "train", "ticket", "travel", "cab"],
}

def categorize(description):
    desc = description.lower()
    for cat, keywords in categories.items():
        if any(word in desc for word in keywords):
            return cat
    return "Other"

@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    data = request.json
    description = data.get("description")
    amount = float(data.get("amount", 0))
    category = categorize(description)
    date = datetime.date.today().isoformat()

    transaction = {"description": description, "amount": amount, "category": category, "date": date}
    transactions.append(transaction)
    return jsonify({"message": "Transaction added", "transaction": transaction})

@app.route("/get_expenses", methods=["GET"])
def get_expenses():
    return jsonify({"transactions": transactions})

@app.route("/budget_alerts", methods=["GET"])
def budget_alerts():
    spent = {cat: 0 for cat in budget_limits}
    for t in transactions:
        spent[t["category"]] += t["amount"]

    alerts = []
    for cat, limit in budget_limits.items():
        if spent[cat] >= limit:
            alerts.append(f"🚨 You exceeded your {cat} budget!")
        elif spent[cat] >= 0.8 * limit:
            alerts.append(f"⚠️ You are close to exceeding {cat} budget ({spent[cat]}/{limit})")

    return jsonify({"alerts": alerts})

@app.route("/predict_spending", methods=["GET"])
def predict_spending():
    # Simple prediction: average of existing expenses * 1.1
    prediction = {}
    spent = {cat: 0 for cat in budget_limits}
    count = {cat: 0 for cat in budget_limits}
    for t in transactions:
        spent[t["category"]] += t["amount"]
        count[t["category"]] += 1

    for cat in budget_limits:
        avg = spent[cat] / count[cat] if count[cat] else 0
        prediction[cat] = round(avg * 1.1, 2)

    return jsonify({"predicted_spending": prediction})

@app.route("/set_goal", methods=["POST"])
def set_goal():
    data = request.json
    goal_name = data.get("goal")
    amount = float(data.get("amount", 0))
    goals[goal_name] = {"target": amount, "progress": 0}
    return jsonify({"message": f"Goal '{goal_name}' set", "goal": goals[goal_name]})

@app.route("/update_goal", methods=["POST"])
def update_goal():
    data = request.json
    goal_name = data.get("goal")
    saved = float(data.get("saved", 0))
    if goal_name in goals:
        goals[goal_name]["progress"] += saved
        return jsonify({"message": "Goal updated", "goal": goals[goal_name]})
    return jsonify({"error": "Goal not found"}), 404

@app.route("/reminders", methods=["GET"])
def reminders():
    reminders_list = [
        "💡 Remember to save at least 20% of your pocket money.",
        "📘 Focus on your academics – financial discipline = success.",
        "🚨 Pay your electricity/wifi bills on time!",
        "✨ Small savings make big differences!"
    ]
    return jsonify({"reminders": random.sample(reminders_list, 2)})

if __name__ == "__main__":
    app.run(debug=True)
