# ui/statistics.py





import customtkinter as ctk
from tkinter import messagebox, ttk
from typing import Any, List, Tuple


# internal modules import in list order >>easy to read
from core.statistics_handler import (
    get_sales_by_branch,
    get_distribution_history,
    get_branch_inventory
)
from core.session import get_session
from utils.chart_utils import (
    plot_sales_bar_chart,
    plot_sales_horizontal_chart,
    plot_sales_pie_chart,
    plot_sales_chart,
    plot_stacked_bar_chart,
    plot_line_chart
)


class StatisticsScreen:
    def __init__(self, parent: Any) -> None:
        self.parent = parent
        self.session = get_session()
        if self.session["role"] not in ("ADMIN", "STAFF"):
            messagebox.showerror("Access Denied", "You do not have permission to view statistics.")
            return

        self.window = ctk.CTkToplevel(parent)
        self.window.title("Enhanced Statistics")
        self.window.geometry("1000x600")
        self.window.resizable(False, False)

        self.build_ui()

    def build_ui(self) -> None:
        # Main wrapper frame
        self.main_frame = ctk.CTkFrame(self.window, width=950, height=520, corner_radius=15, fg_color="#1a1a1a")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Build sidebar and content areas
        self.build_sidebar()
        self.build_tabview()

        # Back button
        back_button = ctk.CTkButton(
            master=self.content_frame,
            text="Back",
            font=("Century Gothic", 18),
            fg_color="#007fff",
            hover_color="#005dc1",
            corner_radius=8,
            height=40,
            command=self.go_back
        )
        back_button.pack(pady=(10, 20))

    def build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(master=self.main_frame, width=200, fg_color="#2a2d2e", corner_radius=10)
        self.sidebar.pack(side="left", fill="y", padx=(10, 5), pady=10)

        ctk.CTkLabel(
            self.sidebar,
            text="Charts",
            font=("Century Gothic", 18, "bold"),
            anchor="w"
        ).pack(pady=(20, 10), padx=20, fill="x")

        # Prepare sales data for chart functions
        sales_data = get_sales_by_branch()
        self.sales_dict = {f"{row[0]} | {row[1]}": row[2] for row in sales_data}

        # Sample functions for stacked and line charts
        def show_stacked_chart() -> None:
            sample_data = {
                "Branch 1": {"Sales": 10, "Distributions": 20},
                "Branch 2": {"Sales": 8, "Distributions": 16}
            }
            plot_stacked_bar_chart(sample_data, "Sales vs Distributions")

        def show_line_chart() -> None:
            trends = {
                "Sales": [5, 10, 15, 8],
                "Distributions": [10, 12, 18, 14]
            }
            time_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]
            plot_line_chart(trends, time_labels, "Weekly Trend", "Total")

        # Define chart buttons with corresponding actions , also copy the image logo and see it it works wit ctk 
        nav_buttons: List[Tuple[str, Any]] = [
            ("📈 Sales Chart (Vertical)", lambda: plot_sales_chart(self.sales_dict)),
            ("📊 Bar Chart", lambda: plot_sales_bar_chart(self.sales_dict)),
            ("📉 Horizontal Bar", lambda: plot_sales_horizontal_chart(self.sales_dict)),
            ("🧁 Pie Chart", lambda: plot_sales_pie_chart(self.sales_dict)),
            ("📊 Stacked Bar (Sample)", show_stacked_chart),
            ("📉 Line Chart (Sample)", show_line_chart)
        ]
        for text, command in nav_buttons:
            ctk.CTkButton(
                master=self.sidebar,
                text=text,
                font=("Century Gothic", 16),
                fg_color="transparent",
                hover_color="#212121",
                anchor="w",
                command=command
            ).pack(pady=10, padx=10, fill="x")

    def build_tabview(self) -> None:
        self.content_frame = ctk.CTkFrame(master=self.main_frame, fg_color="#1a1a1a", corner_radius=10)
        self.content_frame.pack(side="left", fill="both", expand=True, pady=10, padx=(0, 10))

        self.tabview = ctk.CTkTabview(self.content_frame, width=720, height=440, corner_radius=10, fg_color="#2a2d2e")
        self.tabview.pack(pady=20, padx=20, fill="both", expand=True)

        self.sales_tab = self.tabview.add("Sales by Branch")
        self.dist_tab = self.tabview.add("Distribution History")
        self.inventory_tab = self.tabview.add("Branch Inventory")

        # Build tables for each tab
        self.build_table(self.sales_tab, ["Branch", "Good", "Total Sold"], get_sales_by_branch())
        self.build_table(self.dist_tab, ["Good", "From", "To", "Quantity", "Date", "User"], get_distribution_history())
        self.build_table(self.inventory_tab, ["Branch", "Good", "Quantity"], get_branch_inventory())

    def build_table(self, container: ctk.CTkFrame, columns: List[str], data: List[Tuple]) -> None:
        """Builds a Treeview table in the given container."""
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2a2d2e",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#2a2d2e",
                        bordercolor="#2a2d2e",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#007fff')])
        style.configure("Treeview.Heading", background="#444", foreground="white", relief="flat")
        style.map("Treeview.Heading", background=[('active', '#555')])

        outer_frame = ctk.CTkFrame(container, fg_color="transparent")
        outer_frame.pack(fill="both", expand=True, padx=10, pady=10)
        outer_frame.pack_propagate(False)

        vsb = ttk.Scrollbar(outer_frame, orient="vertical")
        hsb = ttk.Scrollbar(outer_frame, orient="horizontal")
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        tree = ttk.Treeview(outer_frame, columns=columns, show='headings',
                            yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)

        for row in data:
            tree.insert("", "end", values=row)

        tree.pack(fill="both", expand=True)

    def refresh_tables(self) -> None:
        """Refreshes all table data by re-fetching from the database."""
        # clear and rebuild each table;  enhance this method to update existing tables instead or use a refresh button !!
        for tab, columns, data_func in [
            (self.sales_tab, ["Branch", "Good", "Total Sold"], get_sales_by_branch),
            (self.dist_tab, ["Good", "From", "To", "Quantity", "Date", "User"], get_distribution_history),
            (self.inventory_tab, ["Branch", "Good", "Quantity"], get_branch_inventory)
        ]:
            # Clear the container and rebuild table
            for widget in tab.winfo_children():
                widget.destroy()
            self.build_table(tab, columns, data_func())

    def go_back(self) -> None:
        self.window.destroy()
        self.parent.deiconify()
        # Navigate back to the main menu if desired:
        from ui.main_menu import MainMenuScreen
        MainMenuScreen(self.parent)



# if __name__ == "__main__":
#     import customtkinter as ctk
#     root = ctk.CTk()
#     StatisticsScreen(root)
#     root.mainloop()
