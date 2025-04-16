import gradio as gr
from budget_manager import BudgetManager
import os

# Ensure necessary folders exist
os.makedirs("data", exist_ok=True)
os.makedirs("plots", exist_ok=True)

bm = BudgetManager()

# Core functions
def record_expense(user_input, selected_category):
    response = bm.log_expense(user_input, selected_category)
    return response, bm.get_expenses_log(), bm.get_summary()

def reset_data():
    bm.reset()
    return "Data reset successfully!", bm.get_expenses_log(), bm.get_summary()

def set_budget(amount):
    try:
        bm.set_budget(float(amount))
        return f"Budget set to ${float(amount):.2f}", bm.get_expenses_log(), bm.get_summary()
    except ValueError:
        return "Invalid budget amount.", bm.get_expenses_log(), bm.get_summary()

def import_csv(file):
    if file is None:
        return "No file selected.", bm.get_expenses_log(), bm.get_summary()
    response = bm.import_csv(file.name)
    return response, bm.get_expenses_log(), bm.get_summary()

def show_clusters():
    return bm.cluster_expenses()

def show_plot():
    return bm.plot_expenses()

def show_cluster_plot():
    return bm.plot_clusters()

def export_excel():
    return bm.export_to_excel()

# Gradio UI
with gr.Blocks(theme=gr.themes.Default(primary_hue="pink")) as app:
    gr.Markdown("""
    # 💖 *Boujee on a Budget*
    ### Welcome to your AI-powered budget tracker!
    """)

    with gr.Row():
        expense_input = gr.Textbox(label="Enter an expense")
        category_dropdown = gr.Dropdown(
            label="Select Category",
            choices=bm.categories,
            value="Other"
        )
        submit_button = gr.Button("Add Expense")

    output_text = gr.Textbox(label="Status", interactive=False)

    with gr.Row():
        expense_log = gr.Textbox(label="Recorded Expenses", lines=10, interactive=False)
        summary_log = gr.Textbox(label="Spending Summary", lines=10, interactive=False)

    with gr.Row():
        budget_input = gr.Textbox(label="Set Monthly Budget ($)")
        set_budget_button = gr.Button("Set Budget")

    reset_button = gr.Button("Reset All Data")

    with gr.Row():
        file_input = gr.File(label="Upload CSV", file_types=[".csv"])
        import_button = gr.Button("Import CSV")
        cluster_button = gr.Button("Show Clusters")
        plot_button = gr.Button("Show Spending Plot")
        cluster_plot_button = gr.Button("Show Cluster Plot")
        export_excel_button = gr.Button("Export to Excel")

    cluster_output = gr.Textbox(label="Cluster Insights", interactive=False)
    plot_output = gr.Image(label="Spending Visualization")
    cluster_plot_output = gr.Image(label="Cluster Visualization")
    excel_file_output = gr.File(label="Download Excel Report")

    submit_button.click(record_expense, inputs=[expense_input, category_dropdown],
                        outputs=[output_text, expense_log, summary_log])
    reset_button.click(reset_data, outputs=[output_text, expense_log, summary_log])
    set_budget_button.click(set_budget, inputs=budget_input,
                            outputs=[output_text, expense_log, summary_log])
    import_button.click(import_csv, inputs=file_input,
                        outputs=[output_text, expense_log, summary_log])
    cluster_button.click(show_clusters, outputs=cluster_output)
    plot_button.click(show_plot, outputs=plot_output)
    cluster_plot_button.click(show_cluster_plot, outputs=cluster_plot_output)
    export_excel_button.click(export_excel, outputs=excel_file_output)

app.launch(share=True)

