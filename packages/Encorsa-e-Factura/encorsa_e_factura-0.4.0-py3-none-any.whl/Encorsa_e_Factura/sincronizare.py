import base64
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import argparse
from datetime import datetime
import traceback

try:
    from .XMLUtils import *
except:
    from XMLUtils import *

try:
    from .WebConRequestUtils import *
except:
    from WebConRequestUtils import *
    
try:
    from .AnafUtils import *
except:
    from AnafUtils import *

namespaces = {
    'ubl': "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    'qdt': "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDataTypes-2",
    'cac': "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    'cbc': "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

nota_namespaces = {
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "ccts": "urn:un:unece:uncefact:documentation:2",
    "default": "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2",
    "qdt": "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDataTypes-2",
    "udt": "urn:oasis:names:specification:ubl:schema:xsd:UnqualifiedDataTypes-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


xpath_CUI = './cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID'
xpath_CUI2 = './cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID'
xpath_ID = './cbc:ID'


def send_to_WebCon(parameters, token, messages, xml_template_file_path, xml_nota_template_file_path=None):
    wtoken = get_webcon_token(
        parameters['webcon_base_url'], parameters['webcon_clientID'], parameters['webcon_clientSecret'])
    current_message = 1

    for message in messages:
        # print(f'Processing message {current_message} of {len(messages)}')
        try:
            id_solicitare = message["id_solicitare"]
            id = message["id"]
            tip_factura = message["tip"]
            iso_data_creare = datetime.strptime(
                message["data_creare"], "%Y%m%d%H%M")

            filtru_facturi = parameters.get(
                'ANAF_invoice_type_filter_E_T_P_R', '')

            if filtru_facturi != '':
                if tip_factura != filtru_facturi:
                    print(
                        f"Skipping invoice with ANAF_ID: {id}, because type filters are applied. The filter is: {filtru_facturi})")
                    continue
            else:
                if tip_factura != "FACTURA TRIMISA" and tip_factura != "FACTURA PRIMITA":
                    print(
                        f"Skipping invoice with ANAF_ID: {id}. The message type is not <FACTURA TRIMISA> or <FACTURA PRIMITA>")
                    continue

            xml_text = descarca_factura_si_extrage_fisier(
                token, str(id), f"{id_solicitare}.xml", parameters)

            # Se actualizeaza namespace-urile din XML
            # Este posibil ca XML-ul sa aiba namespace-uri diferite de cele standard
            # In trecut, au fost identificate cazuri in care namespace-urile erau declarate gresit
            xml_text = update_xml_namespaces(xml_text)

            # Se verifica daca factura preluata exista deja in WebCon pe baza cheii unice formate din ID-factura si CUI
            root = ET.fromstring(xml_text)
            # Se verifica tag-ului nodului root din XML si se elimina ce se afla intre acolade
            root_tag = root.tag
            if '}' in root_tag:
                root_tag = root_tag.split('}', 1)[1]

            local_namespaces = {}
            local_xml_template_file_path = ""
            document_type = ""

            if root_tag == 'Invoice':
                if xml_template_file_path is None or xml_template_file_path == "":
                    print('Skipping invoice with ANAF_ID: ' + id +
                          ' because there is no Invoice template file path provided.')
                    continue
                document_type = "Invoice"
                local_namespaces = namespaces
                local_xml_template_file_path = xml_template_file_path
            elif root_tag == 'CreditNote':
                if xml_nota_template_file_path is None or xml_nota_template_file_path == "":
                    print('Skipping invoice with ANAF_ID: ' + id +
                          ' because there is no Credit Note template file path provided.')
                    continue
                document_type = "CreditNote"
                local_namespaces = nota_namespaces
                local_xml_template_file_path = xml_nota_template_file_path
            else:
                print('Skipping invoice with ANAF_ID: ' + id +
                      ' because it is not an Invoice or Credit Note.')
                continue

            invoice_id_element = root.find(xpath_ID, local_namespaces)
            company_id_element = root.find(xpath_CUI, local_namespaces)
            company_id_element2 = root.find(xpath_CUI2, local_namespaces)
            company_id = ""
            

            if invoice_id_element is None:
                print(
                    f'Cannot get {document_type} ID from XML, skipping {document_type}. ID from ANAF: ' + id)
                continue
            else:
                invoice_id_element = invoice_id_element.text

            if company_id_element is None:
                if company_id_element2 is None:
                    print(
                        f'Cannot get {document_type} Supplier Company ID, skipping {document_type}. ID from ANAF: ' + id)
                else:
                    company_id = company_id_element2.text
            else:
                company_id = company_id_element.text

            ifInvoiceExists, wfd_id_duplicate = check_if_invoice_exists(
                parameters, wtoken, invoice_id_element, company_id)
            if (parameters['how_to_handle_duplicates'] == 'SKIP'):
                if ifInvoiceExists:
                    print(
                        f"Skipping {document_type} with ID: {invoice_id_element}, COMPANY ID: {company_id}, because it already exists in WebCon.")
                    continue

            pdf_content = xml_to_pdf_to_base64(xml_text, parameters, document_type)
            xml_bytes = str(xml_text).encode('utf-8')
            base64_encoded_xml = base64.b64encode(xml_bytes)
            base64_string_xml = base64_encoded_xml.decode('utf-8')

            body = create_webcon_body(parameters, base64_string_xml, pdf_content, xml_text, invoice_id_element, company_id,
                                      local_xml_template_file_path, wfd_id_duplicate, local_namespaces, document_type, id, iso_data_creare)
            response = create_invoice_instance(parameters, wtoken, body)
            print(
                f"{document_type} instance created with SUCCESS having WFD_ID: < {response['id']} >.")
        except Exception as ex:
            # Preparing and printing a detailed error message
            error_details = f"Error at processing message: {message}.\nError message: {str(ex)}"
            detalied_error = traceback.format_exc()
            print(error_details)
            print(detalied_error)
            raise Exception(error_details + '\n' + detalied_error)
        current_message += 1


def read_json_parameters(file_path):
    """Read and return the parameters stored in a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            file_content = file.read().strip()
            parameters = json.loads(file_content)
            return parameters
    except FileNotFoundError:
        error_message = f"Error: The file {file_path} was not found."
        detalied_error = traceback.format_exc()
        print(error_message + '\n' + detalied_error)
        raise Exception(error_message + '\n' + detalied_error)
    except json.JSONDecodeError:
        error_message = f"Error: The file {file_path} contains invalid JSON."
        detalied_error = traceback.format_exc()
        print(error_message + '\n' + detalied_error)
        raise Exception(error_message + '\n' + detalied_error)
    except Exception as ex:
        error_message = f"Error: The file {file_path} cannot opened/used. " + str(ex)
        detalied_error = traceback.format_exc()
        print(error_message + '\n' + detalied_error)
        raise Exception(error_message + '\n' + detalied_error)


def startRunning(json_file_path, xml_template_file_path, xml_nota_template_file_path=None):

    # Read parameters from the JSON file
    parameters = read_json_parameters(json_file_path)

    try:
        unix_timestamp_from = datetime.fromisoformat(
            parameters['get_invoices_from_timestamp'])
        unix_timestamp_to = datetime.fromisoformat(
            parameters['get_invoices_to_timestamp'])

        unix_timestamp_from = int(unix_timestamp_from.timestamp() * 1000)
        unix_timestamp_to = int(unix_timestamp_to.timestamp() * 1000)
        print(unix_timestamp_from)
        print(unix_timestamp_to)

        token_aux = get_token_with_refresh(
            parameters['refresh_token_anaf'], parameters['efactura_clientID'], parameters['efactura_clientSecret'], parameters)

        # get message filter
        messages = get_all_messages(token_aux, str(unix_timestamp_from), str(
            unix_timestamp_to), parameters['cod_fiscal_client'], parameters=parameters)
        send_to_WebCon(parameters, token_aux, messages,
                       xml_template_file_path, xml_nota_template_file_path)
    except Exception as ex:
        error_message = f"Error in main function: {str(ex)}"
        detalied_error = traceback.format_exc()
        print(error_message + '\n' + detalied_error)
        raise Exception(error_message + '\n' + detalied_error)


def startRunningCLI():
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Run the Encorsa_e_Factura synchronization process.")

    # Add arguments
    parser.add_argument('jsonFilePath', type=str,
                        help='The path to the JSON configuration file.')
    parser.add_argument('xmlFilePath', type=str,
                        help='The path to the XML template file to be processed for Invoices.')
    parser.add_argument('--notaXMLFilePath', type=str,
                        help='The path to the XML template file to be processed for Credit Notes.')

    # Parse arguments
    args = parser.parse_args()

    # Read parameters from the JSON file
    parameters = read_json_parameters(args.jsonFilePath)

    try:
        unix_timestamp_from = datetime.fromisoformat(
            parameters['get_invoices_from_timestamp'])
        unix_timestamp_to = datetime.fromisoformat(
            parameters['get_invoices_to_timestamp'])

        unix_timestamp_from = int(unix_timestamp_from.timestamp() * 1000)
        unix_timestamp_to = int(unix_timestamp_to.timestamp() * 1000)
        print(unix_timestamp_from)
        print(unix_timestamp_to)

        token_aux = get_token_with_refresh(
            parameters['refresh_token_anaf'], parameters['efactura_clientID'], parameters['efactura_clientSecret'], parameters=parameters)

        # get message filter
        messages = get_all_messages(token_aux, str(unix_timestamp_from), str(
            unix_timestamp_to), parameters['cod_fiscal_client'])
        send_to_WebCon(parameters, token_aux, messages,
                       args.xmlFilePath, args.notaXMLFilePath)
    except Exception as ex:
        error_message = f"Error in main function: {str(ex)}"
        detalied_error = traceback.format_exc()
        print(error_message + '\n' + detalied_error)
        raise Exception(error_message + '\n' + detalied_error)
