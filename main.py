###Imports
import requests
import os
import sys
import time
import html
import logging

class mvids():
    
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        
        self.test = False
        self.test = True
        logging.debug('This is a Test : '+str(self.test))
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
        self.wait = {'login':0,'pagesamount':0,'totalindex':0,'moviepage':0,'showpage':0,'addMovie':0,'appendEpisodes':0,'appendShow':0}
        
        ##Set active directery to location of script ##
        self._setCWD()
        self.s = requests.session()
        logging.debug('Session Initiated')
        ##Set Variables self.user_id and self.token ## 
        self.login()

        ## Return length of pages
        self.pagenum = {'m':self.pagesamount('m'),'t':self.pagesamount('t')}
        logging.debug(f"There are {self.pagenum['m']} pages of movies\nThere are {self.pagenum['t']} pages of TV Shows")
        self.movieindex, self.tvindex = self.totalindex('m'),self.totalindex('t')
        logging.debug(f"Pulled {len(self.movieindex)} movies and {len(self.tvindex)} TV Shows.")
    def _setCWD(self):#Set CWD to Script Location
        os.chdir(os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0])
        logging.debug(f'Set {os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0]} as CWD')
    def login(self):#Login

        data = {'data': '{"Name":"'+self.username+'","Password":"'+self.code+'"}'}
        response = self.respCall(self.loginURL,'login','post',data = data)

        self.user_id = response['id']
        self.token = response['auth_token']
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
            logging.debug(f"Pulling page {str(i)} of {str(self.pagenum[mot]+1)}")
            params=[['user_id',self.user_id],['token',self.token],['p',str(i)]]
            if mot == 'm':
                response = self.respCall(self.indexMovieURL,'totalindex','get',params = params)
            elif mot == 't':
                response = self.respCall(self.indexTvURL,'totalindex','get',params = params)
            else:
                print(mot,"\nMust be 'm'ovie OR 't'v show.")
                sys.exit()

            for q in response['items']:
                index[str(q['id'])] = {'TITLE':html.unescape(q['title'])}

        return index   
    def appendMovieIndex(self,id,info):#Add URLs to Movie
        for a in range(2):
            try:
                self.movieindex[id].update(info)
                return
            except:
                print('Not found Refreshing List...')
                self.movieindex = self.totalindex('m')
        logging.debug(f"{id} is invalid")
    def addMovie(self,id):#Get Movie URLs and Update
        params = [['id', id],['user_id',self.user_id],['token',self.token]]
        url = self.MovieScreenURL
        response = self.respCall(url,'addMovie','get',params = params)
        x = self.respParse(response,'addMovie')
        self.appendMovieIndex(id,x)
    def appendEpisodes(self,id,season):#Get URL for entire season
        for a in range(2):
            try:
                if season in str(self.tvindex[id].get('season_list')):
                    url = self.EpisodeScreenURL
                    params =[['show_id', id],['season',season],['user_id',self.user_id],['token',self.token]]
                    response = self.respCall(url,'appendEpisodes','get',params = params)
                    x = self.respParse(response,'appendEpisodes')
                    self.tvindex[id][season] = {q['episode']:[q.get('src_free_sd'),q.get('src_vip_sd'),q.get('src_vip_hd'),q.get('src_vip_hd_1080p')] for q in x['episodes']}
                    return
                else:
                    logging.debug('Asked for episode before show')
                    return
            except:
                print('Not found Refreshing List...')
                self.tvindex = self.totalindex('t')
        logging.debug(f"{id} is invalid")
    def appendShow(self,id):# Get Show Meta Data
        params = [['show_id', id],['user_id',self.user_id],['token',self.token]]
        url = self.MainShowURL
        response = self.respCall(url,'appendShow','get',params = params)
        parsed = self.respParse(response,'appendShow')

        for a in range(2):
            try:
                self.tvindex[id]['season_list'] = list(parsed['season_list'].keys())
                return
            except:
                print('Not found Refreshing List...')
            self.tvindex = self.totalindex('t')
        logging.debug(f"{id} is invalid")
    
    def printTV(self):#Print all TV Shows
        print("All TV shows:\n")
        for i in self.tvindex:
            print(i,' : ',self.tvindex[i])
    def printMovie(self):#Print all Movies
        print("All movies:\n")
        for i in self.movieindex:
            print(i,' : ',self.movieindex[i])
    def isMovieDown(self,id):
        try:
            x = self.movieindex[id]['src_free_sd']
            return True
        except:
            return False
    def isShowDown(self,id):
        try:
            x = self.tvindex[id]['season_list']
            return True
        except:
            return False
    def isSeasonDown(self,id,season):
        try:
            x = self.tvindex[id][season]
            return True
        except:
            return False
    def isEpisodeDown(self,id,season,ep):
        try:
            x = self.tvindex[id][season][ep]
            return True
        except:
            return False
    def getMovieURL(self,id):
        if self.isMovieDown(id):
            return (self.movieindex[id]['src_free_sd'],self.movieindex[id]['src_vip_sd'],self.movieindex[id]['src_vip_hd'],self.movieindex[id]['src_vip_hd_1080p'])
        else:
            logging.debug('Movie URL Unknown')
            return False
    def getEpisodeURL(self,id,season,ep):
        if self.isEpisodeDown(id,season,ep):
            return self.tvindex[id][season][ep]
        else:
            logging.debug('Episode URL Unknown')
            return False
    def getSeasonURL(self,id,season):
        if self.isSeasonDown(id,season):
            return [i for i in self.tvindex[id][season]]
        else::
            logging.debug('Episode URL Unknown')
            return False


x = mvids()
while True:
    x.printMovie()
    x.addMovie(input('id'))
    x.printMovie()
    x.printTV()
    x.appendShow(input('id'))
    x.printTV()
    x.printTV()
    x.appendEpisodes(input('id'),input('sea'))
    x.printTV()


        




