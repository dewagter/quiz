#!/usr/bin/env python
 
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Lock

nr = 1;

answers = []


lock = Lock()

# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    def export_csv(self):
        print('[CSV] store')
        file = open("quiz.csv","w")
        
        lock.acquire()
        try:
            cnt = 0
            for mydict in answers:
                cnt = cnt+1
                file.write( str(cnt) + "," )
                for ans in sorted(mydict):
                    file.write( str(ans[0]) + "," + str(ans[1]) + "," + str(mydict[ans]) + ",")
                file.write(  "\n" )
        finally:
            lock.release()

        file.close() 


    def add_answer(self, user, ip, nr, reply):
        global answers
        print("[ADD]",user, ip, nr, reply)
        lock.acquire()
        try:
            while len(answers) < nr:
                answers.append( {} )
            
            answers[nr-1][(user.replace('name=',''),ip)] = reply
            #answers[nr-1][ip.replace('192.168.1.','')] = reply
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

    def user_page(self, nr, ans, user):
        print("[USR] page",nr,ans,user)
        message = "<h1>Question " + str(nr) + "</h1>"
        
        for letter in sorted({'A', 'B', 'C'}):
            stijl = ""
            if '/'+letter in ans:
                stijl = " style=\"background-color:#F6F6FA;\""  
            message += "<p"+stijl+"><a href=\"/" + letter + "?"+user+"\"><font size=\"7\">" + letter + "</a></p>"

        if ans in {'/A','/B','/C'}:
            message += "<p><a href=\"/?"+user+"\">Next></a></p>"

        #message += "<p>"+user+" "+ans+"</p>"

        return message

    def setup_page(self,ip):
        print("[SET]",ip)
        message = "<h1>What is your name?</h1>"
        message += "<form action=\"/\"><p>Name: <input type=\"text\" name=\"name\"/></p><p><input type=\"submit\"></p></form>"
        return message

    def admin_page(self, ans):
        print("[ADM]",ans)
        message = "<h1>Question " + str(nr) + "</h1>"
        
        message += "<p><a href=\"/admin/prev\">&lt;Prev</a> | <a href=\"/admin\">Refresh</a> | <a href=\"/admin/next\">Next&gt;</a></p>"

        return message

    def stat_page(self, nr):
        global answers
        print("[STA]",nr)
        message = "<h1>Responses " + str(nr-1) + "</h1>" + "<p>"

        lock.acquire()
        try:
            if nr > 1:
                if len(answers) >= (nr-1):
                    mydict = answers[nr-2]
                    for ans in mydict:
                        message += "<li><b>" + str(ans[0]) + "</b>: " + str(mydict[ans]) + "</p>"
        finally:
            lock.release()

        message += "</p>"

        return message

  
    # GET
    def do_GET(self):
        global nr
        global answers


        message = ''
        if '/admin' in self.path:
            if '/admin/next' in self.path:
                nr+=1
                self.export_csv()
            elif '/admin/prev' in self.path:
                nr-=1
            message = self.page(self.admin_page(self.path),0)
        elif '/favicon.ico' in self.path:
            print("[ICO] not exist")
            self.send_response(404)
            self.send_header('Content-type','image/x-icon')
            self.end_headers()
            # Write content as utf-8 data
            #self.wfile.write(bytes((""), "utf8"))
            return
        elif '/stat' in self.path:
            message = self.page(self.stat_page(nr),1)
        else:
            url = self.path
            user = ""
            if '?' in url:
                li = url.split('?')
                url = li[0]
                user = li[1]
                #print("USER:", user)
                if url in {'/A','/B','/C'}:
                    self.add_answer(user, self.client_address[0],nr,url.replace('/',''))
                
                message = self.page(self.user_page(nr, url, user),1)
            else:
                message = self.page(self.setup_page(self.client_address[0]),0)

        # Send response status code
        self.send_response(200)
        #print(self.path)
 
        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Write content as utf-8 data
        self.wfile.write(bytes((message), "utf8"))
        # nr+=1
        print("[GET] Ready",self.path,self.client_address)
        return
 
def run():
  print('starting server...')
 
  server_address = ('192.168.1.74', 80)
  httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
  print('running server...')
  httpd.serve_forever()
 
 
run()
