###Imports
import requests
import os
import sys
import time
import html

class mvids():
    
    def __init__(self):

        self.test = False
        ##URLs for indexing Movies and TV##
        self.indexMovieURL = 'https://mobilevids.org/webapi/videos/movies.php'
        self.MainShowURL='https://mobilevids.org/webapi/videos/get_season.php'
        self.EpisodeScreenURL='https://mobilevids.org/webapi/videos/get_episodes.php'
        self.MovieScreenURL = 'https://mobilevids.org/webapi/videos/get_video.php'
        self.indexTvURL = 'https://mobilevids.org/webapi/videos/tvshows.php'
        self.loginURL = 'https://mobilevids.org/webapi/user/login.php'
        self.username = 'mickrich345@gmail.com'
        self.code = "7897412563"
        self.masterkeys = {'login':['id','auth_token'],'pagesamount':['total_pages'],'totalindex':['items'],'addMovie':['src_free_sd','src_vip_sd','src_vip_hd','src_vip_hd_1080p'],'appendShow':['season_list'],'appendEpisodes':['episodes']}
        self.opt=['src_free_sd','src_vip_sd','src_vip_hd','src_vip_hd_1080p']
        ##Set minimum execution times for different requests ##
        self.wait = {'login':1,'pagesamount':1,'totalindex':1,'moviepage':1,'showpage':1,'addMovie':1,'appendEpisodes':1}
        
        ##Set active directery to location of script ##
        self._setCWD()
        self.s = requests.session()
        ##Set Variables self.user_id and self.token ## 
        self.login()

        ## Return length of pages
        self.pagenum = {'m':self.pagesamount('m'),'t':self.pagesamount('t')}
        self.movieindex, self.tvindex = self.totalindex('m'),self.totalindex('t')
        print(len(self.movieindex),len(self.tvindex))

    def respCall(self,url,master,method,params = dict(a=None),data = dict(a=None)):#Call and ensure proper format
        failed = 1
        while True:
            st = time.time()# Get Start Time
            
            if method == 'get': #Check Method
                response = self.s.get(url,params=params,data = data)
            elif method == 'post':
                response = self.s.post(url,params=params,data = data)
            else:
                print("Must be post OR get.")
                sys.exit()
            
            end = time.time()# Get End Time
            
            if end - st < self.wait[master]:# Wait Predetermined Time
                time.sleep(self.wait[master]-(end - st))
            
            try:# Parse as JSON
                y = response.json()
            
            except:#If fail try agin 3 time
                if failed < 4:
                    print(response.text,"\nCould not JSON. Sleeping ",5*failed,' seconds.')
                    time.sleep(5*failed)
                    failed +=1
                    continue
                else:
                    print(response.text,"\nCould not JSON. Exiting")
                    sys.exit()
            if 'session missmatch' in str(y.get('reason')):
                self.login()
                continue
            z = self.respParse(y,master)
            if z == False:
                print('Could not find ',master, ' keys in ',y,'\nTrying Again.' )
                time.sleep(5)
                continue
            break
        return z
    def respParse(self,data,master):#Ensure corect return
        parseddata = {}
        for i in self.masterkeys[master]:
            if data.get(i) == None and i not in self.opt:
                return False
            else:
                parseddata[i] = data.get(i)
        return parseddata
    def login(self):#Login

        data = {'data': '{"Name":"'+self.username+'","Password":"'+self.code+'"}'}
        response = self.respCall(self.loginURL,'login','post',data = data)

        self.user_id = response['id']
        self.token = response['auth_token']
    def _setCWD(self):#Set CWD to Script Location
        os.chdir(os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0])
    def pagesamount(self,mot):#Get Amount OF pages
        params=[['user_id',self.user_id],['token',self.token]]
        if mot == 'm':
            response = self.respCall(self.indexMovieURL,'pagesamount','get',params = params)
        elif mot == 't':
            response = self.respCall(self.indexTvURL,'pagesamount','get',params = params)
        else:
            print(mot,"\nMust be 'm'ovie OR 't'v show.")
            sys.exit()

        return int(response['total_pages'])
    def totalindex(self,mot):#Get all TV shows And Movies
        index = {}
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

            index = index + [{'TITLE':html.unescape(z['title']),'ID':z['id']} for z in response['items']]

        return index   
    def appendMovieIndex(self,id,info):#Add URLs to Movie
        while True:
            amount = len(self.movieindex)
            for i in range(amount):
                if str(self.movieindex[i]['ID']) == str(id):
                    self.movieindex[i].update(info)
                    return
            print('Not found Refreshing List...')
            self.movieindex = self.totalindex('m')
    def addMovie(self,id):#Get Movie URLs and Update
        params = [['id', id],['user_id',self.user_id],['token',self.token]]
        url = self.MovieScreenURL
        response = self.respCall(url,'addMovie','get',params = params)
        x = self.respParse(response,'addMovie')
        self.appendMovieIndex(id,x)
    def appendEpisodes(self,id,season,info):#Get URL for entire season
        while True:
            amount = len(self.tvindex)
            for i in range(amount):
                if str(self.movieindex[i]['ID']) == str(id) and season in self.movieindex[i]['season_list']:
                    url = self.EpisodeScreenURL
                    params =[['show_id', id],['season',str(i)],['user_id',self.user_id],['token',self.token]]
                    response = self.respCall(url,'appendEpisodes','get',params = params)
                    x = self.respParse(response,'appendEpisodes')
                    self.movieindex[i][season] = {q['episode']:[q.get('src_free_sd'),q.get('src_vip_sd'),q.get('src_vip_hd'),q.get('src_vip_hd_1080p')] for q in x['episodes']}
                    return
            print('Not found Refreshing List...')
            self.movieindex = self.totalindex('t')
    def appendShow(self,id):# Get Show Meta Data
        params = [['show_id', id],['user_id',self.user_id],['token',self.token]]
        url = self.MainShowURL
        response = self.respCall(url,'appendShow','get',params = params)
        parsed = self.respParse(response,'appendShow')

        while True:
            amount = len(self.tvindex)
            for i in range(amount):
                if str(self.movieindex[i]['ID']) == str(id):
                    self.movieindex[i]['season_list'] = list(parsed.keys())
                    return
            print('Not found Refreshing List...')
            self.movieindex = self.totalindex('t')
    def printTV(self):#Print all TV Shows
        for i in self.tvindex:
            print(i['TITLE'],' : ',i['ID'])

    def printMovie(self):#Print all Movies
        for i in self.movieindex:
            print(i['TITLE'],' : ',i['ID'])
    def tvIDCheck(self,id):#Check if TV Show ID is in system
        for i in self.tvindex:
            if str(i['ID']) == str(id):
                return True
        return False
    
    
    def movieIDCheck(self,id):#Check if Movie ID is in system
        for i in self.movieindex:
            if str(i['ID']) == str(id):
                return True
        return False

    def printMovieURL(self,id):
        if movieIDCheck(id):
            print([self.movieindex])

x = mvids()
x.printMovie()
x.printTV()

        





#response = requests.get('https://mobilevids.org/webapi/videos/tvshows.php', params=params)
#print(str(response.json())[:500])