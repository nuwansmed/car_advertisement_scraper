# main.py

import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper import scrape_ikman_cars, scrape_riyasewana_cars

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='scraping.log'
)

class CarScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Car Scraper Application")
        self.create_widgets()
        self.results = {}
        self.scrape_thread = None
        self.stop_scraping_flag = threading.Event()

    def create_widgets(self):
        # Create frames
        self.mode_frame = ttk.LabelFrame(self.root, text="Mode Selection")
        self.mode_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.output_frame = ttk.LabelFrame(self.root, text="Output")
        self.output_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.output_frame.columnconfigure(0, weight=1)
        self.output_frame.rowconfigure(0, weight=1)

        # Mode selection
        self.mode_var = tk.StringVar(value="csv")
        ttk.Radiobutton(self.mode_frame, text="CSV Mode", variable=self.mode_var, value="csv", command=self.toggle_mode).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(self.mode_frame, text="Scraping Mode", variable=self.mode_var, value="scrape", command=self.toggle_mode).grid(row=0, column=1, sticky="w")

        # Buttons
        self.load_button = ttk.Button(self.mode_frame, text="Load Data", command=self.load_data)
        self.load_button.grid(row=1, column=0, pady=5)

        self.scrape_button = ttk.Button(self.mode_frame, text="Start Scraping", command=self.open_scrape_params)
        self.scrape_button.grid(row=1, column=1, pady=5)

        self.filter_button = ttk.Button(self.mode_frame, text="Filter Results", command=self.filter_results, state="disabled")
        self.filter_button.grid(row=2, column=0, pady=5)

        self.exit_button = ttk.Button(self.mode_frame, text="Exit", command=self.root.quit)
        self.exit_button.grid(row=2, column=1, pady=5)

        # Output Text
        self.output_text = tk.Text(self.output_frame, wrap="word")
        self.output_text.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for the output text
        self.output_scrollbar = ttk.Scrollbar(self.output_frame, orient='vertical', command=self.output_text.yview)
        self.output_scrollbar.grid(row=0, column=1, sticky='ns')
        self.output_text.configure(yscrollcommand=self.output_scrollbar.set)

        # Initially disable scraping controls
        self.toggle_mode()

    def toggle_mode(self):
        mode = self.mode_var.get()
        if mode == "csv":
            self.load_button.config(state="normal")
            self.scrape_button.config(state="disabled")
        else:
            self.load_button.config(state="disabled")
            self.scrape_button.config(state="normal")

    def load_data(self):
        """Load test data from two CSV files."""
        try:
            # Load the CSV files into pandas DataFrames
            self.results['ikman.lk'] = pd.read_csv("ikman_cars_filtered.csv")
            self.results['riyasewana.com'] = pd.read_csv("riyasewana_cars_filtered.csv")

            # Display the number of records loaded from each site
            for site, df in self.results.items():
                num_records = len(df)
                self.output_text.insert(tk.END, f"{site}: {num_records} records loaded.\n")

            self.filter_button.config(state="normal")
        except FileNotFoundError as e:
            messagebox.showerror("File Not Found", f"Error: {e}")
            logging.error(f"File not found: {e}")

    def open_scrape_params(self):
        """Open a new window to input scraping parameters."""
        self.scrape_params_window = tk.Toplevel(self.root)
        self.scrape_params_window.title("Scraping Parameters")

        # Define options
        district_names = [
            'colombo', 'gampaha', 'kalutara', 'kandy', 'matale', 'nuwara eliya',
            'galle', 'matara', 'hambantota', 'jaffna', 'kilinochchi', 'mannar',
            'vavuniya', 'mullaitivu', 'batticaloa', 'ampara', 'trincomalee',
            'kurunegala', 'puttalam', 'anuradhapura', 'polonnaruwa', 'badulla',
            'moneragala', 'ratnapura', 'kegalle'
        ]
        fuel_types = ['petrol', 'diesel', 'hybrid', 'electric']
        transmissions = ['automatic', 'manual']

        # Input fields
        labels = [
            "District", "Min Price", "Max Price", "Brand",
            "Min Year", "Max Year", "Fuel Type", "Transmission",
            "Pages to Scrape (ikman.lk)", "Pages to Scrape (riyasewana.com)"
        ]
        defaults = [
            "colombo", "100", "100000000", "toyota",
            "1980", "2024", "petrol", "automatic",
            "1", "1"
        ]

        self.scrape_entries = {}
        for i, (label_text, default_value) in enumerate(zip(labels, defaults)):
            ttk.Label(self.scrape_params_window, text=f"{label_text}:").grid(row=i, column=0, sticky="e")

            if label_text == "District":
                combobox = ttk.Combobox(self.scrape_params_window, values=district_names)
                combobox.set(default_value)
                combobox.grid(row=i, column=1, padx=5, pady=5)
                self.scrape_entries[label_text] = combobox
            elif label_text == "Fuel Type":
                combobox = ttk.Combobox(self.scrape_params_window, values=fuel_types)
                combobox.set(default_value)
                combobox.grid(row=i, column=1, padx=5, pady=5)
                self.scrape_entries[label_text] = combobox
            elif label_text == "Transmission":
                combobox = ttk.Combobox(self.scrape_params_window, values=transmissions)
                combobox.set(default_value)
                combobox.grid(row=i, column=1, padx=5, pady=5)
                self.scrape_entries[label_text] = combobox
            else:
                entry = ttk.Entry(self.scrape_params_window)
                entry.insert(0, default_value)
                entry.grid(row=i, column=1, padx=5, pady=5)
                self.scrape_entries[label_text] = entry

        # Start/Stop Scraping Button
        self.start_stop_button = ttk.Button(self.scrape_params_window, text="Start Scraping", command=self.start_stop_scraping)
        self.start_stop_button.grid(row=len(labels), column=0, columnspan=2, pady=10)

        # Close Window Button
        ttk.Button(self.scrape_params_window, text="Close", command=self.scrape_params_window.destroy).grid(row=len(labels)+1, column=0, columnspan=2, pady=5)

        # Reset stop flag
        self.stop_scraping_flag.clear()

    def start_stop_scraping(self):
        if self.start_stop_button.config('text')[-1] == 'Start Scraping':
            # Collect parameters
            self.district = self.scrape_entries['District'].get()
            self.min_price = self.scrape_entries['Min Price'].get()
            self.max_price = self.scrape_entries['Max Price'].get()
            self.brand = self.scrape_entries['Brand'].get()
            self.min_yom = self.scrape_entries['Min Year'].get()
            self.max_yom = self.scrape_entries['Max Year'].get()
            self.fuel_type = self.scrape_entries['Fuel Type'].get()
            self.transmission = self.scrape_entries['Transmission'].get()
            pages_to_scrape_ikman = self.scrape_entries['Pages to Scrape (ikman.lk)'].get()
            pages_to_scrape_riyasewana = self.scrape_entries['Pages to Scrape (riyasewana.com)'].get()

            # Validate numerical inputs
            try:
                self.pages_to_scrape_ikman = int(pages_to_scrape_ikman)
            except ValueError:
                messagebox.showerror("Input Error", "Invalid input for pages to scrape from ikman.lk. Using default value of 1.")
                self.pages_to_scrape_ikman = 1

            try:
                self.pages_to_scrape_riyasewana = int(pages_to_scrape_riyasewana)
            except ValueError:
                messagebox.showerror("Input Error", "Invalid input for pages to scrape from riyasewana.com. Using default value of 1.")
                self.pages_to_scrape_riyasewana = 1

            # Start scraping in a new thread
            self.scrape_thread = threading.Thread(target=self.scrape_data)
            self.scrape_thread.start()

            # Update button to "Stop Scraping"
            self.start_stop_button.config(text="Stop Scraping")
            self.output_text.insert(tk.END, "Starting scraping process...\n")
            self.output_text.see(tk.END)
        else:
            # Stop scraping
            self.stop_scraping_flag.set()
            self.output_text.insert(tk.END, "Stopping scraping process...\n")
            self.output_text.see(tk.END)
            self.start_stop_button.config(state="disabled")

    def scrape_data(self):
        # Define the functions to run in parallel
        def scrape_ikman():
            if self.stop_scraping_flag.is_set():
                return None
            logging.info("Starting scrape_ikman_cars")
            df = scrape_ikman_cars(
                self.district, self.min_price, self.max_price, self.brand, self.min_yom,
                self.max_yom, self.fuel_type, self.transmission, self.pages_to_scrape_ikman,
                output_csv="ikman_cars_filtered.csv", stop_flag=self.stop_scraping_flag  # Pass the stop flag
            )
            logging.info("Completed scrape_ikman_cars")
            return df

        def scrape_riyasewana():
            if self.stop_scraping_flag.is_set():
                return None
            logging.info("Starting scrape_riyasewana_cars")
            df = scrape_riyasewana_cars(
                self.district, self.min_price, self.max_price, self.brand, self.min_yom,
                self.max_yom, self.fuel_type, self.transmission, self.pages_to_scrape_riyasewana,
                output_csv="riyasewana_cars_filtered.csv", stop_flag=self.stop_scraping_flag  # Pass the stop flag
            )
            logging.info("Completed scrape_riyasewana_cars")
            return df

        # Run the scrapers
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(scrape_ikman): 'ikman.lk',
                executor.submit(scrape_riyasewana): 'riyasewana.com'
            }

            # Collect the results as they complete
            for future in as_completed(futures):
                site = futures[future]
                try:
                    result_df = future.result()
                    if result_df is None:
                        self.output_text.insert(tk.END, f"Scraping {site} was stopped by user.\n")
                        self.results[site] = None
                    else:
                        self.results[site] = result_df
                        logging.info(f"Scraping {site} completed successfully.")
                        self.output_text.insert(tk.END, f"Scraping {site} completed successfully.\n")
                except Exception as e:
                    logging.error(f"An error occurred while scraping {site}: {e}")
                    self.output_text.insert(tk.END, f"An error occurred while scraping {site}: {e}\n")
                    self.results[site] = None

        self.on_scraping_complete()

    def on_scraping_complete(self):
        self.output_text.insert(tk.END, "Scraping tasks have completed.\n")
        self.output_text.see(tk.END)
        self.filter_button.config(state="normal")
        self.start_stop_button.config(text="Start Scraping", state="normal")

        # Show the number of records obtained for each site
        for site, df in self.results.items():
            if df is not None and not df.empty:
                num_records = len(df)
                self.output_text.insert(tk.END, f"Number of records obtained from {site}: {num_records}\n")
            else:
                self.output_text.insert(tk.END, f"No data obtained from {site}.\n")

        self.output_text.see(tk.END)

    def filter_results(self):
        """Open a new window for filtering the loaded data."""
        self.filter_window = tk.Toplevel(self.root)
        self.filter_window.title("Filter Results")

        # Filtering options
        ttk.Label(self.filter_window, text="Model name (or part):").grid(row=0, column=0, sticky="e")
        self.model_entry = ttk.Entry(self.filter_window)
        self.model_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.filter_window, text="Mileage Min:").grid(row=1, column=0, sticky="e")
        self.mileage_min_entry = ttk.Entry(self.filter_window)
        self.mileage_min_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.filter_window, text="Mileage Max:").grid(row=2, column=0, sticky="e")
        self.mileage_max_entry = ttk.Entry(self.filter_window)
        self.mileage_max_entry.grid(row=2, column=1, padx=5, pady=5)

        # Apply filter button
        ttk.Button(self.filter_window, text="Apply Filter", command=self.apply_filter).grid(row=3, column=0, columnspan=2, pady=10)

        # Close window button
        ttk.Button(self.filter_window, text="Close", command=self.filter_window.destroy).grid(row=4, column=0, columnspan=2, pady=5)

    def apply_filter(self):
        """Apply filters to the data based on user input."""
        model_name = self.model_entry.get().strip().lower()
        mileage_min_input = self.mileage_min_entry.get().strip()
        mileage_max_input = self.mileage_max_entry.get().strip()

        # Convert mileage inputs to integers, handle exceptions
        mileage_min = None
        mileage_max = None
        try:
            if mileage_min_input:
                mileage_min = int(mileage_min_input)
        except ValueError:
            messagebox.showerror("Input Error", "Invalid input for Mileage Min. Ignoring minimum filter.")

        try:
            if mileage_max_input:
                mileage_max = int(mileage_max_input)
        except ValueError:
            messagebox.showerror("Input Error", "Invalid input for Mileage Max. Ignoring maximum filter.")

        # Apply filters to both datasets
        for site, df in self.results.items():
            if df is not None and not df.empty:
                df_filtered = df.copy()

                # Convert relevant columns to the appropriate types
                df_filtered['Model'] = df_filtered['Model'].astype(str).str.lower()
                df_filtered['Mileage'] = pd.to_numeric(df_filtered['Mileage'], errors='coerce')
                df_filtered['Price'] = pd.to_numeric(df_filtered['Price'], errors='coerce')

                # Apply model filter
                if model_name:
                    df_filtered = df_filtered[df_filtered['Model'].str.contains(model_name, na=False)]

                # Apply mileage filters
                if mileage_min is not None:
                    df_filtered = df_filtered[df_filtered['Mileage'] >= mileage_min]
                if mileage_max is not None:
                    df_filtered = df_filtered[df_filtered['Mileage'] <= mileage_max]

                # Display the number of records and average price
                num_filtered = len(df_filtered)
                self.output_text.insert(tk.END, f"{site}: {num_filtered} records after filtering.\n")

                if not df_filtered.empty:
                    average_price = df_filtered['Price'].mean()
                    self.output_text.insert(tk.END, f"Average price for {site}: {average_price:.2f}\n")
                else:
                    self.output_text.insert(tk.END, f"No matching records found for {site}.\n")
            else:
                self.output_text.insert(tk.END, f"No data from {site} to filter.\n")

        self.filter_window.destroy()
        self.output_text.see(tk.END)

    def on_closing(self):
        # Stop any running threads
        if self.scrape_thread and self.scrape_thread.is_alive():
            self.stop_scraping_flag.set()
            self.scrape_thread.join()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CarScraperGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
