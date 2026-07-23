import sqlite3
import time
import customtkinter as ctk
from tkinter import ttk, messagebox

# Set GUI Theme
ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"


# ==========================================
# DATABASE BACKEND CLASS (INVENTORY)
# ==========================================
class Inventory:
    def __init__(self, db_file="inventory.db", table_name="products"):
        self.db_file = db_file
        self.table_name = table_name
        self.create_table_if_missing()

    def create_table_if_missing(self):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.table_name}
                   (prodname TEXT NOT NULL,
                    timemade TEXT NOT NULL,
                    prodcat TEXT NOT NULL,
                    prodid TEXT PRIMARY KEY NOT NULL,
                    prodstock INTEGER NOT NULL,
                    prodopid TEXT);''')
            connection.commit()

    def add_item(self, name, timemade, category, prod_id, stock, optional_id=None):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            if optional_id in (None, "", "None"):
                cursor.execute(
                    f"INSERT INTO {self.table_name} (prodName, timemade, prodcat, prodID, prodStock) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (name, timemade, category, prod_id, stock),
                )
            else:
                cursor.execute(
                    f"INSERT INTO {self.table_name} (prodName, timemade, prodcat, prodID, prodStock, prodopid) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (name, timemade, category, prod_id, stock, optional_id),
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
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE prodID = ?", (prod_id,)
            )
            return cursor.fetchone()

    def update_time(self, prod_id, new_time):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"UPDATE {self.table_name} SET timemade = ? WHERE prodID = ?",
                (new_time, prod_id),
            )
            connection.commit()
            return cursor.rowcount > 0

    def update_stock(self, prod_id, new_stock):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"UPDATE {self.table_name} SET prodStock = ? WHERE prodID = ?",
                (new_stock, prod_id),
            )
            connection.commit()
            return cursor.rowcount > 0

    def delete_product(self, prod_id):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"DELETE FROM {self.table_name} WHERE prodID = ?", (prod_id,)
            )
            connection.commit()
            return cursor.rowcount > 0

    def update_name(self, prod_id, new_name):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"UPDATE {self.table_name} SET prodname = ? WHERE prodID = ?", (new_name, prod_id)
            )
            connection.commit()
            return cursor.rowcount > 0

    def sort_by(self, category):
        columns = {"prodname", "timemade", "prodcat", "prodid", "prodstock"}
        if category not in columns:
            raise ValueError(f"Invalid sort column: {category}")

        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY {category}")
            return cursor.fetchall()


# ==========================================
# CUSTOMTKINTER GUI APPLICATION
# ==========================================
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

        self.title("Goodwill Inventory Management System")
        self.geometry("950x650")
        self.minsize(850, 550)

        # Configure Main Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header Title
        self.header = ctk.CTkLabel(
            self, 
            text="Goodwill Inventory System", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.header.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        # Tabview Setup
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.tab_view_all = self.tabview.add("View & Manage Inventory")
        self.tab_add_item = self.tabview.add("Add New Product")

        # Build Tab Content
        self.setup_view_tab()
        self.setup_add_tab()

        # Load Data on Startup
        self.refresh_table()

    # ------------------------------------------
    # TIME HELPER
    # ------------------------------------------
    def get_current_formatted_time(self):
        clock = time.localtime()
        format_min = time.strftime("%M", clock)
        return f"{clock.tm_mon}-{clock.tm_mday}-{clock.tm_year} at {clock.tm_hour}:{format_min}"

    # ------------------------------------------
    # TAB 1: VIEW & MANAGE INVENTORY
    # ------------------------------------------
    def setup_view_tab(self):
        self.tab_view_all.grid_columnconfigure(0, weight=1)
        self.tab_view_all.grid_rowconfigure(1, weight=1)

        # Top Control Bar (Search & Sort)
        control_frame = ctk.CTkFrame(self.tab_view_all)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Search Controls
        ctk.CTkLabel(control_frame, text="Search ID:").pack(side="left", padx=(10, 2))
        self.search_entry = ctk.CTkEntry(control_frame, placeholder_text="Enter Product ID", width=140)
        self.search_entry.pack(side="left", padx=5)

        search_btn = ctk.CTkButton(control_frame, text="Search", width=80, command=self.search_item)
        search_btn.pack(side="left", padx=5)

        reset_btn = ctk.CTkButton(control_frame, text="Reset / Refresh", fg_color="gray", width=110, command=self.refresh_table)
        reset_btn.pack(side="left", padx=5)

        # Sort Controls
        self.sort_option = ctk.CTkOptionMenu(
            control_frame, 
            values=["Default", "Name", "Time", "Category", "Product ID", "Stock"],
            command=self.sort_table
        )
        self.sort_option.pack(side="right", padx=10)
        ctk.CTkLabel(control_frame, text="Sort By:").pack(side="right", padx=2)

        # Table Display (Using standard ttk.Treeview styled for CustomTkinter)
        table_frame = ctk.CTkFrame(self.tab_view_all)
        table_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=('Helvetica', 10), rowheight=28, background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white")
        style.configure("Treeview.Heading", font=('Helvetica', 11, 'bold'), background="#1f1f1f", foreground="white")
        style.map("Treeview", background=[('selected', '#1f538d')])

        columns = ("Name", "Time Modified", "Category", "Product ID", "Stock", "Optional ID")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        scrollbar = ctk.CTkScrollbar(table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Bottom Action Bar (Update / Delete)
        action_frame = ctk.CTkFrame(self.tab_view_all)
        action_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkButton(action_frame, text="Update Stock", command=self.open_update_stock_dialog).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(action_frame, text="Update Name", command=self.open_update_name_dialog).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(action_frame, text="Delete Product", fg_color="#c0392b", hover_color="#e74c3c", command=self.delete_item).pack(side="right", padx=10, pady=10)

    # ------------------------------------------
    # TAB 2: ADD NEW PRODUCT
    # ------------------------------------------
    def setup_add_tab(self):
        form_frame = ctk.CTkFrame(self.tab_add_item)
        form_frame.pack(padx=40, pady=20, fill="both", expand=True)

        # Form Inputs
        ctk.CTkLabel(form_frame, text="Product Name:").grid(row=0, column=0, padx=20, pady=12, sticky="w")
        self.entry_name = ctk.CTkEntry(form_frame, width=250)
        self.entry_name.grid(row=0, column=1, padx=20, pady=12)

        ctk.CTkLabel(form_frame, text="Category:").grid(row=1, column=0, padx=20, pady=12, sticky="w")
        self.combo_category = ctk.CTkOptionMenu(form_frame, values=self.CATEGORIES, width=250)
        self.combo_category.grid(row=1, column=1, padx=20, pady=12)

        ctk.CTkLabel(form_frame, text="Product ID (Unique):").grid(row=2, column=0, padx=20, pady=12, sticky="w")
        self.entry_id = ctk.CTkEntry(form_frame, width=250)
        self.entry_id.grid(row=2, column=1, padx=20, pady=12)

        ctk.CTkLabel(form_frame, text="Initial Stock Quantity:").grid(row=3, column=0, padx=20, pady=12, sticky="w")
        self.entry_stock = ctk.CTkEntry(form_frame, width=250)
        self.entry_stock.grid(row=3, column=1, padx=20, pady=12)

        ctk.CTkLabel(form_frame, text="Optional Extra ID:").grid(row=4, column=0, padx=20, pady=12, sticky="w")
        self.entry_opt_id = ctk.CTkEntry(form_frame, width=250)
        self.entry_opt_id.grid(row=4, column=1, padx=20, pady=12)

        # Submit Button
        btn_add = ctk.CTkButton(form_frame, text="Add Product to Database", command=self.add_item, width=200, height=40)
        btn_add.grid(row=5, column=0, columnspan=2, pady=25)

    # ------------------------------------------
    # LOGIC & EVENT HANDLERS
    # ------------------------------------------
    def populate_treeview(self, rows):
        """Clears and re-populates the Treeview rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            # Handle empty optional IDs cleanly
            formatted_row = list(row)
            if not formatted_row[5] or formatted_row[5] == "None":
                formatted_row[5] = "N/A"
            self.tree.insert("", "end", values=formatted_row)

    def refresh_table(self):
        self.search_entry.delete(0, 'end')
        self.sort_option.set("Default")
        rows = self.inventory.get_all_rows()
        self.populate_treeview(rows)

    def search_item(self):
        prod_id = self.search_entry.get().strip()
        if not prod_id:
            messagebox.showwarning("Search Error", "Please enter a Product ID to search.")
            return

        row = self.inventory.search_by_id(prod_id)
        if row:
            self.populate_treeview([row])
        else:
            messagebox.showinfo("Not Found", f"No product found with ID: {prod_id}")

    def sort_table(self, choice):
        mapping = {
            "Name": "prodname",
            "Time": "timemade",
            "Category": "prodcat",
            "Product ID": "prodid",
            "Stock": "prodstock"
        }
        if choice in mapping:
            rows = self.inventory.sort_by(mapping[choice])
            self.populate_treeview(rows)
        else:
            self.refresh_table()

    def add_item(self):
        name = self.entry_name.get().strip()
        category = self.combo_category.get()
        prod_id = self.entry_id.get().strip()
        stock = self.entry_stock.get().strip()
        opt_id = self.entry_opt_id.get().strip()

        if not name or not prod_id or not stock:
            messagebox.showerror("Input Error", "Name, Product ID, and Stock fields are required.")
            return

        if not stock.isdigit():
            messagebox.showerror("Input Error", "Stock must be a valid non-negative integer.")
            return

        timemade = self.get_current_formatted_time()
        optional_id = None if opt_id == "" else opt_id

        try:
            self.inventory.add_item(name, timemade, category, prod_id, int(stock), optional_id)
            messagebox.showinfo("Success", "Product added successfully!")
            
            # Reset Inputs
            self.entry_name.delete(0, 'end')
            self.entry_id.delete(0, 'end')
            self.entry_stock.delete(0, 'end')
            self.entry_opt_id.delete(0, 'end')
            
            self.refresh_table()
            self.tabview.set("View & Manage Inventory")
        except sqlite3.IntegrityError:
            messagebox.showerror("Database Error", f"Product ID '{prod_id}' already exists!")

    def get_selected_product_id(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please click on a row in the table first.")
            return None
        row_values = self.tree.item(selected_item[0], 'values')
        return row_values[3]  # Index 3 is prodID

    def open_update_stock_dialog(self):
        prod_id = self.get_selected_product_id()
        if not prod_id:
            return

        dialog = ctk.CTkInputDialog(text=f"Enter new stock amount for Product ID '{prod_id}':", title="Update Stock")
        new_stock = dialog.get_input()

        if new_stock is not None:
            if new_stock.isdigit():
                new_time = self.get_current_formatted_time()
                self.inventory.update_stock(prod_id, int(new_stock))
                self.inventory.update_time(prod_id, new_time)
                self.refresh_table()
                messagebox.showinfo("Success", f"Stock updated to {new_stock}")
            else:
                messagebox.showerror("Error", "Invalid numeric stock value.")

    def open_update_name_dialog(self):
        prod_id = self.get_selected_product_id()
        if not prod_id:
            return

        dialog = ctk.CTkInputDialog(text=f"Enter new name for Product ID '{prod_id}':", title="Update Name")
        new_name = dialog.get_input()

        if new_name and new_name.strip():
            new_time = self.get_current_formatted_time()
            self.inventory.update_name(prod_id, new_name.strip())
            self.inventory.update_time(prod_id, new_time)
            self.refresh_table()
            messagebox.showinfo("Success", f"Product name changed to '{new_name.strip()}'")

    def delete_item(self):
        prod_id = self.get_selected_product_id()
        if not prod_id:
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Product ID '{prod_id}'?")
        if confirm:
            self.inventory.delete_product(prod_id)
            self.refresh_table()
            messagebox.showinfo("Deleted", "Product deleted successfully.")


# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    app_inventory = Inventory()
    app = InventoryGUI(app_inventory)
    app.mainloop()