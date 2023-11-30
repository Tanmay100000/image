import gradio as gr
import requests
from gradio_pdf import PDF
import pandas as pd

def extract_text_from_pdf(doc):
    # Check if the input is a string (file path)
    if isinstance(doc, str):
        file_path = doc
    elif isinstance(doc, PDF):
        file_path = doc.name

    # Read the file content as binary data
    file_content = open(file_path, 'rb').read()

    # Prepare file data for the API request
    files = [('file', ('file', file_content, 'application/octet-stream'))]

    # Send the POST request to the API
    url = "https://poc.lightinfosys.com/external_api/auto_extraction"
    headers = {}
    response = requests.request("POST", url, headers=headers, data={}, files=files)

    if response.status_code == 200:
        extracted_text = response.json()
        json_data = extracted_text['data']

        # Extract and format the JSON data
        vendor_name = json_data['string_data']['vendor_name']
        invoice_no = json_data['string_data']['invoice_no']
        customer_name = json_data['string_data']['customer_name']
        customer_address = json_data['string_data']['customer_address']
        invoice_date = json_data['string_data']['invoice_date']
        invoice_amount = json_data['string_data']['invoice_total_amount']

        string_data = json_data.get('string_data', {})
        formatted_data = ""

        # Iterate through the keys and values in string_data
        for key, value in string_data.items():
            formatted_data += f"<p style='margin: 0; color: #000;'><span style='display: inline-block; padding: 5px; margin-bottom: 5px; background-color: #007BFF; border-radius: 10px;'><strong style='color: #000;'>{key}:</strong></span> {value}</p>"

        table_data = extracted_text['data']['table_data']
        max_length = max(len(arr) for arr in table_data.values())
        table = {key: value + [""] * (max_length - len(value)) for key, value in table_data.items()}
        df = pd.DataFrame(table)
        styles = [
            dict(selector="table", props=[("border", "1px solid black")]),
            dict(selector="th, td", props=[("background-color", "#212529"), ("color", "white")]),
        ]
        df_html = df.style.set_table_styles(styles).render()

        # Format the data into a label-friendly string
        json_output_text = f"""
        Vendor Name: {vendor_name}
        Invoice No.: {invoice_no}
        Customer Name: {customer_name}
        Customer Address: {customer_address}
        Invoice Date: {invoice_date}
        Invoice Amount: {invoice_amount}
        """

        table_data = {
            "Vendor Name": vendor_name,
            "Invoice No.": invoice_no,
            "Customer Name": customer_name,
            "Customer Address": customer_address,
            "Invoice Date": invoice_date,
            "Invoice Amount": invoice_amount
        }

        html_output = f"""
        <div style="font-family: 'Courier New', monospace; margin: 20px; padding: 20px; border: 2px solid #ddd; border-radius: 10px; background-color: #fff; color: #000;">
            <!-- Header Section -->
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="background-color: #fff; padding: 10px; border-radius: 10px; display: inline-block;">
                    <img src="https://cdn-heiaj.nitrocdn.com/yoXwCrslgRpntnfOSDmSVmVdcrMRrNaM/assets/images/optimized/rev-d4788e9/e42.ai/wp-content/uploads/2021/09/E_42-logo.png" alt="Header Image" style="width: 200px; height: auto;">
                </div>
                <h2 style="color: #000;">ICR EXTRACTION</h2>
            </div>
            <h2 style="text-align: center; color: #000;">Extracted Information</h2>
            <div style='overflow-y: auto; max-height: 200px;'>{formatted_data}</div>
            <h2 style='text-align: center; color: #000;'>Table Data</h2>
            <div id='table-container' style='overflow-x: auto; overflow-y: auto; max-height: 300px;'>{df_html}</div>
            <form method="post" action="/submit">
                <button type="submit">Submit</button>
            </form>
            <script>
                // Make the table contenteditable using JavaScript
                var tableContainer = document.getElementById('table-container');
                tableContainer.contentEditable = true;
            </script>
        </div>
        """

        # Process the API response
        if response.status_code == 200:
            result = response.json()
            return html_output
        else:
            return f"Error: {response.status_code}\n{response.text}"

demo = gr.Interface(
    extract_text_from_pdf,
    [PDF(label="Document")],
    gr.HTML(),
    theme=gr.themes.Monochrome()
)

demo.launch(debug=True)
