import requests
import logging

logger = logging.getLogger("globalLogger")


def extract_data_from_form_recognizer(blob_link: str) -> dict:
    """
    Extract data from a file using Form Recognizer service.

    Parameters:
        blob_link (str): The URL link to the file stored in blob storage.

    Returns:
        dict: A dictionary containing the extracted data points obtained from the Form Recognizer service.
            The dictionary structure depends on the specific output format of the Form Recognizer service.
            In the example below, we assume the output is a nested dictionary where the keys represent different
            fields and the corresponding values are the extracted data.

    Example:
        blob_link = "https://your-blob-storage-url.com/example.pdf"

        result = extract_data_from_form_recognizer(blob_link)
        print(result)
        # Output:
        # {
        #     "field1": "value1",
        #     "field2": "value2",
        #     ...
        # }
    """
    json_response = {}
    try:
        response = requests.post(
            "https://prod-131.westus.logic.azure.com:443/workflows/157b7c0760d54da58bcd2530951c6aa6/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=1I5_2YDuF-gBTk_oAthRxZXcP1V6MBVDcHQKe1blp2Q",
            headers={
                "Content-Type": "application/json",
            },
            json={
                "file": blob_link,
            },
        )
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Get the response content as JSON (if applicable)
            json_response = response.json()
            print("Response JSON:", json_response)
        else:
            print("Request failed with status code:", response.status_code)

    except requests.exceptions.RequestException as e:
        print("Error making the request:", e)

    # json_response = {
    #     "total": "US $ 410.00",
    #     "date": "2009-11-09",
    #     "customerAddress": "P.O. BOX: 307448 Al Quoz Industrial Area 2 DUBAI- UAE",
    #     "customerName": "Precision Industries",
    #     "vendorName": "SATYANARAYAN RUBBER PRODUCTS",
    #     "billingAdress": None,
    #     "vendorAddress": "25, MANGAL ESTATE, NR. CHAKUDI MAHADEV, RAKHIAL, AHMEDABAD - 380023 INDIA",
    #     "paymentTerms": "SEA PORT - DUBAI",
    #     "subTotal": None,
    #     "totalTax": None,
    # }

    logger.info(f"Extracted data from form recognizer: {json_response}")

    return json_response
