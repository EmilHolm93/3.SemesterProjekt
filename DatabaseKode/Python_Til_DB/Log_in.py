import mysql.connector
import qrcode
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from io import BytesIO


def connect_to_database():
    """Connect to the MySQL database and return the connection object."""
    return mysql.connector.connect(
        host="sql7.freemysqlhosting.net",
        user="sql7748471",
        password="lTgrg27nly",
        database="sql7748471"
    )


def create_chip_inventory_table():
    """Create the chip inventory table if it doesn't exist."""
    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS chip_inventory (
            chip_value INT PRIMARY KEY,
            chip_amount INT
        )
        """
        cursor.execute(query)

        # Insert default chip values if the table is empty
        cursor.execute("SELECT COUNT(*) FROM chip_inventory")
        result = cursor.fetchone()
        if result[0] == 0:  # If the table is empty, insert initial chip values
            cursor.executemany("INSERT INTO chip_inventory (chip_value, chip_amount) VALUES (%s, %s)", [
                (1, 0),
                (5, 0),
                (10, 0),
                (20, 0),
            ])
            connection.commit()
    except mysql.connector.Error as error:
        print(f"Error: {error}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def db_login(username, password):
    """Authenticate the user based on username and password."""
    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        # Debugging print statement to check values
        print(f"Attempting login with Username: {username} and Password: {password}")

        query = "SELECT Bruger_ID, Bruger_Email FROM Bruger WHERE Bruger_Navn = %s AND Bruger_Password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()  # Fetch the result here

        # Ensure all results are processed, even if none are fetched
        cursor.fetchall()

        if result:
            user_id, user_email = result
            print("Login successful!")

            # Special case for "maintenance" user
            if username == "maintenance" and password == "1337":
                return user_id, username, user_email, "maintenance"

            return user_id, username, user_email, "user"
        else:
            print("Invalid username or password. Please try again.")
            return None, None, None, None
    except mysql.connector.Error as error:
        print(f"Error: {error}")
        return None, None, None, None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def generate_qr_code(data):
    """Generate a QR code image from the given data."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def send_email_with_qr(user_email, amount):
    """Send an email with a QR code voucher for the withdrawal amount."""
    sender_email = "CasinoChipCounter@gmail.com"
    sender_password = "qagx wpyq vewt vgxk"  # App password for Gmail
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = f"Your Withdrawal Voucher for ${amount}"
    body = f"Thank you for your withdrawal of ${amount}. Please find your QR code voucher attached."
    msg.attach(MIMEText(body, 'plain'))
    qr_data = f"Withdrawal Voucher: ${amount}"
    qr_image = generate_qr_code(qr_data)
    image = MIMEImage(qr_image, name="voucher.png")
    msg.attach(image)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Start TLS encryption
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Email sent to {user_email}.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def deposit(user_id, amount):
    """Deposit the specified amount into the user's account and log the transaction."""
    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        query = "UPDATE Bruger SET Bruger_Balance = Bruger_Balance + %s WHERE Bruger_ID = %s"
        cursor.execute(query, (amount, user_id))
        connection.commit()

        # Insert transaction
        transaction_query = f"""
        INSERT INTO bruger_transaktioner_{user_id} (beløb, transaktion_type, beskrivelse)
        VALUES (%s, 'Deposit', 'User deposited {amount:.2f}')
        """
        cursor.execute(transaction_query, (amount,))
        connection.commit()

        print(f"Successfully deposited {amount:.2f}")
        check_balance(user_id)
    except mysql.connector.Error as error:
        print(f"Error: {error}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

from decimal import Decimal

def withdraw(user_id, amount, user_email):
    """Withdraw the specified amount from the user's account, log the transaction, and send a QR code."""
    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        # Check if the user has enough balance
        cursor.execute("SELECT Bruger_Balance FROM Bruger WHERE Bruger_ID = %s", (user_id,))
        result = cursor.fetchone()

        if result and result[0] >= Decimal(amount):  # Convert 'amount' to Decimal for comparison
            # Update the user's balance
            new_balance = result[0] - Decimal(amount)  # Subtract 'amount' from the balance
            cursor.execute("UPDATE Bruger SET Bruger_Balance = %s WHERE Bruger_ID = %s", (new_balance, user_id))
            connection.commit()

            # Insert transaction record
            transaction_query = f"""
            INSERT INTO bruger_transaktioner_{user_id} (beløb, transaktion_type, beskrivelse)
            VALUES (%s, 'Withdraw', 'User withdrew {amount:.2f}')
            """
            cursor.execute(transaction_query, (amount,))
            connection.commit()

            print(f"Successfully withdrew {amount:.2f}. Your new balance is: {new_balance:.2f}")

            # Send email with QR code
            send_email_with_qr(user_email, amount)

            check_balance(user_id)  # Display updated balance
        else:
            print("Error: Insufficient balance or unable to fetch balance.")
    except mysql.connector.Error as error:
        print(f"Error while processing the withdrawal: {error}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def check_balance(user_id):
    """Check and display the user's current balance."""
    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        query = "SELECT Bruger_Balance FROM Bruger WHERE Bruger_ID = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            print(f"Your current balance is: {result[0]:.2f}")
        else:
            print("Error: Unable to retrieve balance.")
    except mysql.connector.Error as error:
        print(f"Error: {error}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def empty_counter_menu():
    """Show the empty counter menu for the maintenance user."""
    while True:
        print("\nEmpty Counter Menu:")
        print("1. Empty Tray")
        print("2. Log Out")
        choice = input("Enter your choice (1-2): ")
        if choice == '1':
            empty_tray()  # Call the function to empty the tray
        elif choice == '2':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")


def main_menu(user_id, username, user_email, user_type):
    """Display the main menu and process user choices."""
    if user_type == "maintenance":
        empty_counter_menu()
    else:
        while True:
            print(f"\nWelcome, {username}!")
            print("1. Deposit")
            print("2. Withdraw")
            print("3. Check Balance")
            print("4. Log out")
            choice = input("Enter your choice (1-4): ")
            if choice == '1':
                amount = float(input("Enter amount to deposit: "))
                deposit(user_id, amount)
            elif choice == '2':
                amount = float(input("Enter amount to withdraw: "))
                withdraw(user_id, amount, user_email)
            elif choice == '3':
                check_balance(user_id)
            elif choice == '4':
                print("Logging out...")
                break
            else:
                print("Invalid choice. Please try again.")


def empty_tray():
    """Reset the amount deposited for all chip values to 0 in the Chip_Inventory table."""
    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        # Update the 'amount_deposited' column to 0 for all chip values
        update_query = "UPDATE Chip_Inventory SET amount_deposited = 0"
        cursor.execute(update_query)
        connection.commit()

        print("Tray has been emptied. All chip quantities have been reset to 0.")
    except mysql.connector.Error as error:
        print(f"Error while emptying the tray: {error}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def main():
    print("Welcome to the Casino Chip Counter!")
    create_chip_inventory_table()  # Ensure chip inventory table is created
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    user_id, username, user_email, user_type = login(username, password)
    print(f"Logged in as {user_type}.")  # Debugging print

    if user_id:
        if user_type == "maintenance":
            print("Maintenance user logged in. Accessing empty counter menu.")
            empty_counter_menu()  # Call the empty counter menu for the maintenance user
        else:
            main_menu(user_id, username, user_email, user_type)
    else:
        print("Login failed.")


if __name__ == "__main__":
    main()
