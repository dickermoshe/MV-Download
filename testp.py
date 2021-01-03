
import kivy
from kivy.config import Config
from kivy.app import runTouchApp
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

class TestApp(App):

    def build(self):
        self.layout = GridLayout(cols=2, size_hint_y=None,row_force_default=True, row_default_height=Window.height/10)
        self.layout.bind(minimum_height=self.layout.setter("height"))
        self.root = ScrollView(size_hint_x=1 , size=(Window.width, Window.height))
        self.root.add_widget(self.layout)
        for i in range(10):
            tempbutton = Button(text=f'hi{i}',size_hint=(.5, .5))
            tempbutton.bind(on_press=lambda x : self.move())
            self.layout.add_widget(tempbutton)
        tempbutton = Button(text=f'activate',size_hint=(.5, .5))
        tempbutton.bind(on_press=lambda x : self.deb())
        self.layout.add_widget(tempbutton)
        self.x = FloatLayout(size=Window.size)
        print(self.x.size)
        self.x.add_widget(self.root)
        self.btn = Button(text ='Hello world',
                    pos =(400, 300),size_hint =(.05, .05)) 
        self.x.add_widget(self.btn)
        return self.x
    def move(self):
        origin = (5,5)
        setx,sety = (5,5)
        sety = sety + self.btn.size[1]
        sety = (sety * -1) + Window.size[1]

        print(sety)
        self.btn.pos = (setx,sety)
        print('LOL')
        print(self.x.size)
        def FindPoint(x1, y1, x2,  y2, x, y) : 
            if (x > x1 and x < x2 and y > y1 and y < y2) : 
                return True
            else : 
                return False
            
        
        print(self.btn.size)
        x = origin[0]
        y = origin[1]
        print(x,y)
        


        for i in self.layout.children:
            print(i.text)
            x1 , y1 = i.pos
            x2 , y2 =x1+i.size[0]/2,y1+i.size[1]/2
            print(i.text,x1 , y1),
            if FindPoint(x1, y1, x2, y2, x, y) : 
                print(i.text,'Yesssss',x1, y1, x2, y2, x, y) 
            else : 
                print("No") 
            

    def deb(self):
        pass
    

if __name__ == '__main__':
    TestApp().run()

    # Python3 program to Check  
# if a point lies on or  
# inside a rectangle | Set-2 
  
# function to find if  
# given point lies inside  
# a given rectangle or not. 
def FindPoint(x1, y1, x2,  
              y2, x, y) : 
    if (x > x1 and x < x2 and 
        y > y1 and y < y2) : 
        return True
    else : 
        return False
  
# Driver code 
if __name__ == "__main__" : 
  
    # bottom-left and top-right 
    # corners of rectangle. 
    # use multiple assigment 
    x1 , y1 , x2 , y2 = 0, 0, 10, 8
  
    # given point 
    x, y = 1, 5
  
    # function call 
    if FindPoint(x1, y1, x2,  
                 y2, x, y) : 
        print("Yes") 
    else : 
        print("No") 
  
# This code is contributed 
# by Ankit Rai 
