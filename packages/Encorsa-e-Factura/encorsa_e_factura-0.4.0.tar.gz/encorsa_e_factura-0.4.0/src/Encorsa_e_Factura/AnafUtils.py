from requests.auth import HTTPBasicAuth
import requests
import traceback
import zipfile
from io import BytesIO
import time
import base64


def get_token_with_refresh(refresh_token, clientID, clientSecret, parameters):
    url = "https://logincert.anaf.ro/anaf-oauth2/v1/token"
    auth = HTTPBasicAuth(clientID, clientSecret)
    data = {
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    try:
        proxies = {
            'http': None,
            'https': None
        }

        if "proxi_pt_anaf_https" in parameters and parameters["proxi_pt_anaf_https"] != None and parameters["proxi_pt_anaf_https"] != "":
            proxies["https"] = parameters["proxi_pt_anaf_https"]

        if "proxi_pt_anaf_http" in parameters and parameters["proxi_pt_anaf_http"] != None and parameters["proxi_pt_anaf_http"] != "":
            proxies["http"] = parameters["proxi_pt_anaf_http"]

        response = requests.post(url, auth=auth, data=data, proxies=proxies)
        # This checks for HTTP errors and raises an exception if any
        response.raise_for_status()

        json_response = response.json()  # Attempt to parse JSON response

        if 'access_token' in json_response:
            return json_response['access_token']
        else:
            # Handle cases where 'access_token' is not in response
            error_message = "Error at getting ANAF aceess token. Access token not found in the response."
            print(error_message)
            raise Exception(error_message)
    except Exception as e:
        # Catch all other errors
        error_message = f"Error at getting ANAF access token. Error message: {str(e)}"
        detailed_error = traceback.format_exc()
        print(error_message)
        print(detailed_error)
        raise Exception(f"{error_message}\n{detailed_error}")
    

def get_lista_paginata_mesaje(token, start_time, end_time, cif, pagina, filter=None, parameters={}):
    url = f"https://api.anaf.ro/prod/FCTEL/rest/listaMesajePaginatieFactura?startTime={start_time}&endTime={end_time}&cif={cif}&pagina={pagina}"
    if filter is not None:
        if filter != "":
            url += "&filtru=" + filter

    headers = {'Authorization': f'Bearer {token}'}
    try:
        proxies = {
            'http': None,
            'https': None
        }

        if "proxi_pt_anaf_https" in parameters and parameters["proxi_pt_anaf_https"] != None and parameters["proxi_pt_anaf_https"] != "":
            proxies["https"] = parameters["proxi_pt_anaf_https"]

        if "proxi_pt_anaf_http" in parameters and parameters["proxi_pt_anaf_http"] != None and parameters["proxi_pt_anaf_http"] != "":
            proxies["http"] = parameters["proxi_pt_anaf_http"]

        response = requests.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()  # Ridică o excepție pentru coduri de răspuns HTTP eronate
        return response.json()
    except Exception as e:
        error_message = f"Error at getting messages for page {pagina}. Error message: {str(e)}"
        detalied_error = traceback.format_exc()
        print(error_message)
        print(detalied_error)
        return {'eroare': error_message + '\n' + detalied_error}

 
def get_all_messages(token, start_time, end_time, cif, filter=None, parameters={}):
    all_messages = []  # Lista pentru a stoca toate mesajele
    current_page = 1  # Indexul paginii curente începe de la 0

    # Încercăm să obținem mesajele de pe prima pagină pentru a verifica dacă există date
    first_page_response = get_lista_paginata_mesaje(
        token, start_time, end_time, cif, current_page, filter=filter, parameters=parameters)

    # Verificăm dacă răspunsul conține o eroare
    if "eroare" in first_page_response:
        if 'Nu exista mesaje' in first_page_response["eroare"]:
            print(first_page_response["eroare"])
            exit(0)
        error_message = "Error at getting all messages from ANAF: " + \
            first_page_response["eroare"]
        print(error_message)
        raise Exception(error_message)

    # Dacă există mesaje, continuăm să le adunăm din toate paginile
    total_pages = first_page_response['numar_total_pagini']
    all_messages.extend(first_page_response['mesaje'])

    # Continuăm cu următoarele pagini, dacă există
    for current_page in range(2, total_pages + 1):
        response = get_lista_paginata_mesaje(
            token, start_time, end_time, cif, current_page, filter=filter, parameters=parameters)
        if "eroare" in response:
            if 'Nu exista mesaje' in response["eroare"]:
                print(response["eroare"])
                exit(0)
            else:
                error_message = "Error at getting all messages from ANAF: " + \
                    response["eroare"]
                print(error_message)
                raise Exception(error_message)
        all_messages.extend(response['mesaje'])

    return all_messages


"""
Această funcție descarcă o arhivă ZIP de la ANAF folosind un ID de factură
și extrage un fișier specificat prin nume_fisier din aceasta. 
"""
def descarca_factura_si_extrage_fisier(token, id, nume_fisier, parameters):
    try:
        url = f"https://api.anaf.ro/prod/FCTEL/rest/descarcare?id={id}"
        headers = {'Authorization': f'Bearer {token}'}

        proxies = {
            'http': None,
            'https': None
        }

        if "proxi_pt_anaf_https" in parameters and parameters["proxi_pt_anaf_https"] != None and parameters["proxi_pt_anaf_https"] != "":
            proxies["https"] = parameters["proxi_pt_anaf_https"]

        if "proxi_pt_anaf_http" in parameters and parameters["proxi_pt_anaf_http"] != None and parameters["proxi_pt_anaf_http"] != "":
            proxies["http"] = parameters["proxi_pt_anaf_http"]

        response = requests.get(url, headers=headers, proxies=proxies)

        # Verify the response status code
        if response.status_code != 200:
            # Raise an exception for non-200 status codes with the HTTP status code
            error_message = f"Error while downloading ZIP archive with the XML. Code: {response.status_code}"
            print(error_message)
            raise Exception(error_message)

        # Create a BytesIO object from the response content
        zip_in_memory = BytesIO(response.content)

        try:
            # Open the ZIP archive
            with zipfile.ZipFile(zip_in_memory, 'r') as zip_ref:
                # Check if the file exists in the archive
                if nume_fisier in zip_ref.namelist():
                    # Extract the specified file content
                    with zip_ref.open(nume_fisier) as fisier:
                        content_bytes = fisier.read()
                        # Decode bytes into a string using UTF-8
                        content_string = content_bytes.decode('utf-8')
                        return content_string
                else:
                    # File not found in the archive, handle according to your preference
                    error_message = f"File '{nume_fisier}' not found in the ZIP archive"
                    print(error_message)
                    raise Exception(error_message)
        except zipfile.BadZipFile as zp_err:
            # Handle a bad ZIP file error
            error_message = f"Error while extracting ZIP archive with the XML. Message: {zp_err}"
            detalied_error = traceback.format_exc()
            print(error_message)
            print(detalied_error)
            raise Exception(error_message + '\n' + detalied_error)
    except Exception as e:
        # Handle other errors
        error_message = f"Error while downloading ZIP archive with the XML. Message: {e}"
        detalied_error = traceback.format_exc()
        print(error_message)
        print(detalied_error)
        raise Exception(error_message + '\n' + detalied_error)
    

def xml_to_pdf_to_base64(xml_data, parameters, document_type):
    """
    Funcția trimite date XML către un serviciu web al ANAF pentru a fi convertite
    într-un document PDF, apoi encodează conținutul binar al PDF-ului obținut în format Base64
    """

    if document_type == "Invoice":
        url = "https://webservicesp.anaf.ro/prod/FCTEL/rest/transformare/FACT1/DA"
    elif document_type == "CreditNote":
        url = "https://webservicesp.anaf.ro/prod/FCTEL/rest/transformare/FCN/DA"
    else:
        raise ValueError("Invalid document type for XML to PDF conversion." + f" Document type: {document_type}")
    
    headers = {'Content-Type': 'text/plain'}
    proxies = {'http': None, 'https': None}

    # Set proxies if provided in parameters
    if "proxi_pt_anaf_https" in parameters and parameters["proxi_pt_anaf_https"]:
        proxies["https"] = parameters["proxi_pt_anaf_https"]
    if "proxi_pt_anaf_http" in parameters and parameters["proxi_pt_anaf_http"]:
        proxies["http"] = parameters["proxi_pt_anaf_http"]

    # Retry logic
    max_retries = 5
    attempts = 0

    # Encode the XML data to UTF-8 bytes to ensure compatibility
    xml_data = xml_data.encode('utf-8')

    while attempts < max_retries:
        try:
            response = requests.post(
                url, headers=headers, data=xml_data, proxies=proxies)
            if response.status_code != 200:
                response.raise_for_status()

            # Directly check if the response is JSON
            if "application/json" in response.headers.get('Content-Type', ''):
                print("JSON response received, retrying..." + str(response.content))
                # Print the whole response for debugging
                attempts += 1
                # Sleep for 1 second before retrying
                time.sleep(1)
                continue
            else:
                # Assume the response is the binary content of the PDF
                pdf_content = response.content
                # Encode the PDF content to Base64
                base64_encoded_pdf = base64.b64encode(pdf_content)
                return base64_encoded_pdf.decode('utf-8')
        except Exception as e:
            error_message = f"Error when converting the XML to PDF: {str(e)}"
            detalied_error = traceback.format_exc()
            print(error_message + '\n' + detalied_error)
            attempts += 1

    print("Maximum retries reached, PDF content could not be retrieved.")
    raise Exception("Maximum retries reached, PDF content could not be retrieved.")
