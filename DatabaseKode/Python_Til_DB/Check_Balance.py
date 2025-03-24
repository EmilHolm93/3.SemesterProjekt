import mysql.connector

def check_balance(user_id):
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="sql7.freemysqlhosting.net",
            user="sql7743480",
            password="u72Py9FMQI",
            database="sql7743480"
        )

        cursor = connection.cursor()

        # Execute the query
        query = "SELECT Bruger_Navn, Bruger_Balance FROM Bruger WHERE Bruger_ID = %s"
        cursor.execute(query, (user_id,))

        # Fetch the result
        result = cursor.fetchone()

        if result:
            name, balance = result
            print(f"Hello, {name}! Your balance is: {balance:.2f}")
        else:
            print("User not found.")

    except mysql.connector.Error as error:
        print(f"Error: {error}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Get user input
user_id = input("Enter your user ID: ")
check_balance(user_id)