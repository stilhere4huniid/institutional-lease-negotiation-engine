# 📖 User Documentation

## How to Run the App locally

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/stilhere4huniid/institutional-lease-negotiation-engine.git](https://github.com/stilhere4huniid/institutional-lease-negotiation-engine.git)
    cd institutional-lease-negotiation-engine
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Generate Data (First Run Only):**
    * Open `Untitled.ipynb` in Jupyter Notebook.
    * Run all cells to generate `data/historical_leases.csv` and train the initial model.

4.  **Launch the Dashboard:**
    ```bash
    streamlit run app.py
    ```

## Dashboard Guide

### 1. Sidebar Inputs
* **Landlord:** Switches the strategic logic between WestProp and Terrace Africa.
* **Tenant Type:** Selects the category (e.g., Anchor, Diplomat) which applies specific discount/premium logic.
* **Target Rent:** Your goal price per square meter.
* **Vacancy & Credit:** Market conditions and tenant risk profile.

### 2. Main Dashboard
* **Predicted Closing Rent:** The AI's forecast of the final deal price.
* **Asset Value Impact:** The dollar value added or lost to the building's valuation.
* **Executive Recommendation:** A strategic summary advising on Rent-Free periods and CapEx contributions.
* **Negotiation Script:** AI-generated talking points for the leasing officer.

### 3. Stress Test Tools
* **WALE Meter:** Shows the impact of the lease term on portfolio stability.
* **Sensitivity Matrix:** A table at the bottom showing how the rent pricing holds up if vacancy increases to 20%.