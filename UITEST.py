import sqlite3
import customtkinter as ctk
from tkinter import messagebox, ttk

# --- Keep your exact Inventory database logic intact ---
class Inventory:
    def __init__(self, db_file="inventory.db", table_name="products"):
        self.db_file = db_file
        self.table_name = table_name
        self.create_table_if_missing()

    def create_table_if_missing(self):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.table_name}
                   ( prodname TEXT NOT NULL,
                   prodcat TEXT NOT NULL,
                   prodid TEXT PRIMARY KEY NOT NULL,
                   prodstock INTEGER NOT NULL,
                   prodopid TEXT);''')
            connection.commit()

    def add_item(self, name, category, prod_id, stock, optional_id=None):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            if optional_id in (None, "", "None"):
                cursor.execute(
                    f"INSERT INTO {self.table_name} (prodname, prodcat, prodID, prodStock) VALUES (?, ?, ?, ?)",
                    (name, category, prod_id, stock),
                )
            else:
                cursor.execute(
                    f"INSERT INTO {self.table_name} (prodname, prodcat, prodID, prodStock, prodopid) VALUES (?, ?, ?, ?, ?)",
                    (name, category, prod_id, stock, optional_id),
                )
            connection.commit()

    def get_all_rows(self):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name}")
            return cursor.fetchall()

    def search_by_id(self, prod_id):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE prodID = ?", (prod_id,))
            return cursor.fetchone()

    def update_stock(self, prod_id, new_stock):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE {self.table_name} SET prodStock = ? WHERE prodID = ?", (new_stock, prod_id))
            connection.commit()
            return cursor.rowcount > 0


    def delete_product(self, prod_id):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM {self.table_name} WHERE prodID = ?", (prod_id,))
            connection.commit()
            return cursor.rowcount > 0
        
    def update_name(self, prod_id, new_name):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE {self.table_name} SET prodname = ? WHERE prodID = ?", (new_name, prod_id))
            connection.commit()
            return cursor.rowcount > 0
        
    def sort_by(self, category):
        columns = {"prodname", "prodcat", "prodid", "prodstock"}
        if category not in columns:
            raise ValueError(f"Invalid sort column: {category}")
        


        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM  {self.table_name} ORDER BY {category}")
            return cursor.fetchall()


# --- New GUI Interface using CustomTkinter ---
class InventoryGUI(ctk.CTk):
    CATEGORIES = [
        "Clothing", "Footwear", "Accessories", "Computer/Laptops", 
        "Phones", "Audio & Video", "Wearables", "Furniture", 
        "Home Decor", "Health/Beauty", "Sports/Fitness", "Toys", 
        "Food", "Office Supplies"
    ]


    def __init__(self, inventory: Inventory):
        super().__init__()
        self.inventory = inventory

        # Window Settings
        self.title("Goodwill Inventory Prototype System")
        self.geometry("850x550")
        ctk.set_appearance_mode("System")  # Follows Windows/macOS theme
        ctk.set_default_color_theme("blue") # Options: "blue", "green", "dark-blue"

        # Main Layout: Tabview for clean navigation
        self.tabview = ctk.CTkTabview(self, width=820, height=520)
        self.tabview.pack(padx=15, pady=15, fill="both", expand=True)

        self.tab_view_all = self.tabview.add("View Inventory")
        self.tab_add = self.tabview.add("Add / Manage Item")

        # Initialize the tabs
        self.setup_view_tab()
        self.setup_manage_tab()

    # --- TAB 1: VIEW INVENTORY ---
    def setup_view_tab(self):
        # Top Control Row
        control_frame = ctk.CTkFrame(self.tab_view_all, fg_color="transparent")
        control_frame.pack(fill="x", padx=10, pady=10)

        refresh_btn = ctk.CTkButton(control_frame, text="Refresh Data", command=self.load_table_data)
        refresh_btn.pack(side="left", padx=5)

        search_label = ctk.CTkLabel(control_frame, text="Search ID:")
        search_label.pack(side="left", padx=(20, 5))

        self.search_entry = ctk.CTkEntry(control_frame, placeholder_text="Enter ID...")
        self.search_entry.pack(side="left", padx=5)

        search_btn = ctk.CTkButton(control_frame, text="Search", width=80, command=self.search_item)
        search_btn.pack(side="left", padx=5)

        # Scrollable Data Table using standard tkinter Treeview (styled cleanly)
        table_frame = ctk.CTkFrame(self.tab_view_all)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("name", "category", "id", "stock", "optional_id")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("name", text="Product Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("id", text="Product ID")
        self.tree.heading("stock", text="Stock")
        self.tree.heading("optional_id", text="Optional ID")

        self.tree.column("name", width=180)
        self.tree.column("category", width=150)
        self.tree.column("id", width=100)
        self.tree.column("stock", width=80)
        self.tree.column("optional_id", width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_table_data()

        sort_label = ctk.CTkLabel(control_frame, text="Sort by:")
        sort_label.pack(side="left", padx=(20, 5))

        self.sort_options = {
            "Name": "prodname",
            "Category": "prodcat",
            "Product ID": "prodid",
            "Stock" : "prodstock",
        }

        self.combo_sort = ctk.CTkComboBox(control_frame, values=list(self.sort_options.keys()), command=self.sort_table)
        self.combo_sort.set("Sort by...")
        self.combo_sort.pack(side="left", padx=5)
    # --- TAB 2: ADD & MANAGE ---
    def setup_manage_tab(self):
        # Grid layout split: Left side Add, Right side Update/Delete
        self.tab_add.grid_columnconfigure(0, weight=1, uniform="group1")
        self.tab_add.grid_columnconfigure(1, weight=1, uniform="group1")

        # LEFT SIDE: ADD ITEM FORM
        add_frame = ctk.CTkFrame(self.tab_add)
        add_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        ctk.CTkLabel(add_frame, text="Add New Item", font=("Arial", 16, "bold")).pack(pady=10)

        self.entry_name = ctk.CTkEntry(add_frame, placeholder_text="Product Name")
        self.entry_name.pack(pady=5, padx=20, fill="x")

        self.combo_cat = ctk.CTkComboBox(add_frame, values=self.CATEGORIES)
        self.combo_cat.set("Select Category")
        self.combo_cat.pack(pady=5, padx=20, fill="x")

        self.entry_id = ctk.CTkEntry(add_frame, placeholder_text="Product ID")
        self.entry_id.pack(pady=5, padx=20, fill="x")

        self.entry_stock = ctk.CTkEntry(add_frame, placeholder_text="Initial Stock Amount")
        self.entry_stock.pack(pady=5, padx=20, fill="x")

        self.entry_opt_id = ctk.CTkEntry(add_frame, placeholder_text="Optional Extra ID (Leave blank if none)")
        self.entry_opt_id.pack(pady=5, padx=20, fill="x")

        ctk.CTkButton(add_frame, text="Save Item to Database", fg_color="#2b9348", hover_color="#1e6831", command=self.add_item).pack(pady=15)

        # RIGHT SIDE: UPDATE & ACTIONS FORM
        manage_frame = ctk.CTkFrame(self.tab_add)
        manage_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        ctk.CTkLabel(manage_frame, text="Modify Existing Item", font=("Arial", 16, "bold")).pack(pady=10)

        self.action_id = ctk.CTkEntry(manage_frame, placeholder_text="Target Product ID *")
        self.action_id.pack(pady=10, padx=20, fill="x")

        # Row block for updating Stock
        stock_frame = ctk.CTkFrame(manage_frame, fg_color="transparent")
        stock_frame.pack(fill="x", padx=20, pady=5)
        self.entry_new_stock = ctk.CTkEntry(stock_frame, placeholder_text="New Stock Value", width=140)
        self.entry_new_stock.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(stock_frame, text="+", width = 50, command=self.update_stockinc).pack(side="right")
        ctk.CTkButton(stock_frame, text="-", width = 50, command=self.update_stockdec).pack(side="right")

        # Row block for updating Name
        name_frame = ctk.CTkFrame(manage_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=20, pady=5)
        self.entry_new_name = ctk.CTkEntry(name_frame, placeholder_text="New Name Value", width=140)
        self.entry_new_name.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(name_frame, text="Update Name", width=100, command=self.update_name).pack(side="right")
        self.status_label = ctk.CTkLabel(manage_frame, text="No changes yet", font=("Arial", 12, "italic"), text_color="#7e53ff")
        self.status_label.pack(pady=(20, 5))

        # Separation
        ctk.CTkLabel(manage_frame, text="Danger Zone", font=("Arial", 12, "bold"), text_color="#d90429").pack(pady=(20, 5))
        ctk.CTkButton(manage_frame, text="Delete Product Permanently", fg_color="#d90429", hover_color="#b30322", command=self.delete_item).pack(pady=5)

    # --- LOGIC INTEGRATION FUNCTIONS ---
    def load_table_data(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Populate new items
        for row in self.inventory.get_all_rows():
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4] if row[4] else "Null"))

    def search_item(self):
        target_id = self.search_entry.get().strip()
        if not target_id:
            self.load_table_data()
            return
        
        row = self.inventory.search_by_id(target_id)
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if row:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4] if row[4] else "Null"))
        else:
            messagebox.showinfo("Not Found", f"No product found with ID: {target_id}")

    def add_item(self):
        name = self.entry_name.get().strip()
        category = self.combo_cat.get()
        prod_id = self.entry_id.get().strip()
        stock = self.entry_stock.get().strip()
        opt_id = self.entry_opt_id.get().strip()

        if not name or category == "Select Category" or not prod_id or not stock:
            messagebox.showerror("Error", "Please fill in all mandatory fields.")
            return

        if not stock.isdigit():
            messagebox.showerror("Error", "Stock must be a valid integer.")
            return

        try:
            self.inventory.add_item(name, category, prod_id, int(stock), opt_id if opt_id else None)
            messagebox.showinfo("Success", "Product added successfully!")
            self.load_table_data()
            # Clear inputs
            self.entry_name.delete(0, 'end')
            self.entry_id.delete(0, 'end')
            self.entry_stock.delete(0, 'end')
            self.entry_opt_id.delete(0, 'end')
            self.combo_cat.set("Select Category")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "A product with this ID already exists.")

    def update_stockinc(self):
        prod_id = self.action_id.get().strip()
        new_stock = self.entry_new_stock.get().strip()

        if not prod_id:
            messagebox.showerror("Error", f"No product found with ID: {prod_id}")
            return
        
        if not new_stock.isdigit():
            messagebox.showerror("Error", "Please enter a valid digit to update stock.")
            return

        row = self.inventory.search_by_id(prod_id)
        if not row:
            messagebox.showerror("Error", "No product found with ID input.")
            return

        current_stock = row[3]
        new_stock = current_stock + int(new_stock)

        if self.inventory.update_stock(prod_id, int(new_stock)):
            self.status_label.configure(text=f"Stock for {prod_id} updated successfully by value.")
            self.load_table_data()
            self.entry_new_stock.delete(0, 'end')
        else:
            messagebox.showerror("Error", f"No product found with ID: {prod_id}")
    
    def update_stockdec(self):
        prod_id = self.action_id.get().strip()
        new_stock = self.entry_new_stock.get().strip()

        if not prod_id:
            messagebox.showerror("Error", f"No product found with ID: {prod_id}")
            return
        
        if not new_stock.isdigit():
            messagebox.showerror("Error", "Please enter a valid digit to update stock.")
            return
        
        row = self.inventory.search_by_id(prod_id)
        if not row:
            messagebox.showerror("Error", "No product found with ID input.")
            return

        current_stock = row[3]
        decrement = int(new_stock)

        if decrement > current_stock:
            messagebox.showerror("Error", "Cannot reduce stock below 0")
            return
        
        new_stock = current_stock - decrement

        if self.inventory.update_stock(prod_id, int(new_stock)):
            self.status_label.configure(text=f"Stock for {prod_id} updated successfully by value.")
            self.load_table_data()
            self.entry_new_stock.delete(0, 'end')
        else:
            messagebox.showerror("Error", f"No product found with ID: {prod_id}")

    def update_name(self):
        prod_id = self.action_id.get().strip()
        new_name = self.entry_new_name.get().strip()

        if not prod_id or not new_name:
            messagebox.showerror("Error", "Please supply both Product ID and New Name value.")
            return

        if self.inventory.update_name(prod_id, new_name):
            messagebox.showinfo("Success", "Product name changed successfully.")
            self.load_table_data()
            self.entry_new_name.delete(0, 'end')
        else:
            messagebox.showerror("Error", f"No product found with ID: {prod_id}")

    def delete_item(self):
        prod_id = self.action_id.get().strip()
        if not prod_id:
            messagebox.showerror("Error", "Please enter a Product ID to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you absolutely sure you want to delete ID {prod_id}?")
        if confirm:
            if self.inventory.delete_product(prod_id):
                messagebox.showinfo("Deleted", "Product dropped from system registry.")
                self.load_table_data()
                self.action_id.delete(0, 'end')
            else:
                messagebox.showerror("Error", f"No product found with ID: {prod_id}")

    def sort_table(self, choice):
        column = self.sort_options.get(choice)
        if not column:
            return
        
        rows = self.inventory.sort_by(column)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4] if row[4] else "Null"))


if __name__ == "__main__":
    # Make sure you install customtkinter before running: pip install customtkinter
    db_inventory = Inventory()
    app = InventoryGUI(db_inventory)
    app.mainloop()