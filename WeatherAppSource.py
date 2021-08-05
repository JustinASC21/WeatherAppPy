'''
This pygame project will work with my web scrapping graph
used to find the temperatures for the next 24 hours
Weather data used courtesy to  National Weather Service Forecast Office
https://www.weather.gov/okx/
I will provide my matplotlib graph as an image that I have saved
into this pygame project
'''
import requests
from bs4 import BeautifulSoup
import lxml
import matplotlib.pyplot as pl
import random
import pygame as py
import pyautogui as pg
import time


# we can declare global variables to be used everywhere
global back_image # variable for background image
global data_list
global current_hour

# this returns to us the current hour
current_hour = time.localtime()[3] # we can parse the data only when the hour has changed so we do not have to continue sending requests

def weatherData():
    # this function will collect the data and parse the information
    # National Weather Service Forecast Office which contains data for temperatures

    current_hour = time.localtime()[3] # we update our current hour when we parse

    url = "https://forecast.weather.gov/MapClick.php?w0=t&w7=rain&w8=thunder&AheadHour=0&Submit=Submit&&FcstType=digital&textField1=40.6925&textField2=-73.9904&site=all"

    print("Data collected from https://www.weather.gov/okx/")
    print()

    weather_page = requests.get(url)
    print("A request to the webpage was sent") # informs us when a request was sent to the web
    parsed_weather = BeautifulSoup(weather_page.text, 'lxml')

    data_list = []
    # find hours and temp for the change in temperature from parsed website
    data = parsed_weather.find_all('b') # our data is stored in b tags
    for data_points in data:
        data_list.append(data_points.get_text()) # we grab the text only, saves us html elements included

    # start hour will be the where we will start collecting our hour data
    start_hour = data_list.index(str(current_hour)) if current_hour > 9 else data_list.index(f"0{current_hour}") # --> returns the index, which we can reference later
    global  hour_list # makes our variable global so we can use it everywhere
    hour_list = data_list[start_hour:start_hour+24] # covers 24 hr data


    def US_Time(hours_list):
        # will convert the times retrieved by the website into 12hr format
        for i in range(len(hours_list)):
            # i will be the index of the hour in hours_list
            cur_hour = hours_list[i]
            if cur_hour  == "00":
                hours_list[i] = "12 am"
            elif int(cur_hour) < 12:
                # here the hours are in the morning
                hours_list[i]= cur_hour + " am"
            else:
                # hours are in the afternoon
                if int(cur_hour) == 12:
                    hours_list[i] = cur_hour + " pm" # hour is 12 in the afternoon
                else:
                    hours_list[i] = str(int(cur_hour) - 12) + " pm" # hour is in the afternoon all we have to do is add pm

        return hours_list
        
    US_Time(hour_list)

    global temp_list
    temp_list = [int(data) for data in data_list[start_hour+24:start_hour+48]] # we grab the temperature data right after the hour data ends,
    # because the data is 24 items long we can add this by 24 again to add it 48 overall

    # close the connection
    weather_page.close()
    print("The request to the main page has been closed") # tells us when the request closed

def prepare_graph(x,y,labelcolor,tick_width,linestyle,hours):
    # here we set the new range based on how far the user wants to see the data
    x_plot = x[:0+hours]
    y_plot = y[:0+hours]

    # create subplots
    fig, ax = pl.subplots()
    # plot the graph
    ax.plot(x_plot,y_plot)
    ax.grid(True,linestyle = linestyle)
    # below are styles
    ax.tick_params(axis='x',labelcolor=labelcolor[0], labelsize='medium', width=tick_width,labelrotation=67)
    ax.tick_params(axis='y',labelcolor=labelcolor[-1],labelsize="medium")
    # label rotation rotates the tick labels to promote readability

    pl.xlabel("Next Hours")
    pl.ylabel("Temp (°F)")
    pl.title(f"Temperatures for the following {hours} hours")
    # we save our graph as an image for future reference
    pl.savefig(fname = "weather.png",format="png")
    return "weather.png"

# initialize pygame
py.init()

# we create a window here with size (720,600)
size = (720,600)
back_color = (0,255,255)
screen = py.display.set_mode(size) # set up the window

# our surface which we may need to load images
surface = py.display.get_surface()
# background image coords
imgx = 0
imgy = 0
def drawBackground(filename,x,y):
    # this posts the background image
    back_image = py.image.load(filename).convert(surface)
    # displays image to display on surface perfectly as it is (720,600) size
    surface.blit(back_image,(x,y))


# graphButtonsPresent is a boolean referring to if the buttons on the main screen are present or not
weatherData() # --> here we parse the data and collect our data for the next 24 hrs
graphButtonsPresent = True
while True:
    # check if py.event is quit when user closes out of tab
    for event in py.event.get():
        if event.type == py.QUIT:   # will exit the window / game
            exit()
        # we can check if the mouse is pressed down, and if it is, we should check if it is clicking on the button
        if event.type == py.MOUSEBUTTONDOWN:
            # if the buttons in the main screen are present then we should check if they are within the location of the buttons
            x = py.mouse.get_pos()[0]
            y = py.mouse.get_pos()[-1]

            if graphButtonsPresent:
                if (x >= 225 and x <515) and (y>=390 and y <475): # this is the rect area for check Temp button

                    def graph_plot(graphBackgroundImage = ""):
                        # our graphBackgroundImage will be different as it will have a "back" button
                        # if the image is present, then we should not check for event.types and mouseButtonDown
                        # as the buttons to graph will be covered
                        # we can show a pop up dialogue to direct the user to type in a correct range with pyautogui

                        user_hours = pg.prompt(title="Enter a number here",text="Enter a number for hours from 2 to 24")

                        # we should provide error handling so program does not break when user does not enter any data
                        if user_hours == "" or user_hours is None:
                            drawBackground("weather_front.png",imgx,imgy)
                        elif (int(user_hours )== 0 or int(user_hours) == 1) or int(user_hours) > 24:
                            drawBackground("weather_front.png",imgx,imgy)
                        else:
                            # produce the image with given user data
                            if current_hour != time.localtime()[3]: # --> This checks if the recorded current hour is not equal to the actual current hour
                                # if they are different, then that means the hour has increased as time passed, and we have to parse our data again for the new next 24 hours
                                weatherData() # --> this parses and updates the new data
                                weather_image = prepare_graph(hour_list,temp_list,['red' ,'blue'],4,'-.',int(user_hours)) # --> returns the filename as png

                            else: # --> This prevents from repeating the requests to a website and overwhelming the server

                                # else if the current hour is == to time.localtime()[3] then there is no need to grab the data
                                weather_image = prepare_graph(hour_list,temp_list,['red' ,'blue'],4,'-.',int(user_hours))  # --> returns the filename as png

                            drawBackground(graphBackgroundImage,imgx,imgy)
                            drawBackground(weather_image,40,75) # --- > Here we draw the graph
                            global graphButtonsPresent
                            graphButtonsPresent = False

                    graph_plot("graph_back.png")
            else:
                # in the case in which the graphButtons are not present then we are displaying the second screen when the user is looking at the graph
                # we could check if the mouseclick was around the "Back" button in our second screen
                if (y>10 and y <=70) and (x > 580 and x <=715): # ---> The back button is located in between these coordinates for x and y respective
                    # if the mouse click was in this area, we can go back to the main screen
                    drawBackground("weather_front.png",imgx,imgy)
                    graphButtonsPresent = True
    # check if graph is presented to the user or not
    if graphButtonsPresent:
        drawBackground("weather_front.png",imgx,imgy)

    # to keep screen updated we call this function
    py.display.flip()
