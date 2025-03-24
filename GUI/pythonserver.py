from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS

app = Flask(__name__)

# Configure secret key
app.secret_key = 'your_secret_key'

# Set up CORS
CORS(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Set valid QR values
valid_amount = [100, 200, 500, 1000, 2500, 5000]

# To store users
users = {}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password, balance=0):
        self.id = id
        self.username = username
        self.password = password
        self.balance = balance

# Load user callback
@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route("/")
def home():
    return render_template("loginwebsite.html")

# Route to handle logins 
@app.route("/login", methods=["POST"])
@login_required
def login():
    data = request.get_json()
    
    # Validate that the user input a valid set of username and password 
    if not data or "Username" not in data or "Password" not in data:
        return jsonify({"status": "error", "message": "Invalid data format."}), 400
    
    username = data["Username"]
    password = data["Password"]

    # Check if the user exists and the password matches
    user = next((user for user in users.values() if user.username == username), None)
    if user and user.password == password:
        login_user(user)
        return jsonify({"status": "success", "message": "Logged in successfully."}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid username or password."}), 401

# Route to handle logout
@app.route("/logout", methods=["POST", "GET"])
def logout():
    logout_user()
    return redirect(url_for('home'))

# route to the user profile
@app.route("/profile", methods=["POST", "GET"])
@login_required
def profile():
    return render_template("profile.html")

# Route to deposit
@app.route("/profile/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    if request.method == "GET":
        return render_template("deposit.html", balance=current_user.balance, valid_amounts=valid_amount)

    if request.method == "POST":
        try:
            # Extract the amount from the form data
            amount = int(request.form.get("amount", 0))

            # Validate the deposit amount
            if amount in valid_amount:
                # Update the user's balance
                current_user.balance += amount
                return render_template("deposit.html", balance=current_user.balance, valid_amounts=valid_amount, message=f"Deposit successful! New balance: {current_user.balance}")
            else:
                return render_template("deposit.html", balance=current_user.balance, valid_amounts=valid_amount, message="Invalid deposit amount. Please try again.")
        except ValueError:
            return render_template("deposit.html", balance=current_user.balance, valid_amounts=valid_amount, message="Invalid input. Please try again.")


# Withdraw
@app.route("/profile/withdraw", methods=["POST", "GET"])
@login_required
def withdraw():
    message = None  # Message to show success or error feedback

    if request.method == "POST":
        data = request.form  # Get data from the form
        if "amount" in data:
            try:
                amount = int(data["amount"])  # Convert the amount to an integer
            except ValueError:
                message = "Invalid amount. Please enter a valid number."
                return render_template("withdraw.html", balance=current_user.balance, message=message)

            # Check if balance is sufficient for the withdrawal
            if amount <= current_user.balance:
                # Remove from the balance
                current_user.balance -= amount
                message = f"Successfully withdrew {amount}. Your new balance is {current_user.balance}."
            else:
                message = "Insufficient balance. Please try again with a lower amount."
        else:
            message = "Amount not provided. Please try again."

    # Render the withdraw page
    return render_template("withdraw.html", balance=current_user.balance, message=message)


# Check balance
@app.route("/profile/balance", methods=["POST", "GET"])
@login_required
def check_balance():
    return render_template("balance.html", balance=current_user.balance)

# Run the Flask app
if __name__ == "__main__":
    # test users
    users["1"] = User(id="1", username="user1", password="password1", balance=10000)
    users["2"] = User(id="2", username="user2", password="password2", balance=5500)
    
    app.run(host="127.0.0.1", port=8080, debug=True)
