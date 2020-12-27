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
        self.ShowScreenURL='https://mobilevids.org/webapi/videos/get_season.php'
        self.EpisodeScreenURL='https://mobilevids.org/webapi/videos/get_episodes.php'
        self.MovieScreenURL = 'https://mobilevids.org/webapi/videos/get_video.php'
        self.indexTvURL = 'https://mobilevids.org/webapi/videos/tvshows.php'
        self.loginURL = 'https://mobilevids.org/webapi/user/login.php'
        self.username = 'mickrich345@gmail.com'
        self.code = "7897412563"
        
        ##Set minimum execution times for different requests ##
        self.wait = {'login':1,'pagesamount':1,'totalindex':1,'moviepage':1,'showpage':1}
        
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
        threeX = 0
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
                if threeX != 3:
                    threeX +=1
                    x = 0
                    print(response.text,"\nCould not JSON.Try Again in 15 sec")
                    time.sleep(15)
                    continue
                else:
                    print(response.text,"\nCould not JSON. Exiting")
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
        if 'not found' in str(info.get('reason')):
            self.movieindex = self.totalindex('m')
            return False
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
        return True
    def appendEpisodes(self,id,season,info):
        found = False

        if 'not found' in str(info.get('reason')):
            self.tvindex = self.totalindex('t')
            return False
        while True:
            amount = len(self.tvindex)
            for i in range(amount):
                if str(self.tvindex[i]['ID']) == str(id):
                    found = True
                    if self.tvindex[i].get('season_list') == None:
                        self.tvindex[i]['season_list'] = []

                    self.tvindex[i]['season_list'].append({season:{q['episode']:[q.get('src_free_sd'),q.get('src_vip_sd'),q.get('src_vip_hd'),q.get('src_vip_hd_1080p')] for q in info.get('episodes')}})
                    break
            if found == True:
                break
            else:
                self.tvindex = self.totalindex('t')
                continue
        return True

    def parseShow(self,id,info):
        found = False

        if 'not found' in str(info.get('reason')):
            self.tvindex = self.totalindex('t')
            return False
        while True:
            amount = len(self.tvindex)
            for i in range(amount):
                if str(self.tvindex[i]['ID']) == str(id):
                    found = True
                    return info.get('season_list').keys()
                    break
            if found == True:
                break
            else:
                self.tvindex = self.totalindex('t')
                continue
        return True
    
    def appendShow(self,id):
        

        params = [['show_id', id],['user_id',self.user_id],['token',self.token]]
        url = self.ShowScreenURL
        response = self.respCall(url,'moviepage','get',params = params)
        z= self.parseShow(id,response)

        url = self.EpisodeScreenURL
        for i in list(z) :       
            twoX = False
            while True:
                print('finish deson',i)
                params =[['show_id', id],['season',str(i)],['user_id',self.user_id],['token',self.token]]
                response = self.respCall(url,'moviepage','get',params = params)
                x = self.appendEpisodes(id,i,response)
                if x:
                    break
                else:
                    print('Clould not find this season. Trying again.')
                    if twoX == True:
                        print('Clould not find this season. Moving on to next one')
                        break
                    twoX = True
                    continue

    def appendMovie(self,id):
        twoX = False
        while True :
            params = [['id', id],['user_id',self.user_id],['token',self.token]]
            url = self.MovieScreenURL
            response = self.respCall(url,'moviepage','get',params = params)
            x = self.appendMovie(id,response)
            if x:
                break
            else:
                print('Clould not find. Trying again.')
                if twoX == True:
                    print('Could Not Find')
                    sys.exit()
                twoX = True
                continue   

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
    print(x.tvindex)
z= str(input('enter number of tv show'))
print(z,type(z))
x.appendShow(z)
print(x.tvindex)


#response = requests.get('https://mobilevids.org/webapi/videos/tvshows.php', params=params)
#print(str(response.json())[:500])