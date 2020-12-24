import requests
import os
import sys
import time
import html
class indexy():
    def __init__(self):
        os.chdir(os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0])
        try:
            with open('indexmakerstrings.txt','r') as n:
                self.strings = {i.split('::')[0].rstrip():i.split('::')[1].rstrip() for i in n.readlines()}
        except:
            print(os.getcwd(),"\nCant Find "'indexmakerstrings.txt')
            sys.exit()
        self.params = [('user_id', self.strings['user_id']),('token', self.strings['token'])]
        self.movieurl = self.strings['movieurl']
        self.tvurl = self.strings['tvurl']
        self.minwait=1
        self.pagenum = {'m':pagesamount('m'),'t':pagesamount('t')}
        self.movieindex, self.tvindex = self.totalindex('m'),self.totalindex('t')

    def req(self,mot,page = None):
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
            self.relogin()
        return x.json()
        



    def pagesamount(self,mot):
        x = self.reqjson(mot)
        if 'total_pages' in x:
            return x['total_pages']
        else:
            print(c,"\nCould not get Page Amount.")
            sys.exit()
    def singleindex(self,mot,page= None):
        self.reqjson(mot,page)
        if 'itms' in x:
            return x['items']
        else:
            print(c,"\nCould not get items on page: ",page)
            sys.exit()
    
    def totalindex(self,mot):
        index = []
        for i in range(self.pagenum(mot)):
            x = singleindex(self,mot,page = str(i+1))
            for o in x:
                index.append([html.unescape(o['title']),o['id']])
        return index




#response = requests.get('https://mobilevids.org/webapi/videos/tvshows.php', params=params)
#print(str(response.json())[:500])