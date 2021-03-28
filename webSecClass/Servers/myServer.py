# Author: 		Andrew Afonso
# Filename: 	myServer.py
# Tab Width:	4
###########
# Description: 	A HTTP server 
#
# Assn. Brief:	This version (3) of myClient/myServer runs a HTTP/S server using 
#				the arguments specified at the command line at runtime.
# 				
#
# Requirements:
#			-Accept four command line arguments:
#			-[x]		1. The IP address to listen on
#			-[x]		2. The port to listen on
#			-[x]		3. A path to an x509 (.pem or .crt file) to use for HTTPS encryption
#   		-[x]		4. A path to the private key paired with the x509 certificate.
#			-[x]	Support GET, POST, PUT, DELETE, HEAD
#			-[x]	Support the following HTTP response codes: 200, 201, 400, 403, 404, 411, 500, 501, 505
#			-[x]	Log first line of all valid requests to a log file. 
#			-[x] If HTTPS request used and no PEM specified, gracefully handle the case (500)
#			-[x]	Do not execute if x509 path supplied (arg 3) but not private key (arg4)
#			-[x]	No HTTP request parsing libraries. 
#			-[x]	Support HTTP/1.0 and HTTP/1.1
#			-[x]	Code must be documented (this)
#			-[x]	Code must execute on Ubuntu 18.04
#
##########

# Load Libraries
import ssl
import socket
import re
import sys
import os
import codecs
import logging
import threading
import mimetypes
import datetime

# Global Vars
### This is used to hold the closer for symbols that may enclose URL's
url_enders = ['}', ')', ']', '>', '"', "'", "<", " ", ";"] 
### This is a list of URL endings that the program will perform secondary parsing to locate. Some TLD endings will create a high number of false positives, so these have been chosen as default. Add any you like. 
tld_list = [ ".biz", ".co.", ".com", ".edu", ".gov", ".info", ".mil", ".net", ".onion", ".org" ] 
### Used to enclose characters to detect per RFC 2616 Sec. 2.2
quoted_chars = [ "(", ")", "<", ">", "@", ",", ";", ":", '\\', '"', "/", "[", "]", "?", "=", "{", "}", "\t" ]
### List of request methods supported by the request parser. 
parser_supported_request_methods = ["GET", "POST", "PUT", "DELETE", "CONNECT", "HEAD"]
### List of request methods supported by HTTP 1.0
http_one_methods = ["GET", "HEAD", "POST"]
### List of fields not permitted in a Trailer header field. 
bad_trailer_fields = ["Transfer-Encoding", "Content-Length", "Host", "Cache-Control", "Max-Forwards", "TE", "Authorization", "Set-Cookie", "Content-Encoding", "Content-Type", "Content-Range"]

# Socket Object Class
class socketObj:
	# A method that initializes and returns a python socket for the target URL. 
	def make_socket(self):
		base_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#print("DEBUG: " + str(self.port) + "\n")
		# Wrap in SSL socket if needed
		if self.port == 443:
			try:
				socky = socket.create_connection((self.target.split("https://")[0], 443))
				context = ssl.create_default_context()
				context.options &= ~ssl.OP_NO_SSLv3
				socket_object = context.wrap_socket(socky, server_hostname = self.target.split("https://")[0])
				socket_object.settimeout(5)
			except socket.error as socket_error:
				status_msg(500, "[ FATAL ERROR - SSL Socket Connect Error: " + str(socket_error) + " ]")
		elif self.port == 80:
			socket_object = base_socket
			try:
				socket_object.connect((self.target, self.port))
				socket_object.settimeout(5)
			except socket.error as socket_error:
				status_msg(500, "[ FATAL ERROR - Socket Connect Error: " + str(socket_error) + " ]")
		return socket_object
		
	# Method to send a request using the socket. Returns replied data. 
	def send_message(self, request): 
		#print("DEBUG: " + request)
		try:
			reply_output = ""
			self.socket_object.send(request.encode())
			while 1==1:
				response = self.socket_object.recv(4096)
				#print("DEBUG: " + str(response))
				if not response:
					break
				reply_output += str(response)
			#self.close_socket()
		except socket.error as socket_error:
			status_msg(500, "[ FATAL ERROR - Socket Send Error: " + str(socket_error) + " ]")
		return reply_output

	
	# Method to initialize a socketObj object
	def __init__(self, target_URL, port):
		self.target = target_URL
		self.port = port
		self.socket_object = self.make_socket()

	# Method to close socket	
	def close_socket(self):
		self.socket_object.close()
		
	# Method to directly access socket within the socket object
	def get_socket(self):
		return self.socket_object
####
# End of Socket Class
####

