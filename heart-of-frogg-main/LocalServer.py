import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pythonosc import udp_client
from threading import Thread

class RequestHandler(BaseHTTPRequestHandler):
    last_data_received = 0  # Zeitstempel des letzten Datenempfangs

    def _send_response(self, message):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(message, "utf8"))

    def do_POST(self):
        if self.path.startswith('/heart/'):
            rate = self.path.split('/')[-1]
            print(rate)
            # Erstelle eine Instanz des UDP-Clients
            client = udp_client.SimpleUDPClient("192.168.1.167", 8080)
            # Sende die Herzfrequenz an MaxMSP
            client.send_message("/heart", int(rate))
            
            # Setze den Zeitstempel des letzten Datenempfangs
            self.last_data_received = time.time()
            
            message = "Data received and sent successfully"
            self._send_response(message)
        else:
            message = "Invalid request"
            self._send_response(message)
    
    @classmethod
    def check_data_timeout(cls):
        # Überprüfe, ob seit dem letzten Datenempfang 3 Sekunden vergangen sind
        if time.time() - cls.last_data_received > 3:
            
            # Erstelle eine Instanz des UDP-Clients
            client = udp_client.SimpleUDPClient("192.168.1.167", 8080)
            # Sende den Wert 0 an MaxMSP
            client.send_message("/heart", 80)
            
            # Gib eine Meldung im Terminal aus
            print("Sent value 0 to MaxMSP")

def run():
    print('Starting server...')
    server_address = ('192.168.1.167', 8080)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Running server...')
    
    try:
        def check_timeout(request_handler):
            while True:
                time.sleep(1)  # Überprüfung alle 1 Sekunde
                request_handler.check_data_timeout()
        
        timeout_thread = Thread(target=check_timeout, args=(httpd.RequestHandlerClass,))
        timeout_thread.daemon = True
        timeout_thread.start()
        
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    
    httpd.server_close()
    print('Server stopped.')

run()
