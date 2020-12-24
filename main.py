###Imports
import requests
import os
import sys
import time
import html

class mvids():
    
    def __init__(self):
        
        ##Set active directery to location of script##
        self._setCWD()

        self._login()

    
    
    



        self.params = [('user_id', self.strings['user_id']),('token', self.strings['token'])]
        self.movieurl = self.strings['movieurl']
        self.tvurl = self.strings['tvurl']
        self.minwait=1
        self.pagenum = {'m':self.pagesamount('m'),'t':self.pagesamount('t')}
        self.movieindex, self.tvindex = self.totalindex('m'),self.totalindex('t')
        if "Return" in self.pagenum['m'] or "Return" in self.pagenum['t'] or "Return" in [self.movieindex,self.tvindex]:
            self.relogin = True
    
    def login(self):
        count = 0
        while True:
            try:
                data = {'data': '{"Name":"mickrich345@gmail.com","Password":"7897412563"}'}
                response = requests.post('https://mobilevids.org/webapi/user/login.php', data=data).json()
                self.user_id = response['id']
                self.token = response['auth_token']
                break
            except:
                print('Failed to login. Try#'+str(count))
                time.sleep(5)
                count += 1
                continue

    
    def responsibleRequest(self,data):
        st = time.time()
        requests.get(data['url'], params=data['params'])
        end = time.time()
        if end - st < 2:
            time.sleep(self.minwait-(end - st))
    
    
    def _setCWD(self):
        os.chdir(os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0])

    
    
    def req(self,mot,page = []):
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
    def _login





#response = requests.get('https://mobilevids.org/webapi/videos/tvshows.php', params=params)
#print(str(response.json())[:500])