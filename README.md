## Boujee on a Budget 3.0
Boujee on a Budget 3.0 provides a user-friendly AI application that allows users to set a monthly budget based on their income, track their expenses, and report insightful summaries of the users spending habits. 


## Getting Started 

** Clone the Repository ** 
'''bash
git clone https://github.com/your-username/boujee-on-a-budget-3.0.git
cd boujee-on-a-budget

** Install Dependencies ** 
pip install -r requirements.txt

** Run the App ** 
python app.py

** Note **
I included a empty data/ folder with an example .csv file to test. User will need to create an empty plots/ folder

Structure of Code

|-- app.py                  # Main UI built with Gradio
|-- budget_manager.py       # Core logic and data handling
|-- data/                   # Saved transactions (JSON)
|-- plots/                  # Generated charts and Excel reports
|-- requirements.txt
|__ README.md

This project uses Gradio (https://www.gradio.app/guides/quickstart) to build a web application for a machine learning model. 