# Website class
class website:
	# Initialize website
	def __init__(self, url):
		self.url = url
		self.path = get_url_path(self.url)
		self.host = get_url_host(self.url)
		self.port = get_port(self.url)
		self.http_prefix = get_http_prefix(self.port)
		self.url_end = url_ending(self.url)
		self.urls = []
		self.decoded = ""
		self.raw = ""
		
		
	# Method to return site object URL
	def get_site_url(self):
		return self.url
	
	# Method to return site object port	
	def get_site_port(self):
		return self.port
		
	# Method to fetch the host from the site object.
	def get_site_host(self):
		return self.host
		
	# Method to return the decoded site text from the site object
	def get_site_decoded(self):
		return self.decoded
		
	# Method to fetch the URL list from a site object
	def get_site_urls(self):
		return self.urls
		
	# Method to get and return the contents of webpage
	def get_page(self, url_text):
		site_socket = socketObj(self.host, self.port)
		request = make_request(url_text, self.host)
		webpage = site_socket.send_message(request)
		site_socket.close_socket()
		if "200 OK" in webpage:
			return webpage
		else:
			return "error"
		
	# Method to decode a raw website to a viewable, parsable (html) document.
	def organic_decode(self):
		if self.raw == "":
			print("No raw website data present. Fetch it first.")
		else:
			webpage = codecs.decode(self.raw, 'unicode_escape')
			webpage = webpage.replace("\\t", "\t").replace("\\r\\n", "\r\n").replace("\\n", "\n").replace("\'b\'", "").replace("\\/", "/").replace('\\"', '\"')
			self.decoded = webpage
	
	
	# Method to pretty print website		
	def pprint_site(self):
		if self.decoded == "":
			print("No website decoded")
		else:
			print(self.decoded)
			
	# Method to fetch the raw data from the site.
	def get_raw(self):
		self.raw = self.get_page(self.path)
		
	# Method to save the website data to a HTML file
	def save_html(self):
		if self.decoded == "":
			self.organic_decode()
			self.save_html()
		else:
			html_file = open("webpage.html", "w")
			html_file.write(self.decoded)

	# Method to assist in URL parsing
	def temp_element_resolver(self, temp_element):
		if temp_element not in self.urls and "." in temp_element and temp_element != self.url_end:	
			self.urls.append(temp_element)
			
	
	# Method that takes a string, and a URL suffix, then determines the beginning of the URL and returns the string cleaned up 
	def clean_url_front(self, url_messy, suffix):
		tracker = 0
		for a in range(len(url_messy[ : url_messy.rfind(suffix)]) - len(suffix), -1, -1):
			if tracker == 0 and not url_messy[a].isalpha() :
				if url_messy[a] != "." and url_messy[a] != "/" and url_messy[a] != "-" and not url_messy[a].isdigit():
					url_messy = url_messy[ a+1 : ]
					tracker = 1
		if url_messy[0] == ".": # Removes preceeding . if applicable. 
			url_messy = url_messy[1:]
		if url_messy[:2] == "//": # Removes preceeding // if applicable. 
			url_messy = url_messy[2:]
		if url_messy[0] == "/" and url_messy[1].isalpha():
			url_messy = self.http_prefix + self.host + url_messy
		return url_messy
		
	
	# Method to parse string for a URL
	def parse_url(self, input_string):
		# Description:	First, parse known locations for URL's within HTML code, in href and src blocks
		#
		# Explanation:	Both single and double quotes can be used as delimiters in the same way, 
		#				so code blocks are repeated and changed to parse both formats. First, href
		#				elements are parsed, then src elements are parsed. After that, the remaining text is
		#				scanned for occurances of "http", and any remaining URL's should be detected and parsed. 
		#print(input_string)
		if "href=" in input_string:
			if '"http' in input_string:
				temp_element = input_string[input_string.find('"') + 1:]
				temp_element = temp_element[:temp_element.find('"')]
				self.temp_element_resolver(temp_element)
			if "'http" in input_string:
				temp_element = input_string[input_string.find("'") + 1:]
				temp_element = temp_element[:temp_element.find("'")]
				self.temp_element_resolver(temp_element)
			elif 'href="/' in input_string:
				temp_element = self.http_prefix + self.host + input_string[input_string.find('"') + 1:]
				temp_element = temp_element[:temp_element.find('"')]
				self.temp_element_resolver(temp_element)
			elif "href='/" in input_string:
				temp_element = self.http_prefix + self.host + input_string[input_string.find("'") + 1:]
				temp_element = temp_element[:temp_element.find("'")]
				self.temp_element_resolver(temp_element)
		if "src=" in input_string:
			if 'src="/' in input_string and 'src="//' not in input_string:
				temp_element = self.http_prefix + self.host + input_string[input_string.find('"') + 1:]
				temp_element = temp_element[:temp_element.find('"')]
				self.temp_element_resolver(temp_element)
			elif 'src="//' in input_string:	
				temp_element = input_string[input_string.find('//') + 2:]
				temp_element = temp_element[:temp_element.find('"')]
				self.temp_element_resolver(temp_element)
			elif '"http' in input_string:
				temp_element = input_string[input_string.find('"') + 1:]
				temp_element = temp_element[:temp_element.find('"')]
				self.temp_element_resolver(temp_element)
			elif "src='/" in input_string and "src='//" not in input_string:
				temp_element = self.http_prefix + self.host + input_string[input_string.find("'/") + 1:]
				temp_element = temp_element[:temp_element.find("'")]
				self.temp_element_resolver(temp_element)
			elif "src='//" in input_string:	
				temp_element = input_string[input_string.find('//') + 2:]
				temp_element = temp_element[:temp_element.find("'")]
				self.temp_element_resolver(temp_element)
			elif "'http" in input_string:
				temp_element = input_string[input_string.find("'") + 1:]
				temp_element = temp_element[:temp_element.find("'")]
				self.temp_element_resolver(temp_element)
		
		# Last, fall back to barebones text parsing. 
		
		# First, parse for http
		if "http" in input_string and "." in input_string and "src=" not in input_string and "href=" not in input_string:
			temp_element = input_string[input_string.find('http') :]
			if '\n' in input_string:
				temp_element = temp_element[:temp_element.find('\n')]
			
			for x in range(len(temp_element)):
				if temp_element[x] in url_enders:
					temp_element = temp_element[:x]
					break
					
			self.temp_element_resolver(temp_element)
		
		# Next, parse for www.
		if "www." in input_string and "http" not in input_string and "src=" not in input_string and "href=" not in input_string:
			temp_element = input_string[input_string.find('www.'):]
			for x in range(len(temp_element)):
				if temp_element[x] in url_enders:
					temp_element = temp_element[:x]
					break
			if temp_element[len(temp_element) - 1 ] == ".":
				temp_element = temp_element[:len(temp_element) - 1 ]
			
			self.temp_element_resolver(temp_element)
		
		# Next, parse for //, which escapes a rel URL to a top level URL
		if "'//" in input_string or '"//' in input_string and "http" not in input_string and "src=" not in input_string and "href=" not in input_string and len(input_string) > 3:
			if input_string[  input_string.find("//") + 2 ].isalpha():
				if "'//" in input_string:
					temp_element = input_string[  input_string.find("//") + 2 : ]
					temp_element = temp_element[:temp_element.find("'")]
					self.temp_element_resolver(temp_element)
				if '"//' in input_string:
					temp_element = input_string[  input_string.find("//") + 2 : ]
					temp_element = temp_element[:temp_element.find('"')]
					self.temp_element_resolver(temp_element)
		
		# Last, parse for known URL endings. 
		if "www." not in input_string and "http" not in input_string and "src=" not in input_string and "href=" not in input_string and "'//" not in input_string and '"//' not in input_string: 
			for z in range(len(tld_list)):
				if tld_list[z] in input_string:
					
					split_view = re.split('\)|\n', input_string) # Split things up in such a way that ensures one URL per line. 
					
					for y in range(len(split_view)):
						if tld_list[z] in split_view[y]:				
							if split_view[y].count(tld_list[z]) > 1:
								print("\nError-----\nDouble Item BAD: " + split_view[y] + "\n")
							
							elif len(split_view[y]) > ( split_view[y].rfind(tld_list[z]) + len(tld_list[z]) ):
								char_after_suffix = split_view[y][split_view[y].rfind(tld_list[z]) + len(tld_list[z])]
								if char_after_suffix.isalpha() == False :
									if char_after_suffix == "/" or char_after_suffix == ":":
										# These are URL's that have a path or port after the base url
										temp_element = self.clean_url_front(split_view[y], tld_list[z])
										for x in range(len(temp_element)):
											if temp_element[x] in url_enders:
												temp_element = temp_element[:x]
												break
										self.temp_element_resolver(temp_element)
											
									
									else:
										# These are URL's that are simply a base domain, i.e. their suffix is their end. 
										temp_element = split_view[y][ : split_view[y].rfind(tld_list[z]) + len(tld_list[z])]
										temp_element = self.clean_url_front(temp_element, tld_list[z])
										# This final check filters out entries that were just the URL suffix
										if tld_list[z] in temp_element: 
											self.temp_element_resolver(temp_element)
									
							else:
								# These are strings that contain a URL suffix, but that occurs at the very end of the string. 
								temp_element = self.clean_url_front(split_view[y], tld_list[z])
								self.temp_element_resolver(temp_element)

	
	# Method to return a list of URLs from a sites body using text parsing
	def get_url_list(self):
		if self.decoded == "":
			print("No website decoded")
		else:
			temp_decoded = self.decoded.replace("%3A", ":").replace("%3a", ":").replace("%2F", "/").replace("%2f", "/").replace("%3F", "?").replace("%3f", "?").replace("%3D", "=").replace("%3d", "=").replace("&amp;", "&" ).replace("%26", "&").replace("%2C", ",").replace("%2c", ",").replace( "%20",  " ").replace("%25", "%")#.replace("\n", "")
			website_split = temp_decoded.split(" ")
			for x in range( len(website_split) ):
				if "," not in website_split[x]:
					if "=http" not in website_split[x]:
						self.parse_url(website_split[x])
					else:
						double_split = website_split[x].split("http")
						for item in double_split:	
							if ":/" in item[:3]:
								self.parse_url(item)
				else:
					double_split = website_split[x].split(",")
					for item in double_split:
						self.parse_url(item)
				
