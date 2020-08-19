import xml.etree.ElementTree as ET
from six.moves.urllib import request
import requests
import tkinter as tk
from PIL import Image, ImageTk
import datetime
import math
import WeatherHistory



class CreateXML:
    def __init__(self):
#        url = 'https://www.yr.no/sted/Norge/Viken/Rollag/Vegglifjell_skisenter/'
#        self.reset_XML()
#        self.add_location_xml(url)
#        self.remove_location_xml(url)
#        self.update_all_tabulars()
        pass

        

    def update_all_tabulars(self):
        tree = ET.parse('data.xml')
        locations = tree.getroot()
        
        for location in locations:
            url = location.text
            self.remove_location_xml(url)
            self.add_location_xml(url)

    def add_location_xml(self,url):

        # Open original file
        tree = ET.parse('data.xml')
        locations = tree.getroot()
        
        #Extract fresh data
        name, period_tabular, hourly_tabular, location_coords = self.extract_fresh_data(url)
        name = name.replace(" ", "_")
        
        #add location
        new_location = ET.SubElement(locations,name)
        new_location.text = url
        new_location.attrib = location_coords

        
        #create sub-element for fresh data
        tabular1 = ET.SubElement(new_location, "period_tabular")
        tabular2 = ET.SubElement(new_location, "hourly_tabular")
        
        #append the fresh yr-data
        tabular1.append(period_tabular)
        tabular2.append(hourly_tabular)
        
        # Write back to file
        tree.write('data.xml')
    
    
    def remove_location_xml(self,url):
        tree = ET.parse('data.xml')
        locations = tree.getroot()
#        print(sites.getchildren()[0])
        for site in locations:
#            print(site.text)
            if site.text == url:
                locations.remove(site)
        tree.write('data.xml')
  
    def extract_fresh_data(self,url):
        
        name, period_tabular, location_coords = self.extract_fresh_name_and_tabular(url)
        hourly_tabular = self.extract_fresh_hourly_tabular(url)
        return name, period_tabular, hourly_tabular, location_coords
    
    
    def extract_fresh_name_and_tabular(self, url):
        response = requests.get(url + 'varsel.xml')
        with open('feed.xml', 'wb') as file:
            file.write(response.content)
        
        tree = ET.parse('feed.xml')
        data = tree.getroot()
        period_tabular = data[6][1]
        name = data[1][0].text
        location_coords = data[1][4].attrib
        
        return (name, period_tabular, location_coords)
        

    def extract_fresh_hourly_tabular(self, url):
        response = requests.get(url + 'varsel_time_for_time.xml')
        with open('feed.xml', 'wb') as file:
            file.write(response.content)
        
        tree = ET.parse('feed.xml')
        data = tree.getroot()
        hourly_tabular = data[6][1]
        return (hourly_tabular)

    def reset_XML(self):
        sites = ET.Element('sites')
        mydata = ET.tostring(sites)
        myfile = open("data.xml", "wb")
        myfile.write(mydata)
        myfile.close()
        
        url1 = "https://www.yr.no/sted/Norge/Viken/Drammen/Svelvik/"
        url2 = 'https://www.yr.no/sted/Norge/Vestfold_og_Telemark/Tinn/Heddersvatn/'
        url3 = 'https://www.yr.no/sted/Norge/Viken/Rollag/Vegglifjell_skisenter/'
        self.add_location_xml(url1)
        self.add_location_xml(url2)
        self.add_location_xml(url3)
























class MyApp(CreateXML):
    def __init__(self,root_parent):
        self.root_parent = root_parent
#        self.update_all_tabulars()
        
        self.main_level()
        
#        self.forecast_level()
        
#        self.history_level()
        
#        self.settings_level()

        
    def main_level(self):
        self.main_parent = tk.Frame(self.root_parent)
        self.main_parent.grid()
        self.main_parent.configure(width=900,height=354)
        self.main_parent.grid_propagate(True)
        
        self.button_frame = tk.Frame(self.main_parent, bd = 2, relief = "raised")
        self.button_frame.grid(row = 0, column = 0, sticky = "NSEW")
        
        yr_app_label = tk.Label(self.button_frame, text = "YrApp", font=('Comic Sans MS',18), bd = 2, relief = "ridge")
        yr_app_label.pack(side = "top")
        
        self.forecast_button()
        self.history_level_button()
