from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen
from html.parser import HTMLParser
import json

# URL to scrape
url = 'https://time.com/'

# HTML parser class
class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_item = False
        self.in_headline = False
        self.in_timestamp = False
        self.latest_stories = []

    def handle_starttag(self, tag, attrs):
        if tag == 'li' and ('class', 'latest-stories__item') in attrs:
            self.in_item = True
        elif self.in_item and tag == 'h3' and ('class', 'latest-stories__item-headline') in attrs:
            self.in_headline = True
        elif self.in_item and tag == 'time' and ('class', 'latest-stories__item-timestamp') in attrs:
            self.in_timestamp = True

    def handle_endtag(self, tag):
        if tag == 'li':
            self.in_item = False
        elif self.in_headline and tag == 'h3':
            self.in_headline = False
        elif self.in_timestamp and tag == 'time':
            self.in_timestamp = False

    def handle_data(self, data):
        if self.in_headline:
            title = data.strip()
            self.current_story = {'title': title}
        elif self.in_timestamp:
            timestamp = data.strip()
            self.current_story['timestamp'] = timestamp
            self.latest_stories.append(self.current_story)

# Function to fetch HTML content
def fetch_html(url):
    with urlopen(url) as response:
        return response.read().decode('utf-8')

# Custom request handler
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/latest_stories':
            html_content = fetch_html(url)
            parser = MyHTMLParser()
            parser.feed(html_content)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            response_data = json.dumps(parser.latest_stories).encode('utf-8')
            self.wfile.write(response_data)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

# Run the server
def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()