####
# End of Website Class
####			
			
			
# HTTP Server Class			
class httpServer:	
	# Method to initialize a HTTP Server object
	def __init__(self, listen_ip, listen_port, certificate_path="", key_path=""):
		if not validate_ipv4(listen_ip): status_msg(500, "[ Invalid listening IP supplied ]")
		if not listen_port.isdigit():  status_msg(500, "[ Invalid listening port supplied ]")
		if certificate_path!="" and not os.path.exists(certificate_path): status_msg(500, "[ Invalid x509 certificate file specified ]")
		if key_path!="" and not os.path.exists(key_path): status_msg(500, "[ Invalid x509 key file specified ]")
		self.listen_ip = listen_ip
		self.listen_port = int(listen_port)
		self.certificate_path = certificate_path
		self.key_path = key_path
		self.debug = False # Used to control Debug logging (detailed errors logged to logfile.)
		logging.basicConfig(filename='http_server.log', level=logging.DEBUG)
		self.supported_request_methods = ["GET", "POST", "PUT", "DELETE", "HEAD"]
		self.supported_http_one_request_methods = ["GET", "HEAD", "POST"]
		self.supported_major_versions = [ 1 ]
		self.supported_minor_versions = [ 0, 1 ]

	
	# A method for returning the text for HTTP status messages (RFC 2616 Sec. 10)
	def get_status_msg_text(self, statNo):
		# Success (200-299)
		if statNo == 200:
			return("OK")
		if statNo == 201:
			return("Created")
		if statNo == 204:
			return("No Content")
	
		# Cilent errors (400-449)
		if statNo == 400:
			return("Bad Request")
		if statNo == 403:
			return("Forbidden")
		if statNo == 404:
			return("Not Found")
		if statNo == 411:
			return("Length Required")
		if statNo == 414:
			return("Request-URI Too Long")
	
	
		# Server errors (500-599)
		if statNo == 500:
			return("Internal Server Error" )
		if statNo == 501:
			return("Not Implemented" )
		if statNo == 505:
			return("HTTP Version Not Supported" )
	
	# Starts the server
	def start_server(self):
		socky = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		socky.bind((self.listen_ip, self.listen_port))
		socky.listen(5) # number of connections allowed at once. 
		while True:
			(connection_socket, connection_address) = socky.accept()
			if self.debug: print('Connected by', repr(connection_address))
			client_thread = threading.Thread(target=server_connection_thread, args=(connection_socket, self,))	
			client_thread.start()

	# A method to enable debug logging
	def server_debug(self, log_message):
		if self.debug and log_message != "":
			logging.debug( log_message )
			
	# A method to enable info logging
	def server_log(self, log_message):
		if log_message != "":
			logging.info( log_message )

	
