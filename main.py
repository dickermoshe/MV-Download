
from android.storage import primary_external_storage_path

from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
import requests
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import os
import sys
import time
import pickle
from kivy.config import Config
from kivy.app import runTouchApp
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from threading import Thread

class MainApp(App):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        

        self.test = False
        #self.test = True
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
        self.quality=['480P','480P VIP','720P VIP','1080P VIP']
        self.seasonqualitynames=['480P','720P','1080P']
        ##Set minimum execution times for different requests ##
        self.wait = {'login':0,'pagesamount':0,'totalindex':0,'moviepage':0,'showpage':0,'addMovie':0,'appendEpisodes':0,'appendShow':0}
        ##Set active directery to location of script ##
        self._setCWD()
        self.s = requests.session()
        ##Set Variables self.user_id and self.token ## 
        self.login()
        
        ## Return length of pages
        
        self.movieindex, self.tvindex = self.getindex()

    def getindex(self):
        filename = 'pickled.bin'
        response = requests.get('http://15.188.77.209/pickled.bin', stream=True)
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        
        with open(filename,'rb') as n:
            x = pickle.load(n)
        os.remove(filename)
        return {str(i): x[0][i] for i in x[0]},{str(i): x[1][i] for i in x[1]}
        #return x[0],x[1]

    def _setCWD(self):#Set CWD to Script Location
        os.chdir(primary_external_storage_path())

    def login(self):#Login

        data = {'data': '{"Name":"'+self.username+'","Password":"'+self.code+'"}'}
        response = self.respCall(self.loginURL,'login','post',data = data)

        self.user_id = response['id']
        self.token = response['auth_token']
    def respCall(self,url,master,method,params = dict(a=None),data = dict(a=None)):#Call and ensure proper format
        failed = 1
        for hip in range(2):
            st = time.time()# Get Start Time
            
            if method == 'get': #Check Method
                response = self.s.get(url,params=params,data = data)
            elif method == 'post':
                response = self.s.post(url,params=params,data = data)
            else:
                print("Must be post OR get.")

            
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
    def parseURL(self,string):
        return string.replace(' ','%')
    def respParse(self,data,master):#Ensure corect return
        parseddata = {}
        for i in self.masterkeys[master]:
            if data.get(i) == None and i not in self.opt:
                return False
            else:
                parseddata[i] = data.get(i)
        return parseddata

    def appendMovieIndex(self,id,info):#Add URLs to Movie
        for a in range(2):
            try:
                self.movieindex[id].update(info)
                return
            except:
                print('Not found Refreshing List...')
                self.movieindex = self.totalindex('m')

    def addMovie(self,id):#Get Movie URLs and Update
        if self.movieindex.get(id) == None:

            return False
        else:
            if self.movieindex.get(id).get('src_free_sd')!= None:
                return {i:self.movieindex.get(id).get(i) for i in self.opt}
        params = [['id', id],['user_id',self.user_id],['token',self.token]]
        url = self.MovieScreenURL
        response = self.respCall(url,'addMovie','get',params = params)
        x = self.respParse(response,'addMovie')
        self.appendMovieIndex(id,x)
        return x
    def appendEpisodes(self,id,season):#Get URL for entire season
        for a in range(2):
            try:
                if season in str(self.tvindex[id].get('season_list')):
                    if self.tvindex[id].get(season) != None:
                        return self.tvindex[id][season]
                    url = self.EpisodeScreenURL
                    params =[['show_id', id],['season',season],['user_id',self.user_id],['token',self.token]]
                    response = self.respCall(url,'appendEpisodes','get',params = params)
                    x = self.respParse(response,'appendEpisodes')
                    self.tvindex[id][season] = {str(q['episode']):[q.get('src_free_sd'),q.get('src_vip_sd'),q.get('src_vip_hd'),q.get('src_vip_hd_1080p')] for q in x['episodes']}
                    return self.tvindex[id][season]
                else:

                    return
            except:
                print('Not found Refreshing List...')
                self.tvindex = self.totalindex('t')

    def appendShow(self,id):# Get Show Meta Data
        if self.tvindex.get(id) == None:

            return False
        else:
            if self.tvindex.get(id).get('season_list')!= None:
                return self.tvindex.get(id).get('season_list')
        params = [['show_id', id],['user_id',self.user_id],['token',self.token]]
        url = self.MainShowURL
        response = self.respCall(url,'appendShow','get',params = params)
        parsed = self.respParse(response,'appendShow')

        for a in range(2):
            try:
                self.tvindex[id]['season_list'] = list(parsed['season_list'].keys())
                return self.tvindex[id]['season_list']
            except:
                print('Not found Refreshing List...')
            self.tvindex = self.totalindex('t')
    
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
            return False
    def getEpisodeURL(self,id,season,ep):
        if self.isEpisodeDown(id,season,ep):
            return self.tvindex[id][season][ep]
        else:
            return False
    def getSeasonURL(self,id,season):
        if self.isSeasonDown(id,season):
            return [i for i in self.tvindex[id][season]]
        else:
            return False
    def getSeasonStats(self,id,season):
        if self.tvindex.get(id) == None:
            return False
        elif self.tvindex[id].get(season) == None:
            return False            
        return list(self.tvindex[id][season].keys()).sort()
    def getMovieQuality(self,id):
        if self.isMovieDown(id):
            return (self.movieindex[id]['src_free_sd'],self.movieindex[id]['src_vip_sd'],self.movieindex[id]['src_vip_hd'],self.movieindex[id]['src_vip_hd_1080p'])
        else:
            return False
    def getEpisodeQuality(self,id,season,ep):
        print(self.isEpisodeDown(id,season,ep))
        if self.isEpisodeDown(id,season,ep):
            index = {}
            for i in range(len(self.tvindex[id][season][ep])):
                if len(self.tvindex[id][season][ep]) > 0:
                    index[self.quality[i]]=self.tvindex[id][season][ep][i]
            return index
        else:
            pass
    def letterlist(self,let,mse):
        index = self.tvindex if mse in 'se' else self.movieindex
        newindex = {}
        for i in index:
            if (index[i]['TITLE'][0].lower() == let.lower()) or  (index[i]['TITLE'][0].lower() not in 'abcdefghijklmnopqrstuvwxyz' and let.lower() == '#'):
                newindex[i] = index[i]['TITLE']
        if len(newindex) >0:
            return newindex
        else:
            print('ggggg')
            return False
    
    def getqualitylist(self,id,season):
        x = self.appendEpisodes(id,season)
        sd =[]
        hd = []
        fhd = []
        for i in x:
            sdplace = None
            hdplace = None
            fhdplace = None
            y = x[i]
            y.reverse()
            for o in range(len(y)):
                if y[o] != None:
                    if fhdplace == None:
                        fhdplace = o
                    if o > 1 and hdplace == None:
                        hdplace = o
                    if o > 2 and sdplace == None:
                        sdplace = o
                    if o > 3 and sdplace == None:
                        sdplace = o
            sd.append(y[sdplace])
            hd.append(y[hdplace])
            fhd.append(y[fhdplace])
        return sd,hd,fhd





    
    
    def make_f(self,i,o):
        def f(self):
            i(*o)
        return f
    def buttoniter(self,func,com):#com is dict
        functions = []
        
        for i in com:
            f = self.make_f(func,com[i])
            functions.append([f,i])
        return functions
            




    def main_screen(self):
        self.wipe()
        commands = {'Download Movies':['m'],'TV Shows : Season':['s'],'TV Shows : Episodes':['e']}



        for i in self.buttoniter(self.alpha,commands):
            tempbutton = Button(text=i[1],
                            size_hint=(.5, .5),
                            pos_hint={'center_x': .5, 'center_y': .5})
            tempbutton.bind(on_press= i[0])
            self.layout.add_widget(tempbutton)
            self.current_buttons.append(tempbutton)
    
    def gorightback(self):
        self.wipe()
        print('BEter',self.dontgetlost)
        if len(self.dontgetlost) == 1:
            del self.dontgetlost[-1]
            self.main_screen()
        else:
            x = self.dontgetlost[-2]

            del self.dontgetlost[-2]
            del self.dontgetlost[-1]

            
            if len(x) == 1:
                x[0]()
            else:
                x[0](*x[1])
                print('done')
        print('AFter',self.dontgetlost)
    
    def addBack(self):
        tempbutton = Button(text='Back',
                            size_hint=(.5, .5),
                            pos_hint={'center_x': .5, 'center_y': .5})
        tempbutton.bind(on_press=lambda widget: self.gorightback())    
        self.layout.add_widget(tempbutton)
        self.current_buttons.append(tempbutton)
    
    def alpha(self,mse):
        self.dontgetlost.append([self.alpha,[mse]])
        self.wipe()
        self.addBack()
        let = '#abcdefghijklmnopqrstuvwxyz'
        let = {i.upper():[i,mse] for i in let}
        print(let)
        for i in self.buttoniter(self.present,let):
            tempbutton = Button(text=i[1],
                            size_hint=(.5, .5),
                            pos_hint={'center_x': .5, 'center_y': .5})
            tempbutton.bind(on_press=i[0])
            self.layout.add_widget(tempbutton)
            self.current_buttons.append(tempbutton)
    
    
    def present(self,but,mse):
        x = self.letterlist(but,mse)
        if x == False:
            return
        self.dontgetlost.append([self.present,[but,mse]])
        self.wipe()
        self.addBack()
        if mse == 'm':
            let = {x[i]:[mse,i] for i in x}

            for i in self.buttoniter(self.moviepresent,let):
                tempbutton = Button(text=i[1],
                                size_hint=(.5, .5),
                                pos_hint={'center_x': .5, 'center_y': .5})
                tempbutton.bind(on_press=i[0])
                self.layout.add_widget(tempbutton)
                self.current_buttons.append(tempbutton)
        if mse in 'es':
            let = {x[i]:[mse,i] for i in x}

            for i in self.buttoniter(self.seasonpresent,let):
                tempbutton = Button(text=i[1],
                                size_hint=(.5, .5),
                                pos_hint={'center_x': .5, 'center_y': .5})
                tempbutton.bind(on_press=i[0])
                self.layout.add_widget(tempbutton)
                self.current_buttons.append(tempbutton)
    
    def moviepresent(self,mse,id):
        self.dontgetlost.append([self.moviepresent,[mse,id]])
        self.wipe()
        self.addBack()
        self.addMovie(id)
        x = self.getMovieURL(id)
        y = {}
        for i in range(len(x)):
            if x[i] == None or len(str(x[i])) < 1:
                continue
            else:
                y[self.quality[i]] = x[i]
        let = {i:[y[i]] for i in y}
        for i in self.buttoniter(self.downURL,let):
            tempbutton = Button(text=i[1],
                            size_hint=(.5, .5),
                            pos_hint={'center_x': .5, 'center_y': .5})
            tempbutton.bind(on_press=i[0])
            self.layout.add_widget(tempbutton)
            self.current_buttons.append(tempbutton)

    def seasonpresent(self,mse,id):
        self.dontgetlost.append([self.seasonpresent,[mse,id]])
        self.wipe()
        self.addBack()
        x = self.appendShow(id)
        x.reverse
        #x = self.getMovieURL(id)
        
        x = {'Season ' + str(i):[mse,id,str(i)] for i in x}
        if mse == 'e':
            y  = self.buttoniter(self.episodepresent,x)
        else:
            y  = self.buttoniter(self.seasonquality,x)
        

        for i in y:
            tempbutton = Button(text=i[1],
                            size_hint=(.5, .5),
                            pos_hint={'center_x': .5, 'center_y': .5})
            tempbutton.bind(on_press=i[0])
            self.layout.add_widget(tempbutton)
            self.current_buttons.append(tempbutton)
        
    def seasonquality(self,mse,id,season):
        self.dontgetlost.append([self.seasonquality,[mse,id,season]])
        self.wipe()
        self.addBack()
        
        x = self.getqualitylist(id,season)
        y = {}
        for i in range(3):
            y[self.seasonqualitynames[i]] = x[i]
        let = {i:[y[i]] for i in y}
        for i in self.buttoniter(self.threaddownmany,let):
            tempbutton = Button(text=i[1],
                            size_hint=(.5, .5),
                            pos_hint={'center_x': .5, 'center_y': .5})
            tempbutton.bind(on_press=i[0])
            self.layout.add_widget(tempbutton)
            self.current_buttons.append(tempbutton)


    def episodepresent(self,mse,id,season):
        self.dontgetlost.append([self.episodepresent,[mse,id,season]])
        self.wipe()
        self.addBack()
        x = self.appendEpisodes(id,season)
        let = {'Episode ' + str(i):[mse,id,season,i] for i in x}
        for i in self.buttoniter(self.episodequality,let):
            tempbutton = Button(text=i[1],
                            size_hint=(.5, .5),
                            pos_hint={'center_x': .5, 'center_y': .5})
            tempbutton.bind(on_press=i[0])
            self.layout.add_widget(tempbutton)
            self.current_buttons.append(tempbutton)
    
    
    
    def episodequality(self,mse,id,season,ep):
        self.dontgetlost.append([self.episodequality,[mse,id,season,ep]])
        self.wipe()
        self.addBack()
        x = self.getEpisodeURL(id,season,ep)
        y = {}
        for i in range(len(x)):
            if x[i] == None or len(str(x[i])) < 1:
                continue
            else:
                y[self.quality[i]] = x[i]
        let = {i:[y[i]] for i in y}
        for i in self.buttoniter(self.downURL,let):
            tempbutton = Button(text=i[1],
                            size_hint=(.5, .5),
                            pos_hint={'center_x': .5, 'center_y': .5})
            tempbutton.bind(on_press=i[0])
            self.layout.add_widget(tempbutton)
            self.current_buttons.append(tempbutton)

    def threaddownmany(self,listofurl):
        self.listofurlsfordown = listofurl
        
        downloadmany = Thread(target=self.downmanyURL,daemon=True)

        downloadmany.start()
    def downmanyURL(self):
        listofurl =self.listofurlsfordown
        self.progress = Label(text='Downloading '+str(len(listofurl)) + ' Episodes\n')
        x = 'Downloading '+str(len(listofurl)) + ' Episodes\n'
        self.popup = Popup(title='Downloading', content=self.progress,size_hint=(.5, .5),
              auto_dismiss=False)
        self.popup.open()

        for i in range(len(listofurl)):
            self.progress.text = x + 'Downloading '+str(i+1) + ' out of ' + str(len(listofurl))
            if i+1 == len(listofurl):
                self.downURLsin(listofurl[i],last = True)
            else:
                self.downURLsin(listofurl[i])

    def downURLsin(self,url,last = False):

        self.activeurl = url
        self.last = last
        download = Thread(target=self.act4manydown,daemon=True)

        # Starts the new thread
        download.start()
        download.join()

    def downURL(self,url):
        self.progress = Label(text='Please wait.\nThis window will close\nwhen download is complete.\n')
        
        self.popup = Popup(title='Downloading', content=self.progress,size_hint=(.5, .5),
              auto_dismiss=False)
        self.popup.open()
        self.activeurl = url
        print('hi')
        download = Thread(target=self.actdown,daemon=True)

        # Starts the new thread
        download.start()
        print('hi')
        
    def perc(self,x,total):
        return "%.0f%%" % (100 * x/total)   
        
        
        
        #self.popup.dismiss()

    def actdown(self):
        response = requests.get(self.activeurl, stream = True)
        total_size_in_bytes= int(response.headers.get('content-length', 0))
        
        filename = self.activeurl.split('/')[-1].split('?xhk')[0]
        completed = 0
        text_file = open(filename,"wb")
        for chunk in response.iter_content(chunk_size=1024):
            text_file.write(chunk)
            completed += len(chunk)
            self.progress.text = 'Please wait.\nThis window will close\nwhen download is complete.\n'+self.perc(completed,total_size_in_bytes)
        text_file.close()
        self.popup.dismiss()
    def act4manydown(self):
        x = self.progress.text
        response = requests.get(self.activeurl, stream = True)
        total_size_in_bytes= int(response.headers.get('content-length', 0))
        
        filename = self.activeurl.split('/')[-1].split('?xhk')[0]
        completed = 0
        text_file = open(filename,"wb")
        for chunk in response.iter_content(chunk_size=1024):
            text_file.write(chunk)
            completed += len(chunk)
            self.progress.text = x+'\n'+self.perc(completed,total_size_in_bytes)
        text_file.close()
        if self.last:
            self.popup.dismiss()
    
    
    def wipe(self):
        if self.current_buttons == None:
            pass
        else:
            for i in self.current_buttons:
                self.layout.remove_widget(i)
        self.current_buttons = []
            
        #1:Main screen
        
        #A2:Movie : Letter screen
        #A3:Movie : Movie Screen - atr = Letter >> Quality
        

        #B2:Season : Letter Screen
        #B3:Season : Show Screen - atr = Letter >> Quality

        #C2:Episode : Letter screen
        #C3:Episode : Show Screen - atr = Letter
        #C3:Episode : Season Screen - atr = Season
        #C4:Episode : Episode Screen - atr = Season Episode >> Quality
        
        #D Quality
        
        #always have back buttons
        self.newbuttons=[] 




    def build(self):
        self.dontgetlost = []
        self.current_buttons = None
        self.layout = GridLayout(cols=2, size_hint_y=None,row_force_default=True, row_default_height=40)
        self.layout.bind(minimum_height=self.layout.setter("height"))
        
        Window.size = (500, 500)
        self.root = ScrollView(size_hint_x=1 , size=(Window.width, Window.height))
        self.root.add_widget(self.layout)
        self.main_screen()
        return self.root

    def on_press_button(self, instance):
        self.layout.remove_widget(self.button)

if __name__ == '__main__':
    app = MainApp()
    app.run()
