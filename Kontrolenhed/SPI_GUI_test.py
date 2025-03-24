from flask import Flask, request, jsonify, render_template, redirect, url_for, copy_current_request_context
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from threading import Thread, Event
from picamera2 import Picamera2
import cv2
from pyzbar.pyzbar import decode
import time
import requests

from database import *
from actuatorcontrol import *

CMD_CLOSE_SERVO_1 = 0x01
CMD_OPEN_SERVO_1 = 0x02
CMD_OPEN_SERVO_2 = 0x03
CMD_CLOSE_SERVO_2 = 0x04

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Set valid QR values
valid_amount = [1, 5, 10, 20]

# To store users
users = {}

# Temporary deposit storage
user_deposit_temp = {}

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route("/")
def home():
    return render_template("loginwebsite.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    data = request.get_json()
    if not data or "Username" not in data or "Password" not in data:
        return jsonify({"status": "error", "message": "Invalid data format."}), 400
    
    username = data["Username"]
    password = data["Password"]
    
    user_id, db_username, user_email, user_type = db_login(username, password)
    
    if user_id:
        # Check if the user is already in the users dictionary
        if user_id not in users:
            # Create a new User object with the returned data
            user = User(id=str(user_id), username=db_username, email=user_email)
            # Add the user to the global 'users' dictionary
            users[str(user_id)] = user
        
        # Log the user in using Flask-Login
        login_user(users[str(user_id)])
        
        # Debug output for current_user
        print(f"Current User ID: {current_user.id}")
        print(f"Is Authenticated: {current_user.is_authenticated}")
        
        next_url = request.args.get('next', url_for('profile'))  # Redirect after login
        
        return jsonify({"status": "success", "message": "Logged in successfully.", "next": next_url}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid username or password."}), 401

@app.route("/logout")
@login_required
def logout():
    logout_user()
    act_send_command(CMD_CLOSE_SERVO_1)
    act_send_command(CMD_CLOSE_SERVO_2)
    return redirect(url_for('home'))

@app.route("/profile")
@login_required
def profile():
    print(f"User is authenticated: {current_user.is_authenticated}")
    return render_template("profile.html", current_user=current_user)

@app.route("/profile/deposit", methods=["GET", "POST"])
#@login_required
def deposit():
    if request.method == "GET":
        scanner_running.set()
        user_deposit_temp[current_user.id] = []

        @copy_current_request_context
        def thread_safe_scanning():
            start_scanning()

        Thread(target=thread_safe_scanning, daemon=True).start()
        return render_template("deposit.html")

    if request.method == "POST":
        deposits = request.json.get("deposits", [])
        valid_deposits = [int(amount) for amount in deposits if amount in valid_amount]
        invalid_deposits = [amount for amount in deposits if amount not in valid_amount]

        if valid_deposits:
            total_deposit = sum(valid_deposits)
            db_deposit(current_user.id, total_deposit)

            return jsonify({
                "status": "success",
                "new_balance": db_check_balance(current_user.id),
                "valid_deposits": valid_deposits,
                "invalid_deposits": invalid_deposits
            }), 200

        return jsonify({
            "status": "error",
            "message": "Invalid deposit amounts.",
            "invalid_deposits": invalid_deposits
        }), 400

@app.route("/stop_scanning", methods=["POST"])
#@login_required
def stop_scanning():
    scanner_running.clear()

    deposits = user_deposit_temp.get(current_user.id, [])
    if deposits:
        response = requests.post(
            'http://127.0.0.1:8080/profile/deposit',
            json={"deposits": deposits},
            cookies={"session": request.cookies.get("session")},
        )

        if response.status_code == 200:
            print("Deposits processed successfully:", response.json())
        else:
            print("Error processing deposits:", response.status_code, response.text)

    user_deposit_temp[current_user.id] = []
    return redirect(url_for("profile"))

@app.route("/profile/withdraw", methods=["GET", "POST"])
#@login_required
def withdraw():
    message = None
    if request.method == "POST":
        data = request.form
        if "amount" in data:
            try:
                amount = int(data["amount"])
            except ValueError:
                message = "Invalid amount. Please enter a valid number."
                return render_template("withdraw.html", balance=current_user.balance, message=message)

            if amount <= int(float(db_check_balance(current_user.id))):
                db_withdraw(current_user.id, amount, current_user.email)
                message = f"Successfully withdrew {amount}. Your new balance is {db_check_balance(current_user.id)}."
            else:
                message = "Insufficient balance. Please try again with a lower amount."
        else:
            message = "Amount not provided. Please try again."

    return render_template("withdraw.html", balance=db_check_balance(current_user.id), message=message)

@app.route("/profile/balance", methods=["GET"])
#@login_required
def check_balance():
    return render_template("balance.html", balance=db_check_balance(current_user.id))

scanner_running = Event()

def start_scanning():
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    # Ensure actuators start in their default states
    act_send_command(CMD_OPEN_SERVO_1)  # Top actuator open
    act_send_command(CMD_CLOSE_SERVO_2)  # Bottom actuator closed

    print("Starting QR Code Reader...")

    try:
        while scanner_running.is_set():
            frame = picam2.capture_array()
            decoded_objects = decode(frame)

            # Only process if QR code(s) are detected
            if decoded_objects:
                print("QR code detected, starting airlock sequence...")

                # Process all detected QR codes (though it doesn't change airlock sequence logic)
                for obj in decoded_objects:
                    try:
                        to_send = obj.data.decode('utf-8').strip()
                        print(f"QR Code detected: {to_send}")  # Log QR code contents

                        # Optionally check validity (though it doesn't affect airlock)
                        if to_send.isdigit():
                            to_send = int(to_send)
                            if to_send in valid_amount:
                                print(f"Valid QR Code: {to_send}")
                                user_deposit_temp[current_user.id].append(to_send)
                            else:
                                print(f"Invalid QR Code: {to_send}")
                        else:
                            print(f"Non-numeric QR Code: {to_send}")

                    except Exception as e:
                        print(f"Error processing QR code: {e}")

                # Perform airlock sequence
                print("Closing top actuator...")
                act_send_command(CMD_CLOSE_SERVO_1)  # Close top actuator
                time.sleep(1)

                print("Opening bottom actuator...")
                act_send_command(CMD_OPEN_SERVO_2)   # Open bottom actuator
                time.sleep(1)

                print("Closing bottom actuator...")
                act_send_command(CMD_CLOSE_SERVO_2)  # Close bottom actuator
                time.sleep(1)

                print("Reopening top actuator...")
                act_send_command(CMD_OPEN_SERVO_1)  # Reopen top actuator
                time.sleep(1)

            # Delay to avoid excessive CPU usage (even when no QR code is detected)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Exiting.")
    finally:
        picam2.stop()
        cv2.destroyAllWindows()



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