####
# End of HTTP Server Class
####	



# Server connection thread class
class server_connection_thread:
	# Method to initialize a new connection thread
	def __init__(self, connection_socket, serverObject):
		self.conn_socket = connection_socket
		self.serverObj = serverObject
		self.major_version = 1
		self.minor_version = 1
		self.is_basic = False
		self.request_method = ""
		self.target_uri = ""
		self.message_body = b''
		self.client_thread_handler()

	# Method to handle the connection. 
	def client_thread_handler(self):
		request_text = b''
		if self.serverObj.certificate_path != "" and self.serverObj.key_path != "":
			server_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
			server_context.options &= ~ssl.OP_NO_SSLv3
			#server_context.verify_mode=ssl.CERT_NONE
			server_context.load_cert_chain(certfile=self.serverObj.certificate_path, keyfile=self.serverObj.key_path, password=None)
			connected_socket = server_context.wrap_socket( self.conn_socket, server_side=True)	
		else:
			connected_socket = self.conn_socket

		connected_socket.settimeout(0.2)
		
		while True: # Read in data from client 1 KB at a time. 
			try:
				data = connected_socket.recv(1024)
				if not data: 
					break
				request_text = request_text + data
				if len(data) < 1024: # If amount of data received is smaller than the buffer, we are done receiving data. 
					break
				
			except socket.timeout:
				break
			except socket.error as socket_error:
				self.serverObj.server_debug("500 - [ FATAL ERROR - SSL Socket Connect Error: " + str(socket_error) + " ]")
				self.error_and_close_socket(500, connected_socket)
				return
		
		request_text = request_text.decode("utf-8")
		
		if request_text != '': # If we got a non-blank request, deal with it. 
			status_code = self.validate_http_request(request_text)

			#print("REQUEST: " + str(status_code))

			if status_code != 200: # If we errored out
				self.error_and_close_socket( status_code, connected_socket)
				return

			# At this point, the HTTP request has been validated in terms of actual content. Time to start processing.  
			if self.request_method == "GET":
				status_code = self.validate_get_path()
				if status_code != 200: # If we errored out
					self.error_and_close_socket( status_code, connected_socket)
					return
				else:
					mimetypes.init()
					(content_type, content_encoding) = mimetypes.guess_type(self.target_uri, strict=True)
					target_file = open(self.target_uri, "rb")
					
					file_contents = target_file.read()
					content_length = str( len(file_contents) )
			
					get_reply_headers = {}
					get_reply_headers["Content-Type"] = content_type
					get_reply_headers["Content-Length"] = content_length
			
					http_response = self.make_response(200, file_contents, get_reply_headers)
		
			if self.request_method == "POST":
				# At this point, no additional processing is occurring for POSTs, just send back a 204
				http_response = self.make_response( 204 )
				
			if self.request_method == "PUT":
				status_code = self.validate_put()
				self.error_and_close_socket( status_code, connected_socket)
				return
			
			if self.request_method == "DELETE":
				status_code = self.validate_delete()
				self.error_and_close_socket( status_code, connected_socket)
				return
		
				
			if self.request_method == "HEAD":
				status_code = self.validate_get_path()
				if status_code != 200:
					connected_socket.send(self.make_response(status_code))
					connected_socket.close()
					return	
				else:
					mimetypes.init()
					(content_type, content_encoding) = mimetypes.guess_type(self.target_uri, strict=True)
					target_file = open(self.target_uri, "rb")
					file_contents = target_file.read()

					content_length = str( len(file_contents) )
			
					head_reply_headers = {}
					head_reply_headers["Content-Type"] = content_type
					head_reply_headers["Content-Length"] = content_length
			
					http_response = self.make_response(status_code=200, message_headers=head_reply_headers)
					
			connected_socket.send( http_response )
			connected_socket.close()
			return


	# Description:	Evaluates and attempts to perform a loaded DELETE request
	# Returns:		A HTTP status code. (int)
	def validate_delete(self):
		if os.path.exists(self.target_uri):
			try:
				os.remove(self.target_uri)
				return 200
			except:
				return 500		
		return 400
	
	
	# Description:	Evaluates and attempts to perform a PUT request. 
	# Returns:		A HTTP status code. (int)
	def validate_put(self):
		if not os.path.exists(self.target_uri):
			try:
				with open(self.target_uri, 'wb') as put_file:
					put_file.write(bytes( self.message_body, "ISO-8859-1") )
					return 201
			except:
				self.serverObj.server_debug("500 - PUT new file error - [ " + str(repr(sys.exc_info())) + " ]")
				return 500		
		else:
			try:
				with open(self.target_uri, 'wb') as put_file:
					put_file.write(bytes( self.message_body, "ISO-8859-1") )
					return 200
			except:
				self.serverObj.server_debug("500 - PUT new file error - [ " + str(repr(sys.exc_info())) + " ]")
				return 500	
		return 400
		


	# Description:	Validates that the target-uri path is an appropriate file. 
	# Returns:		A HTTP status code. 
	def validate_get_path(self):
		try:
			open(self.target_uri, "r")
		except IOError as io_error:
			error_number = io_error.errno
			if error_number == 2:
				return 404
			if error_number == 13:
				return 403
			else:
				self.serverObj.server_debug("IOError - [ " + str(repr(sys.exc_info())) + " ]")
				return 404
		except:
			self.serverObj.server_debug("GET Validation Catch All - [ " + str(repr(sys.exc_info())) + " ]")
			return 404
			#print(repr(sys.exc_info()))
		return 200


	# Description:	Constructs and returns a HTTP response message based on supplied status code. 
	# Returns:		A bytes object containing a HTTP response message. 
	def make_response(self, status_code, message_body="", message_headers={}):
		http_response = 'HTTP/' + str(self.major_version) + '.' + str(self.minor_version) + ' ' 
		http_response += str(status_code) + ' ' + self.serverObj.get_status_msg_text(status_code) + '\r\n'
		
		if len(message_headers) > 0:
			for header_name, header_value in message_headers.items():
				http_response += str(header_name) + ': ' + str(header_value) + '\r\n'
		
		the_date = datetime.datetime.now(datetime.timezone.utc)
		http_response += "Date: " + the_date.strftime("%a, %d %b %Y %X") + ' GMT\r\n'
		http_response += 'Server: Andrews PythonCLI Server\r\n'
		http_response += 'Connection: close\r\n'
		http_response += '\r\n'
		
		
		http_response = bytes( http_response, "utf-8")
		
		if message_body != "":
			http_response += message_body

		return http_response


	# Description:	Sends off an error message for and closes a socket. 
	def error_and_close_socket(self, status_code, connected_socket):
		connected_socket.send(self.make_error_response(status_code))
		connected_socket.close()
		return	
		

	# Description:	Constructs and returns a HTTP error response message based on supplied status code. 
	# Returns:		A bytes object containing a HTTP error response message. 
	def make_error_response(self, status_code):
		http_response = 'HTTP/' + str(self.major_version) + '.' + str(self.minor_version) + ' ' 
		http_response += str(status_code) + ' ' + self.serverObj.get_status_msg_text(status_code) + '\r\n'
		
		response_body = '<html>' + str(status_code) + ' ' + self.serverObj.get_status_msg_text(status_code) + '</html>\r\n'
		
		the_date = datetime.datetime.now(datetime.timezone.utc)
		http_response += "Date: " + the_date.strftime("%a, %d %b %Y %X") + ' GMT\r\n'
		if status_code != 204:
			http_response += 'Content-Length: ' + str(len(response_body.encode("utf-8") )) + '\r\n'
			http_response += 'Content-Type: text/html\r\n'
		http_response += 'Connection: close\r\n'
		http_response += '\r\n'
		
		if status_code != 204:
			http_response += response_body
		
		http_response = bytes( http_response, "utf-8")
		
		return http_response


	# Description:	Accepts a single line of text that contains a HTTP requests' request line. This should already be stripped of CRLF. 
	# Returns:		An HTTP status code.  
	def validate_request_line(self, request_line):
		line_split = request_line.split(" ")
		
		# Parse text blocks to check if this is a barebones HTTP/1.0 request. 
		calc_items  = 0
		for item in line_split:
			if item != '':
				calc_items += 1

		if calc_items == 2: # Only valid for HTTP 1.0 and below requests. Assumed to be HTTP 0.9. Headers not accepted. 
			if line_split[0] not in self.serverObj.supported_http_one_request_methods: # Check 1st element
				self.serverObj.server_debug("501 - [ Unsupported HTTP 1.0 request method ]")
				return 501
			else: # If a barebones HTTP 1.0 or below message, set message type to basic, set connection version as 1.0. Headers not accepted.
				self.is_basic = True
				self.major_version = 1 
				self.minor_version = 0
				return 200

		if line_split[0] not in self.serverObj.supported_request_methods: # Check 1st element
			self.serverObj.server_debug("501 - [ Unsupported request method ]")
			return 501
		else:
			request_method = line_split[0]
			
		if request_method != "CONNECT": # Check 2nd element (non-connects)
			if line_split[1][0] != "/":
				if line_split[1][0] != "*":
					if line_split[1][:4] != "http" or line_split[1] == "http"  or "://" not in line_split[1]: # MUST NOT process if uri= "http"
						self.serverObj.server_debug("400 - [ Invalid URI ]")
						return 400
						
		
		if request_method == "CONNECT": # Check 2nd element (connects)
			if "." not in line_split[1] or ":" not in line_split[1]: # Ensure the authority form of the request-target is in use
				self.serverObj.server_debug("400 - [ Invalid CONNECT URI ]")
				return 400

		if "HTTP/" not in line_split[2] or "." not in line_split[2]:
			self.serverObj.server_debug("400 - [ Invalid HTTP version format ]")
			return 400

		return 200
		
	# Description:	Method to validate the format of a HTTP header line. Expects CRLF to have been removed. 
	#				Returns an HTTP status code. 
	def validate_http_header_format(self, header_line):
		cut_line = header_line[:header_line.find(" ")]
		if ":" not in cut_line:
			self.serverObj.server_debug("400 - [ Improperly formatted header detected ]")
			return 400

		field_name = header_line[:header_line.find(":")]
		field_value = header_line[header_line.find(":"):]
		in_quotes = False

		for character in field_name:
			if not character.isalpha() and character != "-" and character != '"' and not in_quotes:
				self.serverObj.server_debug("400 - [ Invalid unquoted character used in header name ]")
				return 400
			if character == '"':
				in_quotes = not in_quotes
				
		return 200


	# Description:	Method to validate an incoming HTTP request.  
	# 				Returns a HTTP status code indicating validity of request. 
	def validate_http_request(self, http_request):
		if http_request == "":
			self.serverObj.server_debug("400 - [ Blank request provided ]")
			return 400
		elif "\r\n\r\n" not in http_request:
			self.serverObj.server_debug("400 - [ Request not ended with double CRLF ]")
			return 400
		elif "\r\n\r\n\r\n" in http_request:
			self.serverObj.server_debug("400 - [ Header ended with double CRLF ]")
			return 400
		elif http_request[:2] == "\r\n":
			self.serverObj.server_debug("400 - [ Improper line spacing beginning request ]")
			return 400
		else:
			try:
				split_http_request = http_request.split("\r\n")
				
				#print(repr(http_request))
				#print(repr(split_http_request))

				counter = 0
				end_header_line = 0
				crlf_lines = 0
				provided_content_length = 0
				calculated_content_length = 0
				
				host_value = ""
				has_body = False
			
				# These are booleans used to track if specific headers have been detected for RFC conditionals  
				has_connection_header = False
				has_upgrade_header = False
				has_host_header = False
				has_transfer_encoding_header = False
				has_content_length_header = False
			
				# Validate first line of header. 
				request_check_code = self.validate_request_line(split_http_request[0])
				if request_check_code != 200:
					return request_check_code
				
				# Now we parse first line of header a bit. 	
				line_one_split = split_http_request[0].split(" ")
				self.request_method = line_one_split[0]
			
				if line_one_split[1] == "/":
					self.target_uri = "index.html"
				else:
					if len(line_one_split[1]) > 1:
						if line_one_split[1][0] == "/":
							self.target_uri = line_one_split[1][1:]
					
				
				# Limit Request-URI to len of 255
				if len(self.target_uri) > 255: 
					return 414

				# Skip all this processing if we know this is a barebones HTTP/1.0 request. 
				if not self.is_basic:
				
					# Parse HTTP version per RFC
					major_version = line_one_split[2].split("/")[1].split(".")[0]
					minor_version = line_one_split[2].split("/")[1].split(".")[1]
					while major_version[0] == "0" and len(major_version) > 1:
						major_version = major_version[1:]	
					while minor_version[0] == "0" and len(minor_version) > 1:
						minor_version = minor_version[1:]	
					if not minor_version.isdigit() or not major_version.isdigit():
						self.serverObj.server_debug("400 - [ Invalid HTTP version ]")
						return 400
					minor_version = int(minor_version)
					major_version = int(major_version)
					if minor_version not in self.serverObj.supported_minor_versions:
						self.serverObj.server_debug("505 - [ Unsupported HTTP minor version ]")
						return 505
					if major_version not in self.serverObj.supported_major_versions:
						self.serverObj.server_debug("505 - [ Unsupported HTTP major version ]")
						return 505
					self.minor_version = minor_version
					self.major_version = major_version
					# Done parsing version

					# Validate headers. 
					for x in range(1, split_http_request.index('')):
						line = split_http_request[x]
					
						# Validate header format before parsing.
						header_validation_code = self.validate_http_header_format(line)
						if header_validation_code != 200:
							return header_validation_code

						# Parse header
						field_name = line[:line.find(":")]
						field_value = line[line.find(":"):]
					
						## Evaluate conditions
					
						if "Connection:" in line:
							has_connection_header = True
					
						if "Content-Length" in line: # Detects if body data is expected. 
							if has_transfer_encoding_header == 1:
								self.serverObj.server_debug("400 - [ Content-Length and Transfer-Encoding can't be sent together ]")
								return 400
							elif has_content_length_header:
								self.serverObj.server_debug("400 - [ Duplicate Content-Length fields detected ] ")
								return 400
							else:
								has_content_length_header = True
								has_body = True
								if not field_value.strip("\r\n").strip(": ").isdigit():
									self.serverObj.server_debug("400 - [ Invalid content length value specified (non-int) ] ")
									return 400
								else: 
									provided_content_length = int(field_value.strip("\r\n").strip(": "))
		
						if "Content-Range" in line:
							if self.request_method == "PUT":
								self.serverObj.server_debug("400 - [ Unsupported header found in PUT request ]")
								return 400
		
						#if "Date:" in line or "Expires:" in line:
						#	if "GMT" not in line:
						#		self.serverObj.server_debug("400 - [ Invalid time format specified ]")
						#		return 400	
							
						if "Host:" in line:
							if has_host_header == True:
								self.serverObj.server_debug("400 - [ Multiple Host headers specified ]")
								return 400
							if has_host_header == False:
								has_host_header = True
								if field_value == "": #or "." not in field_value:
									self.serverObj.server_debug("400 - [ Invalid host specified ]")
									return 400
								host_value = field_value
							
		
						if "Trailer:" in line:
							if any(element in line for element in bad_trailer_fields) or line.find("Trailer") > 1:
								self.serverObj.server_debug("400 - [ Invalid trailer specified ]")
								return 400

						if "Transfer-Encoding" in line:
							if has_content_length_header:
								self.serverObj.server_debug("400 - [ Content-Length and Transfer-Encoding can't be sent together ]")
								return 400
							else:
								has_transfer_encoding_header = True
								if major_version != 1 or minor_version != 1:
									self.serverObj.server_debug("400 - [ Transfer-Encoding header only supported in HTTP/1.1 ]")
									return 400
			
						if "Upgrade:" in line:
							has_upgrade_header = True
				
				# Check if there is a body. If so, calculate its length.
				body_start_ind = http_request.find('\r\n\r\n') 
				self.message_body = http_request[body_start_ind+4:]
				
				if self.message_body != '':
					has_body = True
					if not has_content_length_header:
						self.serverObj.server_debug("400 - [ Messages with a body require a Content-Length header ]")
						return 400
					else:
						calculated_content_length = len(self.message_body.encode("utf-8"))
				
							
				# Final checks, then return 200 if no issues found. 
				if has_upgrade_header and not has_connection_header: # If upgrade header used, ensure connection header used as well
					self.serverObj.server_debug("400 - [ Upgrade header requires use of Connection header ]") 
					return 400
					
				if self.request_method == "POST" and not has_content_length_header:
					self.serverObj.server_debug("411 - [ Content length not provided for POST message ]")
					return 411
		
				if self.major_version == 1 and self.minor_version == 1:
					if has_host_header == 0:
						self.serverObj.server_debug("400 - [ Host header must be provided in HTTP/1.1 messages ]")
						return 400
						
					if ":" in self.target_uri:
						if ":" not in host_value:
							self.serverObj.server_debug("400 - [ Both Host and URI must be authority if URI has authority ]")
							return 400
						if host_value not in target_uri:
							self.serverObj.server_debug("400 - [ Authoritative target URI requires authoritative Host field as well ]")
							return 400

				if has_content_length_header or has_body:
					if calculated_content_length != provided_content_length:
						self.serverObj.server_debug("400 - [ Invalid Content Length Provided | P=" + str(provided_content_length) + "  C=" + str(calculated_content_length) + " ]")
						return 400
		
				self.serverObj.server_log(str(split_http_request[0]))
				return 200
				
			except: # A catch all 500 error message
				self.serverObj.server_debug("500 - [ " + str(repr(sys.exc_info())) + " ]")
				return 500


