# Car Advertisement Scraper Application

## Overview

The Car Scraper Application is a Python-based GUI application designed to scrape car listings from two popular Sri Lankan websites: [ikman.lk](https://ikman.lk/) and [riyasewana.com](https://riyasewana.com/). The application allows users to:

- **Specify search parameters**: District, price range, brand, year of manufacture, fuel type, transmission type, and the number of pages to scrape.
- **Start and stop the scraping process**: Users can interrupt the scraping at any time.
- **Load and filter data**: After scraping, users can filter the results based on model name and mileage, and calculate the average price.
- **Save results**: The scraped data can be saved to CSV files for further analysis.

This application leverages various Python technologies and logical concepts to provide a responsive and user-friendly experience.

---

## Table of Contents

- [Technologies Used](#technologies-used)
- [Application Structure](#application-structure)
  - [GUI with Tkinter](#gui-with-tkinter)
  - [Multithreading](#multithreading)
  - [Web Scraping](#web-scraping)
  - [Data Handling with Pandas](#data-handling-with-pandas)
- [Features](#features)
  - [Mode Selection](#mode-selection)
  - [Scraping Parameters](#scraping-parameters)
  - [Start/Stop Scraping](#startstop-scraping)
  - [Filtering Results](#filtering-results)
- [How to Run the Application](#how-to-run-the-application)
- [Dependencies](#dependencies)
- [Code Breakdown](#code-breakdown)
  - [main.py](#mainpy)
  - [car_scraper.py](#car_scraperpy)
- [Conclusion](#conclusion)

---

## Technologies Used

- **Python 3.x**: The core programming language used for the application.
- **Tkinter**: A standard GUI library in Python for creating graphical user interfaces.
- **Requests**: A Python HTTP library used for sending HTTP requests to websites.
- **BeautifulSoup**: A library for parsing HTML and XML documents, used here to parse web pages.
- **Pandas**: A data analysis library used for data manipulation and analysis.
- **Threading**: Python's threading module is used to run tasks in separate threads.
- **Concurrent Futures**: Specifically, `ThreadPoolExecutor` for managing a pool of threads.
- **Logging**: Python's logging module for logging events that occur during the execution of the program.

---

## Application Structure

### GUI with Tkinter

The application uses Tkinter to create a graphical user interface. Key components of the GUI include:

- **Mode Selection**: Allows users to choose between "CSV Mode" (loading data from CSV files) and "Scraping Mode" (scraping data from websites).
- **Output Frame**: Displays messages and results to the user.
- **Buttons and Input Fields**: Users can input search parameters, start/stop scraping, load data, and filter results.

### Multithreading

- **Threading Module**: The application uses the `threading` module to run the scraping functions in separate threads. This ensures that the GUI remains responsive while the scraping tasks are running.
- **Stop Flag**: A `threading.Event` object is used as a stop flag to gracefully terminate the scraping process when the user requests it.
- **ThreadPoolExecutor**: The `concurrent.futures.ThreadPoolExecutor` is used to manage threads that run the scraping functions for both websites concurrently.

### Web Scraping

- **Requests Library**: Used to send HTTP requests to the target websites and retrieve the HTML content.
- **BeautifulSoup**: Parses the HTML content to extract relevant data such as price, brand, model, year, etc.
- **Respectful Scraping**: The application includes `time.sleep(1)` calls to avoid overwhelming the target websites with requests.

### Data Handling with Pandas

- **DataFrames**: Scraped data is stored in Pandas DataFrames for easy manipulation and analysis.
- **CSV Export**: DataFrames can be exported to CSV files for external use.
- **Filtering**: Users can filter the data based on model name and mileage, and compute the average price.

---

## Features

### Mode Selection

Upon launching the application, users can select between:

- **CSV Mode**: Load existing data from CSV files (`ikman_cars_filtered.csv` and `riyasewana_cars_filtered.csv`).
- **Scraping Mode**: Scrape new data from the websites based on user-defined parameters.

### Scraping Parameters

In Scraping Mode, users can input the following parameters:

- **District**: Selected from a dropdown list of districts in Sri Lanka.
- **Min Price and Max Price**: Define the price range of the cars.
- **Brand**: Specify the car brand (e.g., Toyota, Nissan).
- **Min Year and Max Year**: Define the range of the year of manufacture.
- **Fuel Type**: Choose from `petrol`, `diesel`, `hybrid`, or `electric`.
- **Transmission**: Choose from `automatic` or `manual`.
- **Pages to Scrape**: Specify the number of pages to scrape from each website.

### Start/Stop Scraping

- **Start Scraping**: Begins the scraping process in a separate thread to keep the GUI responsive.
- **Stop Scraping**: Users can interrupt the scraping process at any time. The application uses a stop flag to gracefully terminate ongoing scraping tasks.

### Filtering Results

After scraping or loading data, users can:

- **Filter by Model Name**: Enter a model name or part of it to filter the results.
- **Filter by Mileage**: Specify minimum and/or maximum mileage to filter the cars.
- **View Results**: The application displays the number of records after filtering and calculates the average price.

---

## How to Run the Application

1. **Clone the Repository**: Download or clone the project files to your local machine.
2. **Install Dependencies**: Ensure all required Python libraries are installed:
   ```bash
   pip install requests beautifulsoup4 pandas
   ```
3. **Run the Application**: Execute the `main.py` file:
   ```bash
   python main.py
   ```
4. **Use the GUI**:
   - **Select Mode**: Choose between CSV Mode and Scraping Mode.
   - **Input Parameters**: If scraping, input the desired parameters.
   - **Start Scraping**: Click the "Start Scraping" button.
   - **Stop Scraping**: Click "Stop Scraping" to interrupt.
   - **Filter Results**: After data is loaded or scraped, use the "Filter Results" button.

---

## Dependencies

- **Python 3.x**
- **requests**
- **beautifulsoup4**
- **pandas**
- **tkinter** (comes standard with Python installations on Windows and macOS)
- **concurrent.futures** (included in Python 3 standard library)
- **threading** (included in Python 3 standard library)
- **logging** (included in Python 3 standard library)

---

## Code Breakdown

### main.py

The `main.py` script contains the `CarScraperGUI` class, which manages the GUI and user interactions.

#### Key Components:

- **Initialization**: Sets up the main window and initializes variables.
- **create_widgets()**: Constructs the GUI elements, including frames, buttons, and input fields.
- **toggle_mode()**: Enables or disables buttons based on the selected mode.
- **load_data()**: Loads data from CSV files into Pandas DataFrames.
- **open_scrape_params()**: Opens a new window for users to input scraping parameters.
- **start_stop_scraping()**: Starts or stops the scraping process.
- **scrape_data()**: Manages the scraping threads and handles the results.
- **on_scraping_complete()**: Updates the GUI after scraping is finished.
- **filter_results()**: Opens a window for filtering data.
- **apply_filter()**: Applies filters to the data and displays the results.
- **on_closing()**: Ensures threads are terminated when the application is closed.

#### Technologies Used in main.py:

- **Tkinter Widgets**: `Tk`, `Toplevel`, `Label`, `Entry`, `Button`, `Combobox`, `Text`, `Scrollbar`.
- **Threading**: Used to run the scraping functions without freezing the GUI.
- **Concurrent Futures**: Manages threads for scraping functions.
- **Event Handling**: Start/Stop buttons and window close events.
- **Data Handling**: Pandas for data storage and manipulation.
- **Logging**: Records events and errors during scraping.

### car_scraper.py

The `car_scraper.py` script contains functions for scraping data from the websites.

#### Key Functions:

- **scrape_ikman_cars()**: Scrapes car listings from ikman.lk based on parameters.
- **get_ikman_ad_details()**: Extracts details from individual ikman.lk ad pages.
- **get_ikman_ads_from_page()**: Retrieves ad URLs from a page on ikman.lk.
- **construct_ikman_search_url()**: Builds the search URL with query parameters.
- **scrape_riyasewana_cars()**: Scrapes car listings from riyasewana.com based on parameters.
- **scrape_riyasewana_page()**: Processes a page of listings from riyasewana.com.
- **scrape_riyasewana_individual_listing()**: Extracts details from individual riyasewana.com ad pages.

#### Technologies Used in car_scraper.py:

- **Requests**: Sending HTTP requests to retrieve web pages.
- **BeautifulSoup**: Parsing HTML content to extract data.
- **Regular Expressions**: Cleaning and extracting numeric values from strings.
- **Time Module**: Introducing delays between requests to be respectful to the target websites.
- **Data Structures**: Using dictionaries and lists to store scraped data.
- **Pandas**: Converting data into DataFrames and saving to CSV files.
- **Threading Stop Flag**: Checking the stop flag to interrupt scraping when requested.

#### Logical Concepts:

- **Modular Design**: Separating scraping logic into distinct functions for maintainability.
- **Error Handling**: Try-except blocks to handle exceptions during scraping.
- **Data Mapping**: Aligning scraped data with the required fields for consistency.
- **Conditional Checks**: Ensuring the scraping process can be interrupted gracefully.

---

## Conclusion

The Car Scraper Application demonstrates the integration of GUI design, multithreading, web scraping, and data analysis in Python. By combining these technologies, the application provides a user-friendly interface for scraping and analyzing car listings from popular websites.

**Key Takeaways**:

- **GUI Responsiveness**: Using threading to keep the GUI responsive during long-running tasks.
- **Graceful Termination**: Implementing a stop flag to allow users to interrupt processes.
- **Data Management**: Leveraging Pandas for efficient data handling and analysis.
- **Web Scraping Ethics**: Including delays between requests to prevent overloading target websites.

---

**Note**: This application is intended for educational purposes. When scraping websites, always ensure compliance with the website's terms of service and legal regulations.