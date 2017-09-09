#!/usr/bin/env python
 
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Lock

nr = 3;

answers = []


lock = Lock()

# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    def add_answer(self, ip, nr, reply):
        global answers
        print(ip, nr, reply)
        lock.acquire()
        try:
            while len(answers) < nr:
                answers.append( {} )
            
            answers[nr-1][ip.replace('192.168.1.','')] = reply
        finally:
            lock.release()
        


    def page(self, content, refresh):
        message = "<!DOCTYPE html><html lang=\"en\"><head><title>QUIZ</title>"
        message += "<meta charset=\"utf-8\" /><meta http-equiv=\"Cache-Control\" content=\"no-cache\" />"
        message += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        if refresh:
            message += "<meta http-equiv=\"refresh\" content=\"1\">"
        message += "<style>\nh1 {\n   background-color: #D6D6EA;\n}\n</style>\n"
        message += "</head><body bgcolor=\"#E6E6FA\"><center>" + content 
        message += "</center></body></html>"
        return message

    def user_page(self, nr, ans):
        message = "<h1>Question " + str(nr) + "</h1>"
        
        for letter in sorted({'A', 'B', 'C'}):
            stijl = ""
            if '/'+letter in ans:
                stijl = " style=\"background-color:#F6F6FA;\""  
            message += "<p"+stijl+"><a href=\"/" + letter + "\"><font size=\"7\">" + letter + "</a></p>"

        if self.path in {'/A','/B','/C'}:
            message += "<p><a href=\"/\">Next></a></p>"

        return message

    def admin_page(self, ans):
        message = "<h1>Question " + str(nr) + "</h1>"
        
        message += "<p><a href=\"/admin/prev\">&lt;Prev</a> | <a href=\"/admin/next\">Next&gt;</a></p>"

        return message

    def stat_page(self, nr):
        global answers
        message = "<h1>Responses to question " + str(nr-1) + "</h1>" + "<p>"

        lock.acquire()
        try:
            if nr > 1:
                if len(answers) >= (nr-1):
                    message += "<p>" + str(answers[nr-2]) + "</p>"
        finally:
            lock.release()

        message += "</p>"

        return message

  
    # GET
    def do_GET(self):
        global nr
        global answers
        # Send response status code
        self.send_response(200)
        print(self.path)
 
        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()


        message = ''
        if '/admin' in self.path:
            if '/admin/next' in self.path:
                nr+=1
            elif '/admin/prev' in self.path:
                nr-=1
            message = self.page(self.admin_page(self.path),0)
        elif '/stat' in self.path:
            message = self.page(self.stat_page(nr),1)
        else:
            if self.path in {'/A','/B','/C'}:
                self.add_answer(self.client_address[0],nr,self.path.replace('/',''))
            message = self.page(self.user_page(nr, self.path),1)

        #print(self.client_address)
        # Write content as utf-8 data
        self.wfile.write(bytes((message), "utf8"))
        # nr+=1
        return
 
def run():
  print('starting server...')
 
  server_address = ('192.168.1.74', 80)
  httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
  print('running server...')
  httpd.serve_forever()
 
 
run()