####
# End of server connection thread class. 
####


# Description:	Method to get external references from a list of URL's based on a input URL
def get_ext_ref(target_url, url_list):
	count = 0
	no_www_url = target_url.replace("www.", "")
	host_url = get_url_host(target_url)
	for item in url_list:
		if target_url not in item and no_www_url not in item and host_url not in item:
			print(item)
			count = count + 1
	print("Total external references: " + str(count))

# Description:	Returns "http" or "https" based on supplied port number (80/443)
def get_http_prefix(port):
	if port == 80:
		return "http://"
	if port == 443:
		return "https://"
		
		
# Description:	Validates an IPv4 address. Returns True or False
def validate_ipv4(potential_ip):
	octets = potential_ip.split(".")
	if len(octets) != 4:
		return False
	for octet in octets:
		if not octet.isdigit():
			return False
		octet_int = int(octet)
		if octet_int < 0 or octet_int > 255:
			return False
	return True



# Description:	Constructs HTTP request text
def make_request(target, host):
	request = "GET "
	request += target
	request += " HTTP/1.1\r\n"
	request += "Accept-Encoding: identity\r\n"
	request += "Host: " + host + "\r\n"
	#request += "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15\r\n"
	request += "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0\r\n"
	request += "Connection: close\r\n"
	request += "\r\n"
	#print("DEBUG\n" + request)
	return request
	
	
# Description:	Removes the protocol indicators from a URL and returns it. 
def url_ending(full_url):
	if full_url.find("https://") != -1:
		new_url = full_url[12:]
	else:
		new_url = full_url[11:]
	return new_url


# Description:	Returns the path for a url (part after .com)
def get_url_path(full_url):
	chopped_url = url_ending(full_url)
	if "/" in chopped_url:
		for x in range(len(chopped_url)):
			if chopped_url[x] == "/":
				return chopped_url[x:]
	else:
		return "/" 


# Description:	Returns the host portion of a url
def get_url_host(full_url):
	chopped_url = url_ending(full_url)
	if "/" in chopped_url:
		for x in range(len(chopped_url)):
			if chopped_url[x] == "/":
				return "www." + chopped_url[:x]
	else:
		return "www." + chopped_url


# Description:	Checks if URL provided contains HTTPS. If so, return 443, else, return 80
def get_port(url):
	if url.find("https://") != -1:
		return 443
	else:
		return 80
		
		
# Description:	Downloads and saves a list of english (and unique) TLD endings from Mozilla
def download_tld_list():
	if not os.path.exists("tld.db"):
		tld_site = website("https://www.publicsuffix.org/list/public_suffix_list.dat")
		tld_site.get_raw()
		tld_site.organic_decode()
		if "200 OK" in tld_site.get_site_decoded():
			tld_decoded = tld_site.get_site_decoded().split("\n")
			tld_db_list = []
			for line in tld_decoded:
				if not line[:2] == "//": # Ignore comments
					if "." not in line and line != "" and line.isalpha():
						line = "." + line
						if line not in tld_db_list:
							tld_db_list.append(line)
					if "." in line and line != "":
						split_tld = line.split(".")
						tld_ending = "." + split_tld[len(split_tld) - 1 ]
						if tld_ending not in tld_db_list and tld_ending.isalpha():
							tld_db_list.append(tld_ending)
			with open("tld.db", "w") as tld_db_file:
				for item in tld_db_list:
					tld_db_file.write(item + "\n")
	else:
		print("Error: Seems there is already a tld.db file. Rename, move, or delete the existing file to download a new db")
		
		


