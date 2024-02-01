import datetime
import io
import os
import time
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget
import base64
import json
import pandas as pd
import subprocess


def get_dataframe_from_bin(file_data):
    '''
    temp_file_path = '/opt/uploaded_file.csv'

    with open(temp_file_path, 'wb') as csv_file:
        csv_file.write(file_data)

    return temp_file_path
    '''

    csv_data = io.StringIO(file_data.decode('utf-8'))
    df = pd.read_csv(csv_data, sep=',')
    return df


def generate_unique_pdf_filename(license_id, package_id, start_date, end_date, utc_offset):
    filename = f"{license_id}_{package_id}_{start_date}_{end_date}_{utc_offset}.pdf".replace("/", "_")
    return filename


def save_to_path(data, file_path):
    try:
        with open(file_path, 'wb') as file:
            file.write(data)
    except Exception as e:
        print(f"Error saving data to {file_path}: {str(e)}")


def lambda_handler(event, context):
    try:
        # print(event)

        start_time = time.time()
        print(f"lambda_handler start: {datetime.datetime.now()}")

        parser = StreamingFormDataParser(headers=event['headers'])

        # Read input parameters
        csv_data = ValueTarget()
        license_id = ValueTarget()
        package_id = ValueTarget()
        start_date = ValueTarget()
        end_date = ValueTarget()
        utf_offset = ValueTarget()

        parser.register("csv_data", csv_data)
        parser.register("license_id", license_id)
        parser.register("package_id", package_id)
        parser.register("start_date", start_date)
        parser.register("end_date", end_date)
        parser.register("utf_offset", utf_offset)

        data_received = base64.b64decode(event["body"])

        parser.data_received(data_received)

        license_id_str = license_id.value.decode("utf-8")
        package_id_str = package_id.value.decode("utf-8")
        start_date_str = start_date.value.decode("utf-8")
        end_date_str = end_date.value.decode("utf-8")
        utf_offset_str = utf_offset.value.decode("utf-8")

        print(f"Text parameters read: {license_id_str}, {package_id_str}, {start_date_str},"
              f" {end_date_str}, {utf_offset_str}")

        # Get csv dataframe
        save_to_path(csv_data.value, '/tmp/data.csv')
        # csv_df = get_dataframe_from_bin(csv_data.value)

        print(f"Dataframe created: {datetime.datetime.now()}")

        pdf_filename = generate_unique_pdf_filename(license_id_str, package_id_str,
                                                    start_date_str, end_date_str, utf_offset_str)

        run_report('/tmp/data.csv', license_id_str, package_id_str, start_date_str, end_date_str, utf_offset_str)

        with open('/tmp/pdf_output_path.pdf', 'rb') as pdf_result:
            pdf_data = pdf_result.read()
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        end_time = time.time()
        elapsed_time_ms = (end_time - start_time) * 1000

        print(f'Total execution time in ms: {elapsed_time_ms}')

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/pdf",
                "Content-Disposition": f"attachment; filename={pdf_filename}"
            },
            "body": pdf_base64,
            "isBase64Encoded": True,
            "elapsed_time_ms": elapsed_time_ms
        }

    except Exception as e:

        response_code = 500
        response_error = f"REQUEST ERROR: {str(e)}"

        return {
            "statusCode": response_code,
            "body": json.dumps({
                "error_message": response_error
            })
        }


def run_report(csv_path, license_id, package_id, start_date, end_date, utc_offset):
    BASE_PATH = os.getcwd()

    # Command to run the Dash app
    dash_command = ["python3", f"{BASE_PATH}/FingerDashApp.py",
                    csv_path, license_id, package_id, start_date, end_date, utc_offset]

    # Command to run the PDF export script (assuming 'your_pdf_export_script.py' is the name of your PDF export script)
    # On a computer with graphical browsers
    pdf_export_command = ["python3", f"{BASE_PATH}/ExportDashToPDF.py", '/tmp/pdf_output_path.pdf']

    # On a ubuntu Server
    # pdf_export_command = [
    #    "xvfb-run", "-a", "--server-args=-screen 0 1920x1080x24", "python3",
    #    f"{BASE_PATH}/ExportDashToPDF.py", 'pdf_output_path.pdf'
    # ]

    # Start running the Dash app in a separate process
    print(f"command: {dash_command}")
    dash_process = subprocess.Popen(dash_command)

    # mp.set_start_method('fork')

    # print(f"Dash server command prepared: {datetime.datetime.now()}")

    # finger_dash_app_process.start()

    # print(f"Dash server started: {datetime.datetime.now()}")

    # Allow some time for the Dash app to start
    time.sleep(4)  # Adjust the delay as needed

    # Run the PDF export script after the Dash app has started
    print(f"Start PDF export: {datetime.datetime.now()}")
    subprocess.run(pdf_export_command)
    # export = ExportDashToPDF('http://172.0.0.1:8050/')
    # export = ExportDashToPDF('https://google.es')
    # pdf_result = asyncio.get_event_loop().run_until_complete(export.generate_pdf())
    print(f"Finished PDF export: {datetime.datetime.now()}")

    # finger_dash_app_process.terminate()
    # return pdf_result

    # Optional: Terminate the Dash app process after exporting the PDF (if needed)


if __name__ == '__main__':
    print(f"Main start: {datetime.datetime.now()}")
    start_time = time.time()
    df = pd.read_csv('MasNomina_FINGER_1499_2023-11-01_2023-11-20.csv', sep=',')
    pdf_binary = run_report(df, '1499', 'masnomina.finger.com', '01/11/23', '31/11/23', -7)

    with open('test.pdf', 'wb') as pdf_file:
        pdf_file.write(pdf_binary)
    print(f"Saved PDF Report: {datetime.datetime.now()}")

    end_time = time.time()
    elapsed_time_ms = (end_time - start_time) * 1000

    print(f'Total execution time in ms: {elapsed_time_ms}')
