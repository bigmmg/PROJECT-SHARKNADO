import sqlite3

database_name = "products"

def addNewItem():
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    print("Please input the corresponding entry for registering a new product")
    while True:
        print("New Product Entry Name")
        newProdName = input(">>")
        newProdName = newProdName.strip()
        if newProdName == "":
            print("Invalid Entry")
        else:
            break
    while True:
        print("New Product Category")
        print("Clothing[1], Footwear[2], Accessories[3], Computers/Laptops[4], Phones[5], Audio & Video[6], Wearables[7], Furniture[8], Home Decor[9], Health/Beauty[10], Sports/Fitness[11], Toys[12], Food[13], Office Supplies[14]")
        catChosen = input(">>")
        if catChosen == "1":
            newProdCat = "Clothing"
            break
        elif catChosen == "2":
            newProdCat = "Footwear"
            break
        elif catChosen == "3":
            newProdCat = "Accessories"
            break
        elif catChosen == "4":
            newProdCat = "Computer/Laptops"
            break
        elif catChosen == "5":
            newProdCat = "Phones"
            break
        elif catChosen == "6":
            newProdCat = "Audio & Video"
            break
        elif catChosen == "7":
            newProdCat = "Wearables"
            break
        elif catChosen == "8":
            newProdCat = "Furniture"
            break
        elif catChosen == "9":
            newProdCat = "Home Decor"
            break
        elif catChosen == "10":
            newProdCat = "Health/Beauty"
            break
        elif catChosen == "11":
            newProdCat = "Sports/Fitness"
            break
        elif catChosen == "12":
            newProdCat = "Toys"
            break
        elif catChosen == "13":
            newProdCat = "Food"
            break
        elif catChosen == "14":
            newProdCat = "Office Supplies"
            break
        else:
            print("Invalid Category") 
    while True:
        print("New Product Entry ID")
        newProdID = input(">>")
        newProdID = newProdID.strip()
        if newProdID == "":
            print("Invalid ID")
        else:
            break
    while True:
        print("New Product Current Amount In Stock")
        newProdStock = input(">>")
        if int(newProdStock) < 0:
            print("Invalid Stock Amount")
        else:
            break
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
    print("Product Name | Product ID | Product Stock | Optional ID")
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
    row = cursor.fetchall()
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

    cursor.execute(f"SELECT COUNT(*) FROM {database_name}")
    beforeDel = cursor.fetchall()[0]
    

    cursor.execute(f"DELETE FROM {database_name} WHERE prodID = ?", (prodID,))

    #always prints product not found even if it is found, need to fix this
    #Instead check if the number of rows has change after deletion compared to before

    cursor.execute(f"SELECT COUNT(*) FROM {database_name}")
    afterDel = cursor.fetchall()[0]
    
    if beforeDel > afterDel:
        print("Product has been deleted")
    else:
        print("Product not found")

    connection.commit()
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

