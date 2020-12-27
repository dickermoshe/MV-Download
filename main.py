###Imports
import requests
import os
import sys
import time
import html

class mvids():
    
    def __init__(self):

        self.test = True
        ##URLs for indexing Movies and TV##
        self.indexMovieURL = 'https://mobilevids.org/webapi/videos/movies.php'
        self.MovieScreenURL = 'https://mobilevids.org/webapi/videos/get_video.php'
        self.indexTvURL = 'https://mobilevids.org/webapi/videos/tvshows.php'
        self.loginURL = 'https://mobilevids.org/webapi/user/login.php'
        self.username = 'mickrich345@gmail.com'
        self.code = "7897412563"
        
        ##Set minimum execution times for different requests ##
        self.wait = {'login':1,'pagesamount':1,'totalindex':0,'moviepage':1}
        
        ##Set active directery to location of script ##
        self._setCWD()
        self.s = requests.session()
        ##Set Variables self.user_id and self.token ## 
        self.login()
        ## Return length of pages
        self.pagenum = {'m':self.pagesamount('m'),'t':self.pagesamount('t')}
        
        self.movieindex, self.tvindex = self.totalindex('m'),self.totalindex('t')
        print(len(self.movieindex),len(self.tvindex))

    def respCall(self,url,master,method,params = dict(a=None),data = dict(a=None)):
        x = 0
        while x == 0:
            x = 1
            st = time.time()
            if method == 'get':
                response = self.s.get(url,params=params,data = data)
            elif method == 'post':
                response = self.s.post(url,params=params,data = data)
            else:
                print("Must be post OR get.")
                sys.exit()
            end = time.time()
            
            if end - st < self.wait[master]:
                time.sleep(self.wait[master]-(end - st))
            try:
                y = response.json()
            except:
                print(response.text,"\nCould not JSON.")
                sys.exit()
            
            if 'session missmatch' in str(y.get('reason')):
                self.login()
                x = 0
                continue
        return y

    def login(self):


        data = {'data': '{"Name":"'+self.username+'","Password":"'+self.code+'"}'}
        response = self.respCall(self.loginURL,'login','post',data = data)

        self.user_id = response['id']
        self.token = response['auth_token']
    def appendMovie(self,id,info):
        found = False
        while True:
            amount = len(self.movieindex)
            for i in range(amount):
                if str(self.movieindex[i]['ID']) == str(id):
                    found = True
                    self.movieindex[i].update(info)
                    break
            if found == True:
                break
            else:
                self.movieindex = self.totalindex('m')
                continue

            





    def moviepage(self,movieID):
        params = [['id', movieID],['user_id',self.user_id],['token',self.token]] 
        response = self.respCall(self.MovieScreenURL,'moviepage','get',params = params)
        self.appendMovie(movieID,response)
    
    def _setCWD(self):
        os.chdir(os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0])
    
    def pagesamount(self,mot):
        params=[['user_id',self.user_id],['token',self.token]]
        if mot == 'm':
            response = self.respCall(self.indexMovieURL,'pagesamount','get',params = params)
        elif mot == 't':
            response = self.respCall(self.indexTvURL,'pagesamount','get',params = params)
        else:
            print(mot,"\nMust be 'm'ovie OR 't'v show.")
            sys.exit()
        if 'total_pages' in response:
            return int(response['total_pages'])
        else:
            print(response,"\nCould not get Page Amount.")
            sys.exit()
    
    def totalindex(self,mot):
        index = []
        itera = range(1,self.pagenum[mot]+1) if not self.test else range(1,3)
        for i in itera:
            params=[['user_id',self.user_id],['token',self.token],['p',str(i)]]
            if mot == 'm':
                response = self.respCall(self.indexMovieURL,'totalindex','get',params = params)
            elif mot == 't':
                response = self.respCall(self.indexTvURL,'totalindex','get',params = params)
            else:
                print(mot,"\nMust be 'm'ovie OR 't'v show.")
                sys.exit()
            if 'items' in response:
                index = index + [{'TITLE':html.unescape(z['title']),'ID':z['id']} for z in response['items']]
            else:
                print(response,"\nPage Details not found.")
                sys.exit()
        return index
x = mvids()
if x.test:
    print(x.movieindex)
z= str(input('enter number of movie'))
print(z,type(z))
x.moviepage(z)
print(x.movieindex)


#response = requests.get('https://mobilevids.org/webapi/videos/tvshows.php', params=params)
#print(str(response.json())[:500])