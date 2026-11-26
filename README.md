Chicago Crime Analytics Dashboard
Steps to un the dashboard 



1. Create and activate a Python environment
On Windows PowerShell, run:

python -m venv .venv
.\.venv\Scripts\Activate.ps1


2. Install the required packages

python -m pip install --upgrade pip
pip install -r requirements.txt

3. Start the Streamlit dashboard
Make sure database\chicago_crime.db exists, then run:

streamlit run dashboard\app.py
Streamlit will open the dashboard in your web browser. If it does not
open automatically, copy the Local URL shown in the terminal
(usually http://localhost:8501) into your browser.