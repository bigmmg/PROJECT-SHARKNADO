import sqlite3

database_name = "products"

def addNewItem():
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    print("Please input the corresponding entry for registering a new product")
    print("New Product Entry Name")
    newProdName = input(">>")
    print("New Product Entry ID")
    newProdID = input(">>")
    print("New Product Current Amount In Stock")
    newProdStock = input(">>")
    print("Optional Extra ID thing, Type N or n to skip")
    newOptionalID = input(">>")

    if newOptionalID == "N" or newOptionalID == "n":
        try:
            cursor.execute("INSERT INTO products (prodName, prodID, prodStock) VALUES (?, ?, ?)", (newProdName, newProdID, newProdStock))
            connection.commit()
            print("Product added successfully.")
        except sqlite3.IntegrityError:
            print("Error: A product with this ID already exists.")
    else:
        try:
            cursor.execute("INSERT INTO products (prodName, prodID, prodstock, prodopid) VALUES (?, ?, ?, ?)", (newProdName, newProdID, newProdStock, newOptionalID))
            connection.commit()
            print("Product added successfully with optional ID.")
            connection.close()
        except sqlite3.IntegrityError:
            print("Error: A product with this ID already exists.")
            connection.close()


def print_all_rows():
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM {database_name}")

    rows = cursor.fetchall()
    print("All products in the database:")
    for row in rows:
        print(row)
    connection.close()
    
def search_by_id(prodID):
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM {database_name} WHERE prodID = ?", (prodID,))
    row = cursor.fetchone()
    if row:
        print(f"Product with ID {prodID}: {f'{row[0]} \nProduct ID: {row[1]} \nProduct Stock: {str(row[2])} \nOptional ID: {row[3] if row[3] else 'Null'}'}")
    else:
        print(f"No product found with ID {prodID}")
    
    connection.close()

def update_stock(prodID, new_stock):
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute(f"UPDATE {database_name} SET prodstock = ? WHERE prodID = ?", (new_stock, prodID))
    row = cursor.fetchone()
    if row:
        print(f"Product with ID {prodID} updated to new stock: {new_stock}")
    else:
        print(f"No product found with ID {prodID}")

    
    connection.commit()
    print("Stock updated successfully.")
    connection.close()

def delete_product(prodID):
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute(f"DELETE FROM {database_name} WHERE prodID = ?", (prodID,))
    row = cursor.fetchone()
    connection.commit()
    if row:
        print("Product has been deleted")
    else:
        print("Product not found")

    connection.close()

while True:
    print("\nMenu:")
    print("1. Print all items")
    print("2. Add a new item")
    print("3. Search by ID")
    print("4. Update stock")
    print("5. Delete a product")
    print("6. Exit")

    choice = input("Enter your choice (1-6): ")

    if choice == "1":
        print_all_rows()
    elif choice == "2":
        addNewItem()
    elif choice == "3":
        prodID = input("Enter the product ID to search for: ")
        search_by_id(prodID)
    elif choice == "4":
        prodID = input("Enter the product ID to update: ")
        new_stock = input("Enter the new stock quantity: ")
        update_stock(prodID, new_stock)
    elif choice == "5":
        prodID = input("Enter the product ID to delete: ")
        delete_product(prodID)
    elif choice == "6":
        print("Exiting the program.")
        break
    else:
        print("Invalid choice. Please enter a number between 1 and 6.")