#        self.settings_button()


    def destroy_current_level(self):
        try:
            self.gridParent.destroy()
        except AttributeError:
            pass
        

    def history_level_button(self):
        history_level_button = tk.Button(self.button_frame, text = "History", fg = "red", font=(14), command = self.history_level_select)
        history_level_button.pack(side = "top", ipadx = 7)
    def history_level_select(self):
        self.current_level = "history"
        self.destroy_current_level()
        self.history_level()
        
    def history_level(self):
        self.setup_history_level()
        self.history_location_buttons()
        self.setup_add_remove_location()
        
        

        
    def setup_history_level(self):
        self.gridParent = tk.Frame(self.main_parent)
        self.gridParent.grid(row = 0, column = 1)

        

    def history_location_buttons(self): # I must set up theese buttons to take names from data.xml, simple as that.
        self.locationParent = tk.Frame(self.gridParent)
        self.locationParent.grid(row=0, column = 0, rowspan = 2, sticky = "NSW")
        
        YrApp_label = tk.Label(self.locationParent, text = "Locations", font=('Italic',15))
        YrApp_label.grid(row = 0)
        
        
        tree = ET.parse('data.xml')
        locations = tree.getroot()
        
        for index, location in enumerate(locations, start = 1):
            name = (location.tag).replace("_", " ")
            self.helper_function(location, name, index)
    def helper_function(self, location, name, index):
            self.new_location = tk.Button(self.locationParent, text = name, command = lambda : self.history_location_select(location))
            self.new_location.grid(row = index, sticky = "EW", ipadx = 9)
        
    
    def history_location_select(self, location):
        try:
            self.topParent.destroy()
        except:
            pass
        
        self.location = location
        
        self.setup_extraction_button()
        
        self.topParent = tk.Frame(self.gridParent)
        self.topParent.grid(row = 0, column = 1, sticky = "NEW")
        
        refresh_image = self.resize_refresh_image("refresh.png")
        refresh_button = tk.Button(self.topParent, image = refresh_image, command = None)
        refresh_button.grid(row = 0, column = 5, sticky = "E")
        refresh_button.image = refresh_image
        
        location_name = location.tag
        print(location_name)
        tree = ET.parse('weather_history.xml')
        locations = tree.getroot()
        for location in locations:
            if location_name == location.tag:
                location #saved as the last location chosen by the user, and now being viewed, contains all data
                self.setup_calendar(location)
                
    def setup_calendar(self, location):
        self.history = location[1]
        self.calendarParent = tk.Frame(self.topParent)
        self.calendarParent.grid(row=0, column = 1, rowspan = 1, sticky = "NSWE")
        
        self.setup_year_buttons()
            
    def setup_year_buttons(self):
        for year_index, year in enumerate(self.history):
            name = year.tag[5:]
            self.year_calendar_helper_function(name, year, year_index)
    def year_calendar_helper_function(self, name, year, year_index):
        self.year_button = tk.Button(self.calendarParent, text = name, command = lambda : self.setup_month_button(year))
        self.year_button.grid(row = 0, column = year_index, sticky = "N", ipadx = 9)
    
    
    def setup_month_button(self, button_year):
        self.destroy_calendar_buttons()
        
        self.year_for_back_button = button_year
        self.back_button = tk.Button(self.calendarParent, text = "Back", command = lambda : self.setup_year_buttons())
        self.back_button.grid(row = 0, column = 0, sticky = "N", ipadx = 9)
        
        for month_index, month in enumerate(button_year, 1):
            name = month.tag[6:]
            self.month_calendar_helper_function(name, month, month_index)
    def month_calendar_helper_function(self, name, month, month_index):
        self.month_button = tk.Button(self.calendarParent, text = name, command = lambda : self.setup_day_button(month))
        self.month_button.grid(row = 0, column = month_index, sticky = "N", ipadx = 9)
        
        
    def setup_day_button(self, button_month):
        self.destroy_calendar_buttons()
        
        self.back_button = tk.Button(self.calendarParent, text = "Back", command = lambda : self.setup_month_button(self.year_for_back_button))
        self.back_button.grid(row = 0, column = 0, sticky = "N", ipadx = 9)
        
        for day_index, day in enumerate(button_month, 1):
            name = day.tag[4:]
            self.day_calendar_helper_function(name, day, day_index)
    def day_calendar_helper_function(self, name, day, day_index):
        self.day_button = tk.Button(self.calendarParent, text = name, command = lambda : self.setup_hourly_history(day))
        self.day_button.grid(row = 0, column = (day_index), sticky = "N", ipadx = 9)
        
        

    def myfunction2(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"),width=600,height=200)
    def setup_hourly_history(self, button_day):
        
        self.destroy_history_info()
   
        self.canvas=tk.Canvas(self.history_info_parent)
        self.frame=tk.Frame(self.canvas)
        myscrollbar=tk.Scrollbar(self.history_info_parent,orient="vertical",command=self.canvas.yview, relief = "sunken")
        
        self.canvas.configure(yscrollcommand=myscrollbar.set)
        myscrollbar.pack(side="right",fill="y")
        self.canvas.pack(side="left")
        self.canvas.configure(width=600,height=200)
        self.canvas.create_window((0,0),window=self.frame,anchor='n')
        self.frame.bind("<Configure>",self.myfunction2)
        
        for hour_index, hour in enumerate(button_day):

            self.create_one_hourly_history_row(hour_index, hour)
            
#            print(hour[0]), print(hour[1]), print(hour[2]), print(hour[3]), print(hour[4])
                
                

    def create_one_hourly_history_row(self, row, hour):
            
        time, windspeed, wind_direction, weather, temperature = self.extract_history(hour)
        
        weather_image = self.resize_weather_image("weather_icons/{}.png".format(weather), multiplier = 1)
        
        self.time_period = tk.Label(self.frame, text = (time), font = 12, relief = "ridge")
        self.time_period.grid(row = row, column = 1, sticky ="WE", ipadx = 10, ipady = 4)

        self.weather = tk.Label(self.frame, image = weather_image)
        self.weather.grid(row = row, column = 2, sticky ="WE")
        self.weather.image = weather_image
        
        self.wind_speed = tk.Label(self.frame, text = (windspeed + " mps  "), font = 12, relief = "ridge")
        self.wind_speed.grid(row = row, column = 3, ipadx = 10, ipady = 4, sticky = "EW")
        try:
            self.wind_direction = self.create_wind_compass(self.frame, float(wind_direction), row)
        except ValueError:
            pass
        
        self.temperature = tk.Label(self.frame, text = (temperature + "°C"), font = 12, relief = "ridge")
        self.temperature.grid(row = row, column = 5, sticky ="WE", ipadx = 15, ipady = 4)
        if temperature[0] == "-":
            self.temperature.config(fg = "blue")
        else:
            self.temperature.config(fg = "red")

    def extract_history(self, hour):
        
        time = hour.tag[5:]

        windspeed = hour[0].attrib["wind_speed"]
        
        wind_direction = hour[1].attrib["wind_direction"]
        
        cloud_cover = hour[2].attrib["cloud_cover"]
        precipitation = hour[3].attrib["precipitation"]
        
        temperature = ""
        temp = hour[4].attrib["temperature"]
        for char in temp:
            if char == ('.'):
                break
            temperature += char
            
#        weather = combination of cloud_cover and precipitaion
        weather = self.decide_weather(cloud_cover, precipitation, temperature)
        
        
        
        
        return time, windspeed, wind_direction, weather, temperature

        
        
    def decide_weather(self, cloud_cover, precipitation, temperature):
        weather = "No Value"
        try:
            for char in precipitation:
                if char == ('E'):
                    precipitation = 0
            precipitation = float(precipitation)
            cloud_cover = float(cloud_cover)
            temperature = float(temperature)
            
            if precipitation == 0 and cloud_cover == 0:
                weather = "Klarvær"
            elif precipitation == 0 and cloud_cover < 0.3:
                weather = "Lettskyet"
            elif precipitation == 0 and cloud_cover < 0.85:
                weather = "Delvis skyet"
            elif precipitation == 0 and cloud_cover >= 0.85:
                weather = "Skyet"
            elif precipitation > 0 and precipitation < 0.1 and cloud_cover >= 0.85 and temperature > 0:
                weather = "Lett regn"
            elif precipitation > 0 and precipitation < 0.1 and cloud_cover >= 0.85 and temperature < 0:
                weather = "Lett snø"
            elif precipitation > 0.1 and precipitation < 0.3 and cloud_cover >= 0.85 and temperature > 0:
                weather = "Regn"
            elif precipitation > 0.1 and precipitation < 0.3 and cloud_cover >= 0.85 and temperature < 0:
                weather = "Snø"
            elif precipitation > 0.3 and cloud_cover >= 0.85 and temperature > 0:
                weather = "Kraftig regn"
            elif precipitation > 0.3 and cloud_cover >= 0.85 and temperature < 0:
                weather = "Kraftig snø"
                     
            return weather
        except ValueError:
            return weather


        
    def destroy_calendar_buttons(self):
#        self.calendarParent.children.clear()
        self.calendarParent.destroy()
        self.calendarParent = tk.Frame(self.topParent)
        self.calendarParent.grid(row=0, column = 1, sticky = "NSWE")

    def destroy_history_info(self):
        try:
            self.history_info_parent.destroy()
        except AttributeError:
            pass
        
        self.history_info_parent = tk.Frame(self.topParent)
        self.history_info_parent.grid(column = 1, sticky = "NSWE")
        
        
        
    def setup_extraction_button(self):
        try:
            self.extract_button.destroy()
        except:
            pass
        self.extract_button = tk.Button(self.entryParent, text = "Extract weather history from {}".format(self.location.tag), font=('Comic Sans MS',12),command = self.extraction_tool)
        self.extract_button.grid(row = 0, column = 1)

    def extraction_tool(self):
        print("Extracting from: ", self.location.tag)
        
        self.tool_root = tk.Tk()
        self.tool_root.wm_title("Extraction tool")
        
        main_tool_frame = tk.Frame(self.tool_root)
        main_tool_frame.grid()
        
        between_dates_label = tk.Label(main_tool_frame, text = "           Retrieve history from every day, between theese dates")
        between_dates_label.grid(row = 1, column = 0, columnspan = 4, ipadx = 1)
        self.between_dates = tk.Checkbutton(main_tool_frame, command = self.check_box_between)
        self.between_dates.grid(row = 1, column = 0,  ipadx = 1)
        
        repeat_period_label = tk.Label(main_tool_frame, text = "      Retrieve history from the same period  this month, every year")
        repeat_period_label.grid(row = 2, column = 0, columnspan = 5, ipadx = 1)
        self.repeat_period = tk.Checkbutton(main_tool_frame, command = self.check_box_periodic)
        self.repeat_period.grid(row = 2, column = 0, ipadx = 1)
        
        from_label = tk.Label(main_tool_frame, text = "From: ", font=('Comic Sans MS',12))
        from_label.grid(row = 3, column = 1, ipadx = 1, columnspan = 1)
        from_year_label = tk.Label(main_tool_frame, text = "Year:")
        from_year_label.grid(row = 3, column = 2, ipadx = 1)
        self.from_year_entry = tk.Entry(main_tool_frame)
        self.from_year_entry.grid(row = 3, column = 3, ipadx = 2)
        self.from_year_entry.insert(3, "2019")
        from_month_label = tk.Label(main_tool_frame, text = "Month:")
        from_month_label.grid(row = 3, column = 4, ipadx = 1)
        self.from_month_entry = tk.Entry(main_tool_frame)
        self.from_month_entry.grid(row = 3, column = 5, ipadx = 2)
        self.from_month_entry.insert(3, "12")
        from_day_label = tk.Label(main_tool_frame, text = "Day:")
        from_day_label.grid(row = 3, column = 6, ipadx = 1)
        self.from_day_entry = tk.Entry(main_tool_frame)
        self.from_day_entry.grid(row = 3, column = 7, ipadx = 2)
        self.from_day_entry.insert(0, "27")
        
        
        to_label = tk.Label(main_tool_frame, text = "To: ", font=('Comic Sans MS',12))
        to_label.grid(row = 5, column = 1, ipadx = 1, columnspan = 1)
        to_year_label = tk.Label(main_tool_frame, text = "Year:")
        to_year_label.grid(row = 5, column = 2, ipadx = 1)
        self.to_year_entry = tk.Entry(main_tool_frame)
        self.to_year_entry.grid(row = 5, column = 3, ipadx = 2)
        self.to_year_entry.insert(5, "2020")
        
        self.to_month_label = tk.Label(main_tool_frame, text = "Month:")
        self.to_month_label.grid(row = 5, column = 4, ipadx = 1)
        self.to_month_entry = tk.Entry(main_tool_frame)
        self.to_month_entry.grid(row = 5, column = 5, ipadx = 2)
        self.to_month_entry.insert(5, "01")
        
        to_day_label = tk.Label(main_tool_frame, text = "Day:")
        to_day_label.grid(row = 5, column = 6, ipadx = 1)
        self.to_day_entry = tk.Entry(main_tool_frame)
        self.to_day_entry.grid(row = 5, column = 7, ipadx = 2)
        self.to_day_entry.insert(0, "03")
        
        
        between_label = tk.Label(main_tool_frame, text = "Between:", font=('Comic Sans MS',12))
        between_label.grid(row = 7, column = 1, ipadx = 1, columnspan = 1)
        
        from_hour_label = tk.Label(main_tool_frame, text = "From hour:")
        from_hour_label.grid(row = 7, column = 2, ipadx = 1)
        self.from_hour_entry = tk.Entry(main_tool_frame)
        self.from_hour_entry.grid(row = 7, column = 3, ipadx = 2)
        self.from_hour_entry.insert(0, "12")
        
        to_hour_label = tk.Label(main_tool_frame, text = "To hour:")
        to_hour_label.grid(row = 7, column = 4, ipadx = 1)
        self.to_hour_entry = tk.Entry(main_tool_frame)
        self.to_hour_entry.grid(row = 7, column = 5, ipadx = 2)
        self.to_hour_entry.insert(0, "15")
        
        self.order_history_button = tk.Button(main_tool_frame, text = "Order weather history", font=('Comic Sans MS',12),  command = self.verify_request)
        self.order_history_button.grid(row = 9, column = 3, columnspan = 3)
        self.clear_all_button = tk.Button(main_tool_frame, text = "Clear all", font=('Comic Sans MS',12),  command = self.clear_all)
        self.clear_all_button.grid(row = 9, column = 5, columnspan = 3)

        self.error_display = tk.Label(main_tool_frame, text = "")
        self.error_display.grid(row = 8, column = 2, columnspan = 6)
        
        self.tool_root.mainloop()
        
        
    def check_box_periodic(self):
        self.check_periodic = True
        self.between_dates.deselect()
        self.check_between = False
        
    def check_box_between(self):
        self.check_between = True 
        self.repeat_period.deselect()
        self.check_periodic = False
        
        
        
        
        
        
    def clear_all(self):
        self.from_year_entry.delete(0, tk.END)
        self.from_month_entry.delete(0, tk.END)
        self.from_day_entry.delete(0, tk.END)
        self.from_hour_entry.delete(0, tk.END)  
        self.to_year_entry.delete(0, tk.END)
        self.to_month_entry.delete(0, tk.END)
        self.to_day_entry.delete(0, tk.END)
        self.to_hour_entry.delete(0, tk.END)   



    def verify_request(self):
        print("Order weather history from: ", self.location.tag)
        
        self.display_error("")

        from_year = self.from_year_entry.get()
        from_month = self.from_month_entry.get()
        from_day = self.from_day_entry.get()
        from_hour = self.from_hour_entry.get()
        to_year = self.to_year_entry.get()
        to_month = self.to_month_entry.get()
        to_day = self.to_day_entry.get()
        to_hour = self.to_hour_entry.get()

        entry_info = from_year, from_month, from_day, from_hour, to_year, to_month, to_day, to_hour
        entry_labels = ("from","year", "from","month", "from","day", "from","hour", "to","year", "to","month", "to","day", "to","hour")
        
        
        converted_info = self.process_entries(entry_info, entry_labels)
        
        if converted_info == None:
            return
        else:
            self.order_history(*converted_info)
            
    def order_history(self, from_year, from_month, from_day, from_hour, to_year, to_month, to_day, to_hour):
        #Setting up a few local variables:
        previus_year = ""
        previus_month = ""
        location = self.location.tag
        latitude = self.location.get('latitude')
        longitude = self.location.get('longitude')
        place = latitude, longitude, location
        delta = datetime.timedelta(days=1)
        
        print(type(from_year))
        print(from_year)
        
        start_hour = from_hour # 0-24
        end_hour = to_hour # 0-24
        
        if self.check_periodic == True: # Let's extract weather history between theese dates, for every year from first to last.
            
            
            year = from_year
            month = from_month
            while int(year) <= int(to_year): # Goes through all years requested, one at a time.
                all_dates = []
                
                
                start_date = datetime.date(int(year), int(month), int(from_day)) #Setter start datoen (yyyy, mm, dd)
                end_date = datetime.date(int(year), int(month), int(to_day)) #Setter end datoen (yyyy, mm, dd)
                date = start_date
                
                while date <= end_date:
                    all_dates.append(date) # Lager en liste med alle datoer i tidsrommet som ble etterspurt
                    date += delta # += 1 dag
                for date in all_dates: #I believe this will release the program in between runs, thereby releasing memory? nope ## Går igjennom lista
                    date_str = date.__str__() # Bare for å skrive ut navnet på stedet som er requesta historie fra
                    print("Extracting weather history from: ", date_str)
                    
                    WeatherHistory.Write_history(place, date, start_hour, end_hour, previus_year, previus_month)
                    year = date_str[:4]
                    month = date_str[5:7]
                    previus_year = year
                    previus_month = month
                
                
                year = int(year) + 1
                

            
            
            

        

        
        


        

        

            
        if self.check_between == True:
            start_date = datetime.date(from_year, from_month, from_day) #Setter start datoen (yyyy, mm, dd)
            end_date = datetime.date(to_year, to_month, to_day) #Setter end datoen (yyyy, mm, dd)

            
            date = start_date
            all_dates = []
            while date <= end_date:
                all_dates.append(date) # Lager en liste med alle datoer i tidsrommet som ble etterspurt
                date += delta # += 1 dag
            for date in all_dates: #I believe this will release the program in between runs, thereby releasing memory? nope ## Går igjennom lista
                date_str = date.__str__() # Bare for å skrive ut navnet på stedet som er requesta historie fra
                print("Extracting weather history from: ", date_str)
                WeatherHistory.Write_history(place, date, start_hour, end_hour, previus_year, previus_month)
                year = date_str[:4]
                month = date_str[5:7]
                previus_year = year
                previus_month = month

                

            
        
        


    def process_entries(self, entry_info, entry_labels):
        today = datetime.date.today()
        today = today.strftime("%m/%d/%Y")

        this_month = int(today[:2])
        this_day = int(today[3:5])
        this_year = int(today[6:10])
        
#        print(this_year, this_month, this_day)
        
        converted_info = []
        for info_index, info in enumerate(entry_info):
            from_to = entry_labels[info_index*2]
            time = entry_labels[info_index*2+1]
            
            value = self.convert_value(info, from_to, time, today)

            if type(value) == int:
                converted_info.append(value)
            else:
                self.display_error(value)
                break # Here the for loop ends if some value given is not a number.
#            print(time, type(value), value)
            
            if time == ("year"):
                if value <= 2012:
                    value = ("The {} you requested weather history {}, is too far back: \"{}\". First ever archieved data is 2013/09/01 kl: 00:00".format(time, from_to, value))
                    self.display_error(value)
                    break
                elif value > this_year:
                    value = ("The {} you requested weather history {}, is in the future: \"{}\". This is {}...".format(time, from_to, value, this_year))
                    self.display_error(value)
                    break
            elif time == ("month"):
                if value > 12 or value == 0:
                    value = ("The {} you requested weather history {}, does not exist: \"{}\". A year has 12 months.".format(time, from_to, value))
                    self.display_error(value)
                    break
                elif value < 0:
                    value = ("The {} you requested weather history {}, does not exist: \"{}\". The chosen month can not be negative.".format(time, from_to, value))
                    self.display_error(value)
                    break
            elif time == ("day"):
                if value > 31:
                    value = ("The {} you requested weather history {}, does not exist: \"{}\". A month has at most 31 days.".format(time, from_to, value))
                    self.display_error(value)
                    break
                elif value <= 0:
                    value = ("The {} you requested weather history {}, does not exist: \"{}\". Bad days exist, but no days are truely negative.".format(time, from_to, value))
                    self.display_error(value)
                    break
            elif time == ("hour"):
                if value > 24:
                    value = ("The {} you requested weather history {}, does not exist: \"{}\". A day has at most 24 days.".format(time, from_to, value))
                    self.display_error(value)
                    break
                elif value <= 0:
                    value = ("The {} you requested weather history {}, does not exist: \"{}\". Value negative.".format(time, from_to, value))
                    self.display_error(value)
                    break
        if len(converted_info) != 8:
            return None

        from_year, from_month, from_day, from_hour, to_year, to_month, to_day, to_hour = converted_info
        
        print(from_year, from_month, from_day, from_hour, to_year, to_month, to_day, to_hour)
        
        if to_year == this_year:
            if to_month == this_month:
                if to_day >= this_day:
                    value = ("The {} you requested weather history {} is in the future: \"{}\". Do you know what \"history\" means?".format("day", "to", to_day))
                    self.display_error(value)
        
        if from_year > to_year:
            value = ("The year you requested weather history from, is before the year you ordered the history to..")
            self.display_error(value)
            return None
        if from_year == to_year:
            if from_month > to_month:
                value = ("The month you requested weather history from, is before the month you ordered the history to..")
                self.display_error(value)
                return None
            if from_month == to_month:
                if from_day > to_day:
                    value = ("The day you requested weather history from, is before the day you ordered the history to..")
                    self.display_error(value)
                    return None
        if from_hour >= to_hour:
            value = ("Error. The hour you order to must be ahead of the hour ordered from.")
            self.display_error(value)
            return None

        return converted_info # YEYYY, Your request has been passed on.
    
    def display_error(self, info):
        self.error_display.configure(text = info)
            
    def convert_value(self, value, from_to, time, today):
        try:
            num_value = int(value)
        except ValueError:
            return ("The {} you requested weather history {} has an invalid value: {}. You can only use numbers".format(time, from_to, value))

        return num_value













    def forecast_button(self):
        forecast_button = tk.Button(self.button_frame, text = "Forecast", fg = "red", font=(14), command = self.forecast_select)
        forecast_button.pack(side = "top")
    def forecast_select(self):
        self.destroy_current_level()
        self.current_level = "forecast"
        self.tabular_type = "periodic"
        self.forecast_level()
        
    def forecast_level(self):

        self.day_choice = 0
        self.setup_forecast_level()
        self.forecast_location_buttons() # Setting up a name button for all locations added to the App.
        self.setup_add_remove_location()
        self.setup_info_labels()
        
    def setup_forecast_level(self):
        self.gridParent = tk.Frame(self.main_parent)
        self.gridParent.grid(row = 0, column = 1)
        
        self.topParent = tk.Frame(self.gridParent)
        self.topParent.grid(row = 0, column = 1, sticky = "NEW")
        
        self.day_label = tk.Label(self.topParent, text = "", font=('Comic Sans MS',12))
        self.day_label.grid(row = 0, column = 1, sticky = "E")
        
        self.name_label = tk.Label(self.topParent, text = "", font=('Comic Sans MS',12))
        self.name_label.grid(row = 1, column = 2)
        
        self.from_date_label = tk.Label(self.topParent, text = "", font=('Comic Sans MS',12))
        self.from_date_label.grid(row = 0, column = 3)
        
        
        yesterday_button = tk.Button(self.topParent, text = "Last day", font=(14), command = self.yesterday)
        yesterday_button.grid(row = 0, column = 0, sticky = "W")

        tomorrow_button = tk.Button(self.topParent, text = "Next day", font=(14), command = self.tomorrow)
        tomorrow_button.grid(row = 0, column = 4, sticky = "E")
        
        refresh_image = self.resize_refresh_image("refresh.png")
        refresh_button = tk.Button(self.topParent, image = refresh_image, command = self.refresh)
        refresh_button.grid(row = 0, column = 5, sticky = "E")
        refresh_button.image = refresh_image

        self.switch_tabular_button = tk.Button(self.topParent, text = "Show hourly forecast", font = 12, command = self.switch_tabular)
        self.switch_tabular_button.grid(row = 0, column = 2)

        self.topParent.grid_columnconfigure(0, weight=100)
        self.topParent.grid_columnconfigure(1, minsize=100, weight=1)
        self.topParent.grid_columnconfigure(2, minsize=200, weight=1)
        self.topParent.grid_columnconfigure(3, minsize=120, weight=1)

                
        
    def forecast_location_buttons(self):
        self.locationParent = tk.Frame(self.gridParent)
        self.locationParent.grid(row=0, column = 0, rowspan = 2, sticky = "NSW")
        
        YrApp_label = tk.Label(self.locationParent, text = "Locations", font=('Italic',15))
        YrApp_label.grid(row = 0)
        
        
        tree = ET.parse('data.xml')
        locations = tree.getroot()
        
        for index, location in enumerate(locations, start = 1):
            name = (location.tag).replace("_", " ")
            self.setup_location_buttons_helper_function(location, name, index)
    def setup_location_buttons_helper_function(self, location, name, index):
            self.new_location = tk.Button(self.locationParent, text = name, command = lambda : self.show_location_forecast(location))
            self.new_location.grid(row = index, sticky = "EW", ipadx = 9)
#            print("row: ", index)
    
    
    
    def setup_add_remove_location(self):
        
        self.entryParent = tk.Frame(self.gridParent)
        self.entryParent.grid(row=2, column = 0, columnspan = 2, sticky = "EW")
        
        
        
        remove_location_button = tk.Button(self.entryParent, text = "Remove location", fg = "red",font = 12, command = self.remove_location_button)
        remove_location_button.grid(row = 0, column = 0)
                
        add_location_label = tk.Label(self.entryParent, text = "Add location url:", font=('Comic Sans MS',12))
        add_location_label.grid(row = 1, column = 0)
    
        self.add_location_entry = tk.Entry(self.entryParent)
        self.add_location_entry.grid(row = 1, column = 1, ipadx = 227)
        
        add_button = tk.Button(self.entryParent, text = "Add", font=(14), command = self.add_location_button)
        add_button.grid(row = 1, column = 2, sticky = "E")
        
    
###################################################__Setup info labels below__#########################################################   
        
    def setup_info_labels(self):
        self.destroy_info_labels()
        try:
            if self.tabular_type == "periodic":
                self.setup_periodic_info_labels()
            
            elif self.tabular_type == "hourly":
                self.setup_hourly_info_labels()
            self.update_name_date()
        except AttributeError:
            print("self.location does not yet exist. Select a location.")
         
    def setup_periodic_info_labels(self):
        
        self.infoParent = tk.Frame(self.gridParent)
        self.infoParent.grid(row=1, column = 1, rowspan = 1, columnspan = 1, sticky = "WE")
        self.infoParent.configure(width=500,height=204)
        self.infoParent.grid_propagate(False)
        
        if self.day_choice == 0:
            period = int(self.location[0][0][0].get("period"))
            first_period = period
        else:
            period = 0
        
        first_period = int(self.location[0][0][0].get("period"))
        row = 2
        for this_period in range(4-period):
            if self.day_choice != 0:
                x= this_period + (4 - first_period + (4*(self.day_choice-1)))
#                print("x = ",this_period, " + 4 - ", first_period, " + 4 * (", self.day_choice, "-1) = ", x)
            else:
                x = this_period
            self.create_one_periodic_info_row(row, x) 
            row += 1
        
    def create_one_periodic_info_row(self, row, x):
        from_date, to_date, from_time, to_time, weather,temperature,wind_direction,mps,deg_360 = self.extract_info(self.location[0][0][x])
        weather_image = self.resize_weather_image("weather_icons/{}.png".format(weather), multiplier = 1)
        
        space = tk.Label(self.infoParent)
        space.grid(row = row, column = 0, sticky ="WE", ipadx = 15, ipady = 4)
        
        self.time_period = tk.Label(self.infoParent, text = (from_time + " -"+ to_time), font = ("Italic",16), relief = "ridge")
        self.time_period.grid(row = row, column = 1, sticky ="WE", ipadx = 10, ipady = 4, pady = 6, padx = 10)

        self.weather = tk.Label(self.infoParent, image = weather_image)
        self.weather.grid(row = row, column = 2, sticky ="WE")
        self.weather.image = weather_image

        self.wind_speed = tk.Label(self.infoParent, text = (mps + " mps  "), font = ("Italic",16), relief = "ridge")
        self.wind_speed.grid(row = row, column = 3, ipadx = 10, ipady = 4, sticky = "EW", pady = 6, padx = 10)

        self.wind_direction = self.create_wind_compass(self.infoParent, float(deg_360), row)

        self.temperature = tk.Label(self.infoParent, text = (temperature + "°C"), font = ("Italic",16), relief = "ridge")
        self.temperature.grid(row = row, column = 5, sticky ="WE", ipadx = 15, ipady = 4, pady = 6, padx = 10)
        if temperature[0] == "-":
            self.temperature.config(fg = "blue")
        else:
            self.temperature.config(fg = "red")
                        
        

    
    def myfunction1(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"),width=600,height=200)
    def setup_hourly_info_labels(self):
        
        self.infoParent = tk.Frame(self.gridParent)
        self.infoParent.grid(row=1, column = 1, rowspan = 1, columnspan = 1, sticky = "WE")
   
        self.canvas=tk.Canvas(self.infoParent)
        self.frame=tk.Frame(self.canvas)
        myscrollbar=tk.Scrollbar(self.infoParent,orient="vertical",command=self.canvas.yview, relief = "sunken")
        
        self.canvas.configure(yscrollcommand=myscrollbar.set)
        myscrollbar.pack(side="right",fill="y")
        self.canvas.pack(side="left")
        self.canvas.configure(width=600,height=200)
        self.canvas.create_window((0,0),window=self.frame,anchor='n')
        self.frame.bind("<Configure>",self.myfunction1)
        
        if len(self.location) > 1:
            day_count = 0
            for row, hour in enumerate(self.location[1][0]):
                from_time = hour.get('from')[11:16]
                
                if from_time == '00:00':
                    day_count += 1
                    
                if self.day_choice == 0 and day_count == 0:
                    self.create_one_hourly_info_row(row,hour)
                    if day_count == 1:
                        break
                    
                if self.day_choice == 1 and day_count == 1:
                    self.create_one_hourly_info_row(row,hour)
                    if day_count == 2:
                        break
                    
                if self.day_choice == 2 and day_count == 2:
                    self.create_one_hourly_info_row(row,hour)
                    if day_count == 3:
                        break
     

    def create_one_hourly_info_row(self, row, hour):
            
        from_date, to_date, from_time, to_time, weather,temperature,wind_direction,mps,deg_360 = self.extract_info(hour)
        weather_image = self.resize_weather_image("weather_icons/{}.png".format(weather), multiplier = 1)
        
        self.time_period = tk.Label(self.frame, text = (from_time), font = 12, relief = "ridge")
        self.time_period.grid(row = row, column = 1, sticky ="WE", ipadx = 10, ipady = 4)

        self.weather = tk.Label(self.frame, image = weather_image)
        self.weather.grid(row = row, column = 2, sticky ="WE")
        self.weather.image = weather_image
        
        self.wind_speed = tk.Label(self.frame, text = (mps + " mps  "), font = 12, relief = "ridge")
        self.wind_speed.grid(row = row, column = 3, ipadx = 10, ipady = 4, sticky = "EW")

        self.wind_direction = self.create_wind_compass(self.frame, float(deg_360), row)
        
        self.temperature = tk.Label(self.frame, text = (temperature + "°C"), font = 12, relief = "ridge")
        self.temperature.grid(row = row, column = 5, sticky ="WE", ipadx = 15, ipady = 4)
        if temperature[0] == "-":
            self.temperature.config(fg = "blue")
        else:
            self.temperature.config(fg = "red")


    def create_wind_compass(self, parent, deg_360, row):
        def arrow1(deg_360, rad):
            deg = deg_360 + 150
            degree = (deg / 180) * math.pi
            
            x=rad * math.cos(degree)
            y= rad * math.sin(degree)
            return (x, y)
        
        def arrow2(deg_360, rad):
            deg = deg_360 - 150
            degree = (deg / 180) * math.pi
            
            x=rad * math.cos(degree)
            y= rad * math.sin(degree)
            return (x, y)
        
        wind_compass = tk.Canvas(parent, width=24, height=24, borderwidth=0, highlightthickness=0)
        wind_compass.grid(row = row, column = 4)
        
        center = 12
        rad = 11
        deg_360 = deg_360 - 90
        degree = (deg_360 / 180) * math.pi
        x=rad * math.cos(degree)
        y= rad * math.sin(-degree)
        arrow_point = (center-x), (center+y)
        x1, y1 = arrow1(deg_360, rad)
        x2, y2 = arrow2(deg_360, rad)
        
        wind_compass.create_line((center, center), (center+x, center-y), fill="black", width=1.5)
        wind_compass.create_line((center, center), (center-x, center+y), fill="black", width=1.5)
        wind_compass.create_line(arrow_point, (arrow_point[0] - x1), (arrow_point[1] - y1),fill="black", width=1.5)
        wind_compass.create_line(arrow_point, ((arrow_point[0] - x2), (arrow_point[1] - y2)),fill="black", width=1.5)
        return wind_compass




    def yesterday(self):
        if self.day_choice >= 1:
            self.day_choice -= 1
            self.setup_info_labels()
        
    def tomorrow(self):        
        if self.day_choice < 8:
            if self.tabular_type == "hourly" and self.day_choice > 1:
                return
            self.day_choice += 1
            
            self.setup_info_labels()
        
        
    def show_location_forecast(self,location):
        location_name = location.tag
        tree = ET.parse('data.xml')
        locations = tree.getroot()
        for location in locations:
            if location_name == location.tag:
                self.location = location #saved as the last location chosen by the user, and now being viewed
                self.setup_info_labels()
                

        

    def update_name_date(self):
        period = (4 * self.day_choice)
        from_date, to_date, from_time, to_time, weather,temp,windDir,mps,windDeg = self.extract_info(self.location[0][0][period])
        name = (self.location.tag).replace("_", " ")
        
        day, month, year = (int(x) for x in from_date.split('/'))  
        ans = datetime.date(year, month, day)
        weekday = ans.strftime("%A")
        

        self.name_label.configure(text = name)
        self.day_label.configure(text = weekday)
        self.from_date_label.configure(text = from_date)
        
    def extract_info(self, hour):
        
        from1 = hour.get('from')
        to1 = hour.get('to')
        weather = hour[0].get("name")
        temp = hour[4].get("value")
        windDir = hour[2].get("name")
        mps = hour[3].get("mps")
        windDeg = hour[2].get ("deg")
        
        from_time =  " kl." + from1[11:16]
        to_time =  " kl." + to1[11:16]
        from_date =from1[8:10] + "/" + from1[5:7] + "/" + from1[0:4]
        to_date = "to " + to1[8:10] + "/" + to1[5:7]

        return (from_date, to_date, from_time, to_time, weather,temp,windDir,mps,windDeg)


    def switch_tabular(self):
        if self.tabular_type == "periodic":
            self.tabular_type = "hourly"
            self.switch_tabular_button.configure(text = "Show periodic forecast")
            if self.day_choice > 2:
                self.day_choice = 0
                
        elif self.tabular_type == "hourly":
            self.tabular_type = "periodic"
            self.switch_tabular_button.configure(text = "Show hourly forecast")
            
        self.setup_info_labels()


    def refresh(self):
        self.update_all_tabulars()
        self.show_location_forecast(self.location)


    def add_location_button(self):
        print (self.add_location_entry.get())
        entry = self.add_location_entry.get()
        
        try:
            self.add_location_xml(entry)
            self.locationParent.destroy()
            if self.current_level == ("forecast"):
                self.forecast_location_buttons()
            elif self.current_level == ("history"):
                self.history_location_buttons()
            self.add_location_entry.delete(0, tk.END)
        except:
            self.add_location_entry.delete(0, tk.END)
            self.add_location_entry.insert(0, "Error: try this format: https://www.yr.no/sted/xyz/abc/")

            
    def remove_location_button(self):
        print(self.location)
        try:
            entry = self.location.text
            
            self.remove_location_xml(entry)
            self.locationParent.destroy()
            if self.current_level == ("forecast"):
                self.forecast_location_buttons()
            elif self.current_level == ("history"):
                self.history_location_buttons()
            
        except AttributeError:
            print("You gotta select a location first you dofus")



    def resize_weather_image(self, img_name, multiplier):
        image = Image.open(img_name)
        [image_width, image_height] = image.size
        
        new_image_width,new_image_height = int(image_width*multiplier),int(image_height*multiplier)
        image = image.resize((new_image_width, new_image_height), Image.ANTIALIAS)
        resized_image = ImageTk.PhotoImage(image)
        return resized_image



    def resize_refresh_image(self, img_name):
        image = Image.open(img_name)
        [image_width, image_height] = image.size
        
        new_image_width,new_image_height = int(image_width*0.1),int(image_height*0.1)
        image = image.resize((new_image_width, new_image_height), Image.ANTIALIAS)
        resized_image = ImageTk.PhotoImage(image)
        return resized_image
    
    
    def destroy_info_labels(self):
        try:
            self.infoParent.destroy()
        except AttributeError:
            pass











CreateXML()
root = tk.Tk()
myapp = MyApp(root)
root.wm_title("YrApp")
root.mainloop()