# Description:	A module for printing off HTTP status messages on the CLI. 
def status_msg(statNo, msg=""):
	debug = 0
	if debug == 1 and msg != "":
		print("DEBUG: " + str(statNo) + " : " + msg)
	# Success (200-299)
	if statNo == 200:
		print("200 OK")
	# Cilent errors (400-449)
	if statNo == 400:
		print("400 Bad Request")
		return 1 # returns 1 for error detection in request file parser
	# Server errors (500-599) [Should exit]
	if statNo == 500:
		sys.exit("500 Internal Server Error" )
		

# Description:	Because crlf seems impossible in text editors...
def write_good_request():
	request = make_request("https://www.rit.edu", "rit.edu")
	with open("good_request.txt", "wb") as good_req_file:
		for line in request:
			good_req_file.write(line)

# The main method
def main():
	# Get the path to file containing HTTP request from user input
	if len(sys.argv) == 4: status_msg(500, "[ x509 cert specified without specifying private key file ]")
	
	if len(sys.argv) == 3:
		myServer = httpServer(sys.argv[1], sys.argv[2])
	elif len(sys.argv) == 5:
		myServer = httpServer(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
	else: 
		status_msg(500, "[ Invalid number of arguments provided to program ]")
	
	myServer.start_server()
		

# Calls main
if __name__ == "__main__":
	main()	
