###Imports
import requests
import os
import sys
import time
import html

class mvids():
    
    def __init__(self):

        ##URLs for indexing Movies and TV##
        self.indexMovieURL = 'https://mobilevids.org/webapi/videos/movies.php'
        self.indexTvURL = 'https://mobilevids.org/webapi/videos/tvshows.php'
        self.loginURL = 'https://mobilevids.org/webapi/videos/tvshows.php'
        self.username = 'mickrich345@gmail.com'
        self.code = "7897412563"
        
        ##Set minimum execution times for different requests ##
        self.wait = {'indexpage':1,'pagepull':0}

        ##Set active directery to location of script ##
        self._setCWD()
        
        ##Set var self.user_id and self.token ##
        self._login() 
        
        

        ## Return length of pages
        self.pagenum = {'m':self.pagesamount('m'),'t':self.pagesamount('t')}
        self.movieindex, self.tvindex = self.totalindex('m'),self.totalindex('t')
        if "Return" in self.pagenum['m'] or "Return" in self.pagenum['t'] or "Return" in [self.movieindex,self.tvindex]:
            self.relogin = True
    
    def _login(self):
        count = 0
        while True:
            try:
                data = {'data': '{"Name":"'+self.username+'","Password":"'+self.code+'"}'}
                response = requests.post(self.loginURL, data=data).json()
                self.user_id = response['id']
                self.token = response['auth_token']
                time.sleep(1)
                break
            except:
                print('Failed to login. Try#'+str(count))
                time.sleep(5)
                count += 1
                continue
    
    def _setCWD(self):
        os.chdir(os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0])
    def pagesamount(self,mot):
        while True:
        st = time.time()
        if mot == 'm':
            response = requests.get(self.movieurl, params=self.params)
        elif mot == 't':
            response = requests.get(self.tvurl, params=self.params)
        else:
            print(mot,"\nMust be 'm'ovie OR 't'v show.")
            sys.exit()
        end = time.time()
        if end - st < self.wait['indexpage']:
            time.sleep(self.wait['indexpage']-(end - st))
        try:
            y = response.json()
        except:
            print(response.text,"\nCould not JSON.")
            sys.exit()
        if 'session missmatch' in y['reason']:
            return "Relogin"
        return y

        
        
        
        x = self.reqjson(mot)
        
        if x == "Relogin":
            return x
        if 'total_pages' in x:
            return x['total_pages']
        else:
            print(c,"\nCould not get Page Amount.")
            sys.exit()    


    def responsibleReq(self,data,perp,method):
        st = time.time()
        if method == 'get':
            requests.get(data['url'], params=data['params']).json()
        else:
            requests.post(data['url'], params=data['params']).json()
        end = time.time()
        if end - st < self.wait[perp]:
            time.sleep(self.wait[perp]-(end - st))
    
    


    
    
    def indexRequest(self,mot,page = []):
        st = time.time()
        if type(page) is not str and page != None:
            print('Page number must be passed as string')
            sys.exit()
        if mot == 'm':
            if page == None:
                response = requests.get(self.movieurl, params=self.params)
            else:
                response = requests.get(self.movieurl, params=self.params+['p',str(page)])
        elif mot == 't':
            if page == None:
                response = requests.get(self.tvurl, params=self.params)
            else:
                response = requests.get(self.tvurl, params=self.params+['p',str(page)])
        else:
            print(mot,"\nMust be 'm'ovie OR 't'v show.")
            sys.exit()
        end = time.time()
        if end - st < 2:
            time.sleep(self.minwait-(end - st))
        return response
    
    def reqjson(self,mot,page = None):
        x = self.req(mot,page=page)
        try:
            y = x.json()
        except:
            print(x.text,"\nCould not JSON.")
            sys.exit()
        if 'session missmatch' in y['reason']:
            return "Relogin"
        return x.json()
        
    def pagesamount(self,mot):
        x = self.reqjson(mot)
        if x == "Relogin":
            return x
        if 'total_pages' in x:
            return x['total_pages']
        else:
            print(c,"\nCould not get Page Amount.")
            sys.exit()
    def singleindex(self,mot,page= None):
        x = self.reqjson(mot,page)
        if x == "Relogin":
            return x 
        if 'items' in x:
            return x['items']
        else:
            print(c,"\nCould not get items on page: ",page)
            sys.exit()
    
    def totalindex(self,mot):
        index = []
        for i in range(self.pagenum(mot)):
            x = self.singleindex(self,mot,page = str(i+1))
            if x == "Relogin":
                return x 
            for o in x:
                index.append([html.unescape(o['title']),o['id']])
        return index






#response = requests.get('https://mobilevids.org/webapi/videos/tvshows.php', params=params)
#print(str(response.json())[:500])