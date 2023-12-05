import pytest
from approaches.fileupload import run
from werkzeug.datastructures import FileStorage

file_path = "tests/test_files/InvoiceAEStyle.png"

answer = "'total': 'US $ 410.00', 'date': '2009-11-09', 'customerAddress': 'P.O. BOX: 307448 Al Quoz Industrial Area 2 DUBAI- UAE', 'customerName': 'Precision Industries', 'vendorName': 'SATYANARAYAN RUBBER PRODUCTS', 'billingAdress': None, 'vendorAddress': '25, MANGAL ESTATE, NR. CHAKUDI MAHADEV, RAKHIAL, AHMEDABAD - 380023 INDIA', 'paymentTerms': 'SEA PORT - DUBAI', 'subTotal': None, 'totalTax': None}, 'thoughts': 'Searched for:<br>file<br>Found:<br>{'total': 'US $ 410.00', 'date': '2009-11-09', 'customerAddress': 'P.O. BOX: 307448 Al Quoz Industrial Area 2 DUBAI- UAE', 'customerName': 'Precision Industries', 'vendorName': 'SATYANARAYAN RUBBER PRODUCTS', 'billingAdress': None, 'vendorAddress': '25, MANGAL ESTATE, NR. CHAKUDI MAHADEV, RAKHIAL, AHMEDABAD - 380023 INDIA', 'paymentTerms': 'SEA PORT - DUBAI', 'subTotal': None, 'totalTax': None}<br>'ne, 'totalTax': None}<br>"


# def test_fileupload():
#     with open(file_path, "rb") as file:
#         file_storage = FileStorage(file)
#     assert run(file_storage).get("answer") == answer
