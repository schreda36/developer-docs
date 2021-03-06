import queue
import threading
import time
import urllib3
import lxml.etree as etree
import lxml.objectify as objectify
from zeep.client import Client

def genius_request(url, queue=None):
    """
    Request handler for Genius communication
    :param url: Full URL String to send to the Genius Terminal.
    :param queue: optional queue variable for threaded response.
    :return: returns raw response if no thread queue provided.
    """
    genius_comm = urllib3.PoolManager()
    genius_response = genius_comm.request("GET", url).data
    if queue is not None:
        queue.put(genius_response)
    else:
        return genius_response

def genius_keyed_entry(ip_address):
    """
    Keyed Entry loop
    Sends a Status request to the terminal until it reaches screen 02 or 03. Then Initiates the Keyed Entry mode.
    :param ip_address: IP Address of the device
    """
    genius_on_sale_screen = False

    while genius_on_sale_screen is False:
        time.sleep(1)
        print("\nSending Status Request")
        status_response_data = genius_request("http://%s:8080/v2/pos?Action=Status&Format=XML" % ip_address)
        current_screen = objectify.fromstring(status_response_data, xml_parser).CurrentScreen

        if current_screen == 2 or current_screen == 3:
            print("Terminal is ready for KeyedEntry")
            genius_on_sale_screen = True
        else:
            print("Terminal is not Ready. Current Screen: %s. Waiting 1 second before trying again." % current_screen)

    keyed_entry_status_data = genius_request("http://%s:8080/v2/pos?Action=InitiateKeyedEntry&Format=XML" % ip_address)
    keyed_entry_status = objectify.fromstring(keyed_entry_status_data, xml_parser)
    print("InitiateKeyedEntry Result: %s\n" % keyed_entry_status.Status)

# Declare credentials to be used with the Stage Transaction Request
credentials_name = "TEST MERCHANT"
credentials_site_id = "XXXXXXXX"
credentials_key = "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
ip_address = "192.168.0.123"
# Generate XML and XSD Validation
genius_schema = etree.XMLSchema(file='Genius.xsd')
xml_parser = objectify.makeparser(schema=genius_schema)
# Generate WSDL and SOAP Objects Build Transport request details
transport_soap = Client(wsdl='https://transport.merchantware.net/v4/transportService.asmx?WSDL')
transport_request = transport_soap.get_type("ns0:TransportRequest")(
    TransactionType="SALE",
    Amount=1.01,
    ClerkId="1",
    OrderNumber="INV1234",
    Dba="TEST MERCHANT",
    SoftwareName="Test Software",
    SoftwareVersion="1.0",
    TerminalId = "01",
    PoNumber="PO1234",
    TaxAmount="0.10",
    EntryMode="Undefined",
    ForceDuplicate=True
)
# Stage Transaction
print("Staging Transaction\n");
transport_response = transport_soap.service.CreateTransaction(credentials_name, credentials_site_id, credentials_key, transport_request)
transport_key = transport_response.TransportKey
print("TransportKey Received: %s\n" % transport_key)
# Initiate transaction with TransportKey
print("Sending TransportKey %s to Terminal %s" % (transport_key, ip_address))
genius_request_url = "http://%s:8080/v2/pos?TransportKey=%s&Format=XML" % (ip_address, transport_key)
genius_response = queue.Queue()
genius_thread = threading.Thread(target=genius_request, args=(genius_request_url, genius_response))
genius_thread.start()
# Start Keyed Entry check
genius_keyed_entry(ip_address)
# Join initial thread ready for the response
print("Waiting for transaction to Complete...\n")
genius_thread.join()
# Validate the response with the Genius XSD
genius_response_data = objectify.fromstring(genius_response.get(), xml_parser)
print("Transaction Result: %s" % genius_response_data.Status)
print("Amount: %s" % genius_response_data.AmountApproved)
print("AuthCode: %s" % genius_response_data.AuthorizationCode)
print("Token: %s" % genius_response_data.Token)
print("Account Number: %s" % genius_response_data.AccountNumber)

input("Press Enter to close")
