import sqlite3


class Inventory:
    # Defining the __init__ function, sets the db_file name table_name based on information passed
    def __init__(self, db_file="inventory.db", table_name="products"):
        self.db_file = db_file
        self.table_name = table_name
        self.create_table_if_missing()

    def create_table_if_missing(self):
        # Changed to an f-string to parse self.table_name correctly
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.table_name}
                   ( prodname TEXT NOT NULL,
                   prodcat TEXT NOT NULL,
                   prodid TEXT PRIMARY KEY NOT NULL,
                   prodstock INTEGER NOT NULL,
                   prodopid TEXT);''')
            connection.commit()
            # Removed manual connection.close() to let 'with' manage it safely

    def add_item(self, name, category, prod_id, stock, optional_id=None):
        # Added 'f' prefix to convert these into f-strings for self.table_name
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()

            if optional_id is None:
                cursor.execute(
                    f"INSERT INTO {self.table_name} (prodName, prodcat, prodID, prodStock) "
                    "VALUES (?, ?, ?, ?)",
                    (name, category, prod_id, stock),
                )
            else:
                cursor.execute(
                    f"INSERT INTO {self.table_name} (prodName, prodcat, prodID, prodStock, prodopid) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (name, category, prod_id, stock, optional_id),
                )
            connection.commit()


    def get_all_rows(self):
        # Returns every row as a list of tuples
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name}")
            return cursor.fetchall()

    def search_by_id(self, prod_id):
        # Returns a single row by ID or none if not found
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE prodID = ?", (prod_id,)
            )
            return cursor.fetchone()

    def update_stock(self, prod_id, new_stock):
        # Returns true if a row is found and false if not; meant to update stock
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"UPDATE {self.table_name} SET prodStock = ? WHERE prodID = ?",
                (new_stock, prod_id),
            )
            connection.commit()
            return cursor.rowcount > 0

    def delete_product(self, prod_id):
        # Returns true if a row is found and false if not; meant to delete a product
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"DELETE FROM {self.table_name} WHERE prodID = ?", (prod_id,)
            )
            connection.commit()
            return cursor.rowcount > 0
        
    def update_name(self, prod_id, new_name):
        # Returns true if a row is found and false if not; meant to update a products name
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"UPDATE {self.table_name} SET prodname = ? WHERE prodID = ?", (new_name, prod_id)
            )
            connection.commit()
            return cursor.rowcount > 0



class InventoryCLI:
    # Dictionary to easily implement new categories and such
    CATEGORIES = {
        "1": "Clothing",
        "2": "Footwear",
        "3": "Accessories",
        "4": "Computer/Laptops",
        "5": "Phones",
        "6": "Audio & Video",
        "7": "Wearables",
        "8": "Furniture",
        "9": "Home Decor",
        "10": "Health/Beauty",
        "11": "Sports/Fitness",
        "12": "Toys",
        "13": "Food",
        "14": "Office Supplies",
    }


    # __init__ to initialize the self and inventory classes
    def __init__(self, inventory: Inventory):
        self.inventory = inventory


    # Function used to prompt name
    def prompt_name(self):
        while True:
            print("New Product Entry Name")
            name = input(">>").strip()
            if name == "":
                print("Invalid Entry")
            else:
                return name

    # Function used to prompt category
    def prompt_category(self):
        while True:
            print("New Product Category")
            print("""Clothing[1]\nFootwear[2]\nAccessories[3]\nComputers/Laptops[4]
Phones[5]\nAudio & Video[6]\nWearables[7]\nFurniture[8]
Home Decor[9]\nHealth/Beauty[10]\nSports/Fitness[11]\nToys[12]
Food[13]\nOffice Supplies[14]""")
            choice = input(">>").strip()
            if choice in self.CATEGORIES:
                return self.CATEGORIES[choice]
            print("Invalid Category")

    # Function used to prompt product ID
    def prompt_prod_id(self):
        while True:
            print("New Product Entry ID")
            prod_id = input(">>").strip()
            if prod_id == "":
                print("Invalid ID")
            else:
                return prod_id

    # Function used to prompt stock
    def prompt_stock(self):
        while True:
            print("New Product Current Amount In Stock")
            stock = input(">>").strip()
            if not stock.isdigit():
                print("Invalid Stock Amount")
            else:
                return int(stock)

    # Function used to prompt the optional id
    def prompt_optional_id(self):
        print("Optional Extra ID: Type N or n to skip")
        optional_id = input(">>").strip()
        if optional_id in ("N", "n", ""):
            return None
        return optional_id

    # Method that combines all the prompts to add an item
    def add_item(self):
        name = self.prompt_name()
        category = self.prompt_category()
        prod_id = self.prompt_prod_id()
        stock = self.prompt_stock()
        optional_id = self.prompt_optional_id()

        try:
            self.inventory.add_item(name, category, prod_id, stock, optional_id)
            if optional_id is None:
                print("Product added successfully.")
            else:
                print("Product added successfully with optional ID.")
        except sqlite3.IntegrityError:
            print("Error: A product with this ID already exists.")

    # Method that prints all rows of items
    def print_all_rows(self):
        rows = self.inventory.get_all_rows()

        if not rows:
            print("No products found in the database.")
            return

        page_size = 10
        total_pages = (len(rows) + page_size - 1) // page_size
        page = 0

        while True:
            start_index = page * page_size
            end_index = start_index + page_size
            current_rows = rows[start_index:end_index]

            print(f"\nPage {page + 1}/{total_pages}")
            print("Product Name | Product Category | Product ID | Product Stock | Optional ID")
            for row in current_rows:
                print(f"{row[0]} | {row[1]} | {row[2]} | {str(row[3])} | {row[4] if row[4] else 'Null'}")

            if total_pages == 1:
                break

            print("\nOptions: [P] Next Page, [O] Past Page, [E]xit")
            choice = input("Enter your choice: ").strip().lower()

            if choice == 'p' and page < total_pages - 1:
                page += 1
            elif choice == 'o' and page > 0:
                page -= 1
            elif choice == 'e':
                break
            else:
                print("There are no more pages in that direction.")

    # Method for searching a product by ID
    def search_by_id(self):
        prod_id = input("Enter the product ID to search for: ").strip()
        row = self.inventory.search_by_id(prod_id)
        if row:
            print(
                f"Product with ID {prod_id}: {row[0]}\n"
                f"Product Category: {row[1]}\n"
                f"Product ID: {row[2]}\n"
                f"Product Stock: {row[3]}\n"
                f"Optional ID: {row[4] if row[4] else 'Null'}"
            )
        else:
            print(f"No product found with ID {prod_id}")

    # Method for updating the stock of an item
    def update_stock(self):
        prod_id = input("Enter the product ID to update: ").strip()
        new_stock = input("Enter the new stock quantity: ").strip()
        if not new_stock.isdigit():
            print("Invalid stock number.")
            return
            
        updated = self.inventory.update_stock(prod_id, int(new_stock))
        if updated:
            print(f"Product with ID {prod_id} updated to new stock: {new_stock}")
        else:
            print(f"No product found with ID {prod_id}")

    # Method for deleting a product by ID
    def delete_product(self):
        prod_id = input("Enter the product ID to delete: ").strip()
        deleted = self.inventory.delete_product(prod_id)
        if deleted:
            print("Product has been deleted")
        else:
            print("Product not found")

    # Method for updating the name of a product by ID
    def update_name(self):
        prod_id = input("Enter the product ID to change the name: ").strip()
        new_name = input("Enter the new name for the product: ").strip()
        changed_name = self.inventory.update_name(prod_id, new_name)
        if changed_name:
            print(f"Product has had name changed to: {new_name}")
        else:
            print("Product not found")

    # Method to run the entire main menu
    def run(self):
        while True:
            print("\nGoodwill Inventory Prototype System:")
            print("1. Print all items")
            print("2. Add a new item")
            print("3. Search by ID")
            print("4. Update stock")
            print("5. Delete a product")
            print("6. Update a name")
            print("7. Exit")

            choice = input("Enter your choice (1-7): ").strip()

            if choice == "1":
                self.print_all_rows()
            elif choice == "2":
                self.add_item()
            elif choice == "3":
                self.search_by_id()
            elif choice == "4":
                self.update_stock()
            elif choice == "5":
                self.delete_product()
            elif choice == "6":
                self.update_name()
            elif choice == "7":
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")

# Launches the command-line interface and intializes the app
if __name__ == "__main__":
    inventory = Inventory()
    cli = InventoryCLI(inventory)
    cli.run()