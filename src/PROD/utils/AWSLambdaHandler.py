import base64
import io
import json
import zipfile

from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget

ERROR_INVALID_REQUEST = 400
ERROR_RETURNING_PDF = 501
ERROR_OK = 200


class CustomError(Exception):
    def __init__(self, code, description):
        self.code = code
        self.description = description
        super().__init__(f"Error {code}: {description}")


def validate_date_format(date_str):
    # Split the string into parts using "/"
    date_parts = date_str.split("/")

    # Check that there are three parts and that they are all digits
    if len(date_parts) != 3 or not all(part.isdigit() for part in date_parts):
        raise CustomError(ERROR_INVALID_REQUEST, f"Date format {date_str} is not valid. It should be dd/mm/yy")

    # Check that the numbers are in the appropriate range
    day, month, year = map(int, date_parts)
    if not (1 <= day <= 31) or not (1 <= month <= 12) or not (0 <= year <= 99):
        raise CustomError(ERROR_INVALID_REQUEST, f"Date format {date_str} is not valid. It should be dd/mm/yy")


def validate_positive_number(num_str):
    try:
        num = int(num_str)
        if num <= 0:
            raise CustomError(ERROR_INVALID_REQUEST, f"The license id number must be positive: {num_str}")
    except ValueError:
        raise CustomError(ERROR_INVALID_REQUEST, f"The license id number must be positive: {num_str}")


def validate_modality(modality):
    supported_modalities = ['FACE', 'FINGER', 'OCR']
    try:
        tbd = 0

    except ValueError:
        raise CustomError(ERROR_INVALID_REQUEST,
                          f"The modality value should be one of these enums: {supported_modalities}")


def validate_platform(platform):
    supported_platforms = ['IOS', 'ANDROID', 'WEB']
    try:
        tbd = 0

    except ValueError:
        raise CustomError(ERROR_INVALID_REQUEST,
                          f"The platform value should be one of these enums: {supported_platforms}")


def validate_http_request(license_id_str, start_date_str, end_date_str, platform_str):
    validate_date_format(start_date_str)
    validate_date_format(end_date_str)
    validate_positive_number(license_id_str)
    validate_platform(platform_str)


def return_error(error_code, error_message):
    response_error = f"REQUEST ERROR: {str(error_message)}"

    return {
        "statusCode": error_code,
        "body": json.dumps({
            "error_message": response_error
        })
    }


def return_pdf_report(abs_pdf_path, pdf_filename, elapsed_time_ms):
    try:
        print(f"Reading pdf from {abs_pdf_path} ... ")
        with open(abs_pdf_path, 'rb') as pdf_result:
            pdf_data = pdf_result.read()
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        return {
            "statusCode": ERROR_OK,
            "headers": {
                "Content-Type": "application/pdf",
                "Content-Disposition": f"attachment; filename={pdf_filename}"
            },
            "body": pdf_base64,
            "isBase64Encoded": True,
            "elapsed_time_ms": elapsed_time_ms
        }

    except Exception as e:
        return_error(ERROR_RETURNING_PDF, str(e))


def save_to_path(data, file_path):
    try:
        with open(file_path, 'wb') as file:
            file.write(data)
    except Exception as e:
        print(f"Error saving data to {file_path}: {str(e)}")


def process_http_request(event, abs_path):
    parser = StreamingFormDataParser(headers=event['headers'])

    # Read input parameters
    zip_data = ValueTarget()
    license_id = ValueTarget()
    package_id = ValueTarget()
    start_date = ValueTarget()
    end_date = ValueTarget()
    client = ValueTarget()
    platform = ValueTarget()

    parser.register("zip_data", zip_data)
    parser.register("license_id", license_id)
    parser.register("package_id", package_id)
    parser.register("start_date", start_date)
    parser.register("end_date", end_date)
    parser.register("client", client)
    parser.register("platform", platform)

    data_received = base64.b64decode(event["body"])

    parser.data_received(data_received)

    license_id_str = license_id.value.decode("utf-8")
    package_id_str = package_id.value.decode("utf-8")
    start_date_str = start_date.value.decode("utf-8")
    end_date_str = end_date.value.decode("utf-8")
    client_str = client.value.decode("utf-8")
    platform_str = platform.value.decode("utf-8")

    print(f"Text parameters read: {license_id_str}, {package_id_str}, {start_date_str}, {end_date_str}"
          f", {client_str}, {platform_str}")

    validate_http_request(license_id_str, start_date_str, end_date_str, platform_str)

    # Extract the ZIP file
    try:
        zip_buffer = io.BytesIO(zip_data.value)
        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            first_file_name = zip_file.namelist()[0]
            extracted_data = zip_file.read(first_file_name)

        with open(abs_path, "wb") as output_file:
            output_file.write(extracted_data)

    except zipfile.BadZipFile as e:
        print(f"Not a zip file: {str(e)}")
        raise CustomError(ERROR_INVALID_REQUEST, "Not a zip file")

    return license_id_str, package_id_str, start_date_str, end_date_str, client_str, platform_str
