import mysql.connector

def add_user(name, password, balance, email):
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="sql7.freemysqlhosting.net",
            user="sql7748471",
            password="lTgrg27nly",
            database="sql7748471"
        )

        cursor = connection.cursor()

        # SQL query to insert a new user
        query = """
        INSERT INTO Bruger (Bruger_Navn, Bruger_Password, Bruger_Balance, Bruger_Email)
        VALUES (%s, %s, %s, %s)
        """

        # Values to be inserted
        values = (name, password, balance, email)

        # Execute the query
        cursor.execute(query, values)

        # Commit the changes
        connection.commit()

        print(f"User {name} added successfully!")

        # Create transaction table for the new user
        create_transaction_table(cursor, cursor.lastrowid)

    except mysql.connector.Error as error:
        print(f"Error: {error}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_transaction_table(cursor, user_id):
    try:
        # SQL query to create a transaction table for the user
        query = f"""
        CREATE TABLE IF NOT EXISTS bruger_transaktioner_{user_id} (
            transaktion_id INT AUTO_INCREMENT PRIMARY KEY,
            beløb DECIMAL(10, 2) NOT NULL,
            transaktion_type ENUM('Deposit', 'Withdraw') NOT NULL,
            dato TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            beskrivelse VARCHAR(255)
        )
        """
        cursor.execute(query)
        print(f"Transaction table created for user ID: {user_id}")
    except mysql.connector.Error as error:
        print(f"Error creating transaction table: {error}")

# Add the new user
add_user("maintenance", "1337", 0, "Don_John_Mekanikkeren@ccc.com")