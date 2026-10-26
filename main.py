import os
import csv
import sqlite3

print("1.Import CSV")
print("2.View sales report")

choice = input("Choose an option: ")

connection = sqlite3.connect("sales.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    product TEXT,
    category TEXT,
    quantity INTEGER,
    unit_price INTEGER
)
""")

cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS imported_files(
        filename TEXT PRIMARY KEY
    )
""")

connection.commit()

cursor.execute(
    "INSERT OR IGNORE INTO imported_files (filename) VALUES (?)",
    ("sales.csv",)
)

connection.commit()

if choice == "1":
    if not os.path.exists("sales.csv"):
        print("Error: sales.csv was not found.")
    else:
        cursor.execute(
            "SELECT filename FROM imported_files WHERE filename = ?",
            ("sales.csv",)
        )

        if cursor.fetchone():
            print("sales.csv has already been imported.")

        else:
            try:
                with open("sales.csv", "r", newline="") as file:
                    reader = csv.DictReader(file)

                    for row in reader:
                        quantity = int(row["quantity"])
                        price = int(row["unit_price"])

                        cursor.execute("""
                            INSERT INTO sales(date, product, category, quantity, unit_price)
                            VALUES(?, ?, ?, ?, ?)""",
                            (row["date"], 
                            row["product"], 
                            row["category"], 
                            quantity, 
                            price
                            )
                        )
                    
                        # #total = quantity * price
                        # print(f"{row['product']} : {total}")
                cursor.execute(
                    "INSERT INTO imported_files (filename) VALUES (?)",
                    ("sales.csv",)
                )
                connection.commit()
                print("CSV imported successfully.")

            except FileNotFoundError:
                connection.rollback()
                print("Error : sales.csv was not found.")

            except ValueError:
                connection.rollback()
                print("Error : quantity and unit_price must be valid numbers.")
            
elif choice == "2":

    cursor.execute(
        "SELECT COUNT(*) FROM sales")
    print("Records stored :", cursor.fetchone()[0])

    cursor.execute("""
        SELECT
            product,
            SUM(quantity * unit_price) AS total_sales
        FROM sales
        GROUP BY product
        ORDER BY total_sales DESC
    """)

    print("\nSales Report")
    print("-" * 35)
    print(f"{'Product':<15} {'Total Sales':>15}")
    print("-" * 35)

    for product, total_sales in cursor.fetchall():
        print(f"{product:<15} {'₹' + format(total_sales, ','):>15}")

    print("-" * 35)

else:
    print("Invalid option. Please choose 1 or 2.")
