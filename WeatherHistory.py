from six.moves.urllib import request
import xml.etree.ElementTree as ET
import requests
import datetime
import math
import gc

#_______________________________________________________________________________________________________________ *GARBAGE:*
#        place = ["59.685779", "10.347233", "Homeeeee"]
#        place = ["59.85421", "8.649169", "Gaustatoppen"]
#        place = ["59.834679", "8.726349", "Heddersvatn"]
#        place = ["60.080973", "8.984208", "Vegglifjell_skisenter"] 
#        place = ["59.611635", "10.410745", "Svelvik"] 
#        place = ["60.543469", "7.441195", "Hardangergjokulen"] 
#        place = ["59.819257", "8.713073", "Gaustakne"] 
#        place = ["63.178814", "12.323869", "Storulvan"] 
#        place = ["63.008669", "12.192641", "Sylan"] 
        
        
#        start_date = datetime.date(2019, 12, 25)
#        end_date = datetime.date(2020, 1, 3)
#        
#        start_date = datetime.date(2013, 9, 1)
#        end_date = datetime.date(2020, 4, 20)
#        start_hour = 12 # 0-24
#        end_hour =15 # 0-24
#_______________________________________________________________________________________________________________ *END*

#Ensemble members from and counting /2016/11/08/kl:0200 to 2018 and the archieve_switch_date
#No ensemble members has been observed before this date.
#X/Y wind is allways the case in archieve 2.
# First ever archieved data is 2013/09/01 kl: 00:00

# no wind data before 2018/09/18 # Except there is, in the other Rerun archieve in x-y format.

# x_wind, y_wind from 2018/09/18 to 2019/07/01
# wind_direction and speed from 2019/07/02 to present
#        archieve_switch_date = datetime.date(2018, 9, 18)


class Write_history():
    def __init__(self, place, date, start_hour, end_hour, previus_year, previus_month):
        
#        self.setup_XML() #Resets the XML file
        exists = self.verify_existence(place)
        
        if exists == 0: # The location is not previusly added to the XML file
            self.write_key_info(place)
            exists = 1
        if exists == 1:
            name = place[2]
            
            self.write_history(name, date, start_hour, end_hour, previus_year, previus_month)



    
    def verify_existence(self, place):
        exists = 0
        name = place[2]
        
        try:
            tree = ET.parse('weather_history.xml')
            sites = tree.getroot()
            for location in sites:
                if location.tag == name:
                    exists = 1 # It is exists if the location name is in the xml file
            return exists    
        except FileNotFoundError:
            self.setup_XML()



    def write_key_info(self, place):
        lat_coord = place[0]
        long_coord = place[1]
        name = place[2]
        
        
        time = ['2020', '03', '26', '12'] #Just an unimportant time needed to access the information i need.

        
        url = self.url_format_time(time, 1)
        
        index_coords, loc_keys = self.fetch_index_keys(url, lat_coord, long_coord)
        coord_offset = self.calculate_offset(index_coords, place)
        
#        index_coords = (796, 564, '60.08807431255639', '8.985304572445223')
#        loc_keys = ('-308322.0', '-333442.19999999995')


        indexes = [index_coords[0], index_coords[1]]
        altitude = self.get_altitude(indexes, list(loc_keys), url)
        
        tree = ET.parse('weather_history.xml')
        sites = tree.getroot()
        
        location = ET.SubElement(sites, name) # Creating the child-element of sites, to contain all info about this location.
        location.text = ("altitude_found = "+ str(altitude))
        
        info = ET.SubElement(location, "info")
        
        indexes = ET.SubElement(info, "indexes")
        indexes.attrib = {"x_index" : str(index_coords[0]), "y_index" : str(index_coords[1])}
        
        keys = ET.SubElement(info, "keys")
        keys.attrib = {"x_key" : loc_keys[0], "y_key" : loc_keys[1]}
        
        requested = ET.SubElement(info, "reqested_coords")
        requested.attrib = {"latitude" : lat_coord, "longitude" : long_coord}
        
        found = ET.SubElement(info, "found_coords")
        found.attrib = {"latitude" : index_coords[2], "longitude" : index_coords[3]}
        
        offset = ET.SubElement(info, "offset")
        offset.attrib = {"distance_m" : str(coord_offset[0]), "direction_deg" : str(coord_offset[1]), "symbol" : coord_offset[2]}
        
        history_folder = ET.SubElement(location, "History")
        history_folder.attrib = {}
        
        tree.write('weather_history.xml')

        
    def write_history(self, name, date, start_hour, end_hour, previus_year, previus_month):
        

        date_str = date.__str__()

        year = date_str[:4]
        month = date_str[5:7]
        day = date_str[8:10]
        print(year, month, day)
    
        tree = ET.parse('weather_history.xml')
        sites = tree.getroot()
    
        for location in sites:
            if location.tag == name:
                
                info_elem = location[0]
                x_key = info_elem.find('keys').attrib['x_key']
                y_key = info_elem.find('keys').attrib['y_key']
                x_index = info_elem.find('indexes').attrib['x_index']
                y_index = info_elem.find('indexes').attrib['y_index']
                
                keys = [x_key, y_key]
                indexes = [x_index, y_index]
                
                history_folder = location[1]
                
                year_exists = 0
                month_exists = 0
                day_exists = 0
                
                
                print(location.tag, location[0].tag, location[1].tag)
                if len(history_folder) > 0:
                    for xml_year in history_folder:
#                        print("In the year for loop", xml_year.tag)
#                        print(xml_year.tag[5:])
                        if year == xml_year.tag[5:]: #For the right year
                            for xml_month in xml_year: #For the existing months
                                if int(month) == int(xml_month.tag[6:]): # find the right month
                                    
                                    for xml_day in xml_month: # for every day in the right month
                                        if int(day) == int(xml_day.tag[4:]): #if the day allready exists in the history file
                                            day_exists = 1 # Yes it exists
                                            insert_index = 0 # reset the index for inserting hours of info into the existing day
                                            for hour in range(start_hour, end_hour, 1): #for every requested hour
                                                hour_exists = 0 # HOUR EXISTS NOT  #pretend it's not in the xml
                                                for xml_hour in xml_day:  # Go through the xml for every hour
                                                    if hour == int(xml_hour.tag[5:]): # if it exists:
                                                        hour_exists = 1 # HOUR EXISTS INDEED # enough said
                                                        
                                                if hour_exists == 0: # And if it does not
                                                    print(hour)
                                                    first_xml_hour = (xml_day[0].tag)[5:]
                                                    last_xml_hour_int = int(first_xml_hour)-1
                                                    for hour_index, xml_hour_int in enumerate(xml_day): # For every hour in the xml
                                                        xml_hour_int = int(xml_hour_int.tag[5:]) # you shall be inted!
                                                        if (xml_hour_int -1) != (last_xml_hour_int): #6, 7, 9, 10, trying to find the hole here... AHA! xml_hour_int is now 9 and last_xml_hour_int is 7.
                                                            if int(hour) > last_xml_hour_int and int(hour) < xml_hour_int: # And what if there is a hole, but this hour belongs not in it..?
                                                                insert_index = hour_index
                                                                self.insert_hourly_info(year, month, day, hour, date, indexes, keys, xml_day, insert_index)
                                                                hour_exists = 1
                                                        last_xml_hour_int = xml_hour_int

                                                    if hour > int(xml_hour.tag[5:]) and hour_exists == 0: # Then the hour may be before the existing ones
                                                        print("HOUR EXISTS NOT: After")
                                                        self.write_hourly_info(year, month, day, hour, date, indexes, keys, xml_day)
                                                    elif hour < int(xml_hour.tag[5:]) and hour_exists == 0: # or it may be the hours after the existing info.
                                                        print("HOUR EXISTS NOT: Before")
                                                        self.insert_hourly_info(year, month, day, hour, date, indexes, keys, xml_day, insert_index)
                                                        insert_index += 1

                                    if day_exists == 0: # If days do exists, but not the day for which the request is made:
                                        first_xml_day = (xml_month[0].tag)[4:]
                                        last_xml_day_int = int(first_xml_day)-1
                                        for day_index, xml_day_int in enumerate(xml_month):
                                            xml_day_int = int(xml_day_int.tag[4:])
                                            if (xml_day_int -1) != (last_xml_day_int): #6, 7, 9, 10, trying to fill in 8 here..
                                                if int(day) > last_xml_day_int and int(day) < xml_day_int: # And what if there is a hole, but this day belongs not in it..?
                                                    day_folder = ET.Element('day_' + day)
                                                    for hour in range(start_hour, end_hour, 1): 
                                                        self.write_hourly_info(year, month, day, hour, date, indexes, keys, day_folder)
                                                    xml_month.insert(day_index, day_folder)
                                                    day_exists = 1
                                            last_xml_day_int = xml_day_int
                                            
                                        if int(day) < int(first_xml_day) and day_exists == 0:
                                            day_folder = ET.Element('day_' + day) 
                                            for hour in range(start_hour, end_hour, 1): 
                                                self.write_hourly_info(year, month, day, hour, date, indexes, keys, day_folder)
                                            xml_month.insert(0, day_folder)
                                        elif day_exists == 0 and int(day) > int(xml_day.tag[4:]): # Same as xml_month below, left iteration, last day in history year.
                                            day_folder = ET.SubElement(xml_month, 'day_' + day) 
                                            for hour in range(start_hour, end_hour, 1):
                                                self.write_hourly_info(year, month, day, hour, date, indexes, keys, day_folder)          
                                    month_exists = 1

                            if month_exists == 0: # If months do exists, but not the month for which the request is made:
                                print(xml_year.tag, xml_month.tag)
                                first_xml_month = (xml_year[0].tag)[6:]
                                last_xml_month_int = int(first_xml_month)-1
                                for month_index, xml_month_int in enumerate(xml_year):
                                    xml_month_int = int(xml_month_int.tag[6:])
                                    
                                    if (xml_month_int -1) != (last_xml_month_int): #6, 7, 9, 10, trying to fill in 8 here..
                                        if int(month) > last_xml_month_int and int(month) < xml_month_int: # And what if there is a hole, but this month belongs not in it..?
                                            month_folder = ET.Element('month_' + month)
                                            day_folder = ET.SubElement(month_folder, 'day_' + day)
                                            for hour in range(start_hour, end_hour, 1): 
                                                self.write_hourly_info(year, month, day, hour, date, indexes, keys, day_folder)
                                            xml_year.insert(month_index, month_folder)
                                            month_exists = 1
                                    last_xml_month_int = xml_month_int
                                
                                if int(month) < int(first_xml_month) and month_exists == 0:
                                    month_folder = ET.Element('month_' + month)
                                    day_folder = ET.SubElement(month_folder, 'day_' + day) 
                                    for hour in range(start_hour, end_hour, 1): 
                                        self.write_hourly_info(year, month, day, hour, date, indexes, keys, day_folder)
                                    xml_year.insert(0, month_folder)
                                elif month_exists == 0 and int(month) > int(xml_month.tag[6:]): # Same as xml_year below, left iteration, last month in history year.
                                    month_folder = ET.SubElement(xml_year, 'month_' + month)
                                    day_folder = ET.SubElement(month_folder, 'day_' + day) 
                                    for hour in range(start_hour, end_hour, 1):
                                        self.write_hourly_info(year, month, day, hour, date, indexes, keys, day_folder)
                            year_exists = 1
                            
                    if year_exists == 0: # If years do exists, but not the year for which the request is made:
                        
                        first_xml_year = (history_folder[0].tag)[5:]
                        last_xml_year_int = int(first_xml_year)-1
                        for year_index, xml_year_int in enumerate(history_folder):
                            xml_year_int = int(xml_year_int.tag[5:])
                            
                            if (xml_year_int -1) != (last_xml_year_int): #2014, 2015, 2017, 2018, trying to fill in 2016 here..
                                if int(year) > last_xml_year_int and int(year) < xml_year_int: # And what if there is a hole, but this year belongs not in it..?
                                    year_folder = ET.Element("year_" + year)
                                    month_folder = ET.SubElement(year_folder, 'month_' + month)
                                    day_folder = ET.SubElement(month_folder, 'day_' + day) 
                                    for hour in range(start_hour, end_hour, 1): 
                                        self.write_hourly_info(year, month, day, hour, date, indexes, keys, day_folder)
                                    history_folder.insert(year_index, year_folder)
                                    year_exists = 1
                                    break
                            last_xml_year_int = xml_year_int
                        
                        if int(year) < int(first_xml_year) and year_exists == 0:
                            year_folder = ET.Element("year_" + year)
                            month_folder = ET.SubElement(year_folder, 'month_' + month)
                            day_folder = ET.SubElement(month_folder, 'day_' + day) # The day changes every time.
                            for hour in range(start_hour, end_hour, 1): # Tried writing a callable function with everything below, to fix memory issue. nogo
                                self.write_hourly_info(year, month, day, hour, date, indexes, keys, day_folder)
                            history_folder.insert(0, year_folder)
                        elif year_exists == 0 and int(year) > int(xml_year.tag[5:]): # xml_year is here the last year in the xml becasue we have left the for loop iterating over all xml_years in history
                            year_folder = ET.SubElement(history_folder, "year_" + year)
                            month_folder = ET.SubElement(year_folder, 'month_' + month)
                            day_folder = ET.SubElement(month_folder, 'day_' + day) # The day changes every time.
                            for hour in range(start_hour, end_hour, 1): # Tried writing a callable function with everything below, to fix memory issue. nogo
                                self.write_hourly_info(year, month, day, hour, date, indexes, keys, day_folder)

                else: #If no years exists at all:
                    year_folder = ET.SubElement(history_folder, "year_" + year)
                    month_folder = ET.SubElement(year_folder, 'month_' + month)
                    day_folder = ET.SubElement(month_folder, 'day_' + day) # The day changes every time.
                    for hour in range(start_hour, end_hour, 1): # Tried writing a callable function with everything below, to fix memory issue. nogo
                        self.write_hourly_info(year, month, day, hour, date, indexes, keys, day_folder)
                        
        tree.write('weather_history.xml')
                        

    def write_hourly_info(self, year, month, day, hour, start_date, indexes, keys, day_folder):
        
        str_hour = str(hour)
        if len(str_hour) == 1:
            str_hour = "0" + str_hour
        time = [year, month, day, str_hour]
        
        archieve_type = self.get_archieve_type(start_date, hour)
        url = self.url_format_time(time, archieve_type)
        
        info = self.fetch_info(url, indexes, keys, start_date, hour)
#                        info_names = ['wind_speed', 'wind_direction', 'temperature', 'cloud_cover', 'precipitation', 'altitude']
        
        hour_folder = ET.SubElement(day_folder, "hour_" + str_hour)
        
        wind_speed = ET.SubElement(hour_folder, "wind_speed")
        wind_speed.attrib = {"wind_speed" : info[0]}

        wind_direction = ET.SubElement(hour_folder, "wind_direction")
        wind_direction.attrib = {"wind_direction" : info[1]}

        cloud_cover = ET.SubElement(hour_folder, "cloud_cover")
        cloud_cover.attrib = {"cloud_cover" : info[3]}

        precipitation = ET.SubElement(hour_folder, "precipitation")
        precipitation.attrib = {"precipitation" : info[4]}
        
        temperature = ET.SubElement(hour_folder, "temperature")
        temperature.attrib = {"temperature" : info[2]}



    def insert_hourly_info(self, year, month, day, hour, start_date, indexes, keys, day_folder, insert_index):
        
        str_hour = str(hour)
        if len(str_hour) == 1:
            str_hour = "0" + str_hour
        time = [year, month, day, str_hour]
        
        archieve_type = self.get_archieve_type(start_date, hour)
        url = self.url_format_time(time, archieve_type)
        
        info = self.fetch_info(url, indexes, keys, start_date, hour)
#                        info_names = ['wind_speed', 'wind_direction', 'temperature', 'cloud_cover', 'precipitation', 'altitude']
        
        hour_folder = ET.Element("hour_" + str_hour)
        
        wind_speed = ET.SubElement(hour_folder, "wind_speed")
        wind_speed.attrib = {"wind_speed" : info[0]}

        wind_direction = ET.SubElement(hour_folder, "wind_direction")
        wind_direction.attrib = {"wind_direction" : info[1]}

        cloud_cover = ET.SubElement(hour_folder, "cloud_cover")
        cloud_cover.attrib = {"cloud_cover" : info[3]}

        precipitation = ET.SubElement(hour_folder, "precipitation")
        precipitation.attrib = {"precipitation" : info[4]}
        
        temperature = ET.SubElement(hour_folder, "temperature")
        temperature.attrib = {"temperature" : info[2]}
        
        day_folder.insert(insert_index, hour_folder)






        
        
        
    def fetch_index_keys(self, url, loc_lat_precise, loc_long_precise):
        
        lat_index = self.get_lat_index(url, loc_lat_precise) # Returns lat_index[list of: (x_index, y_index, lat_coord)]
#        print(lat_index)
#        print(("out of "), len(lat_index), "latitude locations:")
        
        coord_list = self.get_long(lat_index, url, loc_long_precise) # Returns long_list[x_index, y_index, lat_coord, long_coord]
#        print(coord_list)
#        print("There are only", len(coord_list), "longitudes that even are close.")
        
        index_coords = self.find_closest_index_coords(coord_list, loc_long_precise) # Returns one single closest_index_coords[x_index, y_index, lat_coord, long_coord]
#        print("This is from the closest one: ")
#        print("indexes and coords: ", index_coords)
        
        keys = self.check_keys(index_coords, url) # Returns keys [x_key, y_key] for the closest coordinate after checking the coordinate keys against ecah other.
#        print("keys: ", keys)
        
        return index_coords, keys
        


    def fetch_info(self, url, indexes, keys, date, hour):

        archieve_type = self.get_archieve_type(date, hour)

        if archieve_type == 1:

            self.ensemble = 0
            wind_direction, wind_speed = self.get_direction_speed(indexes, keys, url, date, hour)
            
            temperature = self.get_temperature(indexes, keys, url)
            cloud_cover = self.get_cloud_cover(indexes, keys, url)
            precipitation = self.get_precipitation(indexes, keys, url)
            altitude = self.get_altitude(indexes, keys, url)
    
            info = [wind_speed, wind_direction, temperature, cloud_cover, precipitation, altitude]

        elif archieve_type == 2:
            ensemble_date = datetime.date(2016, 11, 8) #Ensemble members from and counting /2016/11/08/kl:0200 to 2018 and the archieve_switch_date
            
            if date >= ensemble_date:
                self.ensemble = 1
                if date == ensemble_date:
                    if hour == 0 or hour == 1:
                        self.ensemble = 0
            else:
                self.ensemble = 0
            
            wind_direction, wind_speed = self.get_direction_speed(indexes, keys, url, date, hour)
            
            temperature = self.get_temperature(indexes, keys, url)
            cloud_cover = self.get_cloud_cover(indexes, keys, url)
            precipitation = self.get_precipitation(indexes, keys, url)
            altitude = self.get_altitude(indexes, keys, url)
            
            info = [wind_speed, wind_direction, temperature, cloud_cover, precipitation, altitude]
            
        return info
        
        
    def get_archieve_type(self, date, hour):
        archieve_switch_date = datetime.date(2018, 9, 18)
        
        if date >= archieve_switch_date:
            archieve_type = 1
            if date == archieve_switch_date and hour <= 8:
                archieve_type = 2
        else:
            archieve_type = 2
            
        return archieve_type
    
    
    
    
    def url_format_time(self, time, archieve_type):
        
        if archieve_type == 1:
            url = 'https://thredds.met.no/thredds/dodsC/metpparchive/{}/{}/{}/met_analysis_1_0km_nordic_{}{}{}T{}Z.nc.ascii?'
            url = url.format(*time[:3], *time)
            
        elif archieve_type == 2:
            url = 'https://thredds.met.no/thredds/dodsC/metpparchivev1/{}/{}/{}/met_analysis_1_0km_nordic_{}{}{}T{}Z.nc.ascii?'
            url = url.format(*time[:3], *time)
        return url
        
        
    def set_initial_indexes(self, loc_lat):
        short_lat = loc_lat[:3]        # 'xy.' is the short_lat.
        latitude_index_list = [['52.', (0, 0), (80, 0)], ['53.', (0, 570), (195, 0)], ['54.', (100, 850), (310, 0)], ['55.', (213, 810), (425, 0)], ['56.', (325, 820), (540, 0)], ['57.', (436, 890), (655, 0)], ['58.', (548, 850), (769, 0)], ['59.', (660, 830), (884, 0)], ['60.', (771, 850), (999, 0)], ['61.', (882, 870), (1115, 0)], ['62.', (994, 830), (1230, 0)], ['63.', (1105, 840), (1346, 0)], ['64.', (1216, 850), (1463, 0)], ['65.', (1327, 860), (1579, 0)], ['66.', (1439, 830), (1697, 0)], ['67.', (1550, 850), (1815, 0)], ['68.', (1662, 830), (1934, 0)], ['69.', (1773, 870), (2053, 0)], ['70.', (1885, 870), (2174, 0)], ['71.', (1998, 830), (2297, 0)], ['72.', (2110, 860), (2320, 1790)]]
        
        
        for latitude in latitude_index_list:
            if latitude[0] == short_lat:
                initial_x_index = latitude[1][0]
                step_x = 1
                stop_x_index = latitude[2][0]  #max 2320 and is the [x] listing chunks
                break
        

        inital_y_index = 0
        step_y = 1
        stop_y_index = '1795' #max 1795 and is the [y] coord in each chunk
        
        
        
        
        
        
        return initial_x_index, step_x, stop_x_index, inital_y_index, step_y, stop_y_index
        
        
        
        
    def get_lat_index(self, url, loc_lat_precise):
        loc_lat = loc_lat_precise[:5]
        action = 'latitude'
        inquiry_type = '{}[{}:{}:{}][{}:{}:{}]'
        
        url = url + inquiry_type
        inital_x_index, step_x, stop_x_index, inital_y_index, step_y, stop_y_index = self.set_initial_indexes(loc_lat)
        
        url = url.format(action, str(inital_x_index), str(step_x), stop_x_index, str(inital_y_index), str(step_y), stop_y_index)
        
        open('data.txt', 'wb').write(request.urlopen(url).read())
        lat_index = []
        with open('data.txt', 'r') as file:
            for line in file.readlines():
                try:
                    if line[100]: # If the line is reeally long:
                        coord_list = line.split()
                        local_x_index = (coord_list.pop(0)) # The first entry in every line is fortunatly the index of that line.
                        local_x_index = (str(local_x_index))[1:(len(local_x_index)-2)] # Extracting the number, insted of "[xy]"
                        for y_index, coord in enumerate(coord_list):
                            if loc_lat == coord[0:len(loc_lat)]: # Checking of the loc_lat sent in equals a coordinate of equal lenght in the file.
                                                                # The following is done when the coordinate found matches the latitude sent in.
                                coord = coord[0:(len(coord)-1)] # Removing "," at the end of every coordinate
                                
                                x_index = inital_x_index + (int(local_x_index) * step_x)# Calculating the correct x_index.
                                y_index = inital_y_index + (y_index * step_y) # Calculating the correct y_index.

                                lat_index.append((x_index, y_index, coord)) # Also returning the full latitude found as coord, not hte one sent in.
                except IndexError: # if the line is not reeally long:
                    pass # pass the line, go to the next.
        return lat_index
    

    def get_long(self, lat_index, url, loc_long_precise):
        loc_long = loc_long_precise[:3]
        first_x_index = int(lat_index[0][0]) # Very first x_index of the lat_index list
        last_x_index = int(lat_index[(len(lat_index)-1)][0]) # Last x_index of the lat_index list
        step_x = 1 # Since the function is somewhat effiecient, in, it only goes through the list of latitude locations allready found
        step_y = 1 # accessing the indexes directly, seeing if they are close enough. The steps should likely not be skipped here
        coord_list = [] # For appending
        
        action = 'longitude'
        inquiry_type = '{}[{}:{}:{}][{}:{}:{}]'
        url = url + inquiry_type
        long_url = url.format(action, first_x_index, step_x, last_x_index, 0, step_y, 1795)
        
        open('long_data.txt', 'wb').write(request.urlopen(long_url).read())
        with open('long_data.txt', 'r') as file:
            for line in file.readlines():
                try:
                    if line[100]: # If the line is reeally long:
                        
                        if line[0] == ('['): # and if it is a chunk of index_coords it will start like this.
                            local_x_index = ''
                            x = 1
                            while line[x] != (']'):
                                local_x_index = local_x_index + line[x]
                                x += 1
                            x_index = first_x_index + (int(local_x_index) * step_x) # Calculating the actualx index
                        else: # There are lines(chunks) of keys at the end, that are not indexed, theese are skipped.
                            break
                        
                        answer = self.check_if_index_exists_in_loc_index(lat_index, x_index) # Returns True if x_index is in the list of lat_index sent in, False if not
                        
                        if answer == True: # Do this if x_index is in the list of lat_index
                            long_coord_list = line.split()
                            long_coord_list.pop(0) # The first index in the list is still an index.
                            
#                            print(long_coord_list) # Will now print a list[] of y index_coords for each True x-chunk in long_data
#                            print(x_index) will now print the true index of each x-chunk in long_data
                            
                            for entry in lat_index: # Going through the latitude locations found in self.get_lat_index()
                                if entry[0] == x_index: # Do this if we are in the same x-chunk
                                    
                                    long_x = entry[0] # x_index from lat_index
                                    long_y =entry[1] # y_index
                                    latitude = entry[2] # lat_coord
                                    longitude = (long_coord_list[entry[1]]).strip(',')
                                    # And now we proceed to checking for each possible lattitude, using the index directly, if the longitude is even close:
                                    if longitude[:len(loc_long)] == loc_long: #There are many finds along the latitude, append only if it is near the longitude-
                                        coord_list.append((long_x, long_y, latitude, longitude)) # -that we are searching for. To be narrowed down to one single next.
                        elif answer == False:
                            pass # if answer is 'False', you are useless to me..
                except IndexError: # if the line is not reeally long:
                    pass # pass the line, go to the next in "for line in file.readlines():"
        return coord_list
    def check_if_index_exists_in_loc_index(self, lat_index, x_index):
        for index in lat_index:
            if index[0] == x_index:
                return True
        return False




    def find_closest_index_coords(self, coord_list, loc_long_precise):
        longitudes = []
        for entry in coord_list:
            longitudes.append(float(entry[3]))
        closest_latitude = min(longitudes, key=lambda x:abs(x-float(loc_long_precise)))
        
        for entry in coord_list:
            if entry[3] == str(closest_latitude):
                closest_index_coords = entry
        return closest_index_coords



    def check_keys(self, closest_index_coords, url):
        
        action1 = 'latitude'
        action2 = 'longitude'
        
        inquiry_type = '{}[{}][{}]'
        
        lat_spot_url = url + inquiry_type
        long_spot_url = url + inquiry_type
        
        x_index = closest_index_coords[0]
        y_index =closest_index_coords[1]
        
        lat_url = lat_spot_url.format(action1, x_index, y_index)
        long_url = long_spot_url.format(action2, x_index, y_index)
        
        key_urls = [lat_url, long_url]
        keys = []
        for key_url in key_urls:
            open('key_data.txt', 'wb').write(request.urlopen(key_url).read())
            with open('key_data.txt', 'r') as file:
                for index, line in enumerate(file.readlines()):
    #                print(index, ";", line)
                    if index == 14 or index == 17:                        
                        if index == 14: # This line contains the x-key
                            line = line.strip()
                            x_key = line
                        if index == 17: # This line contains the y-key
                            line = line.strip()
                            y_key = line
            keys.append((x_key,y_key))
        if keys[0] == keys[1]: # checking if both keys are the excact same.
            return keys[0]
        else:
            print("The keys are not the same")
            return False
        
        
        
        
        
    def calculate_offset(self, index_coords, place):
        reqested_coords = (place[0], place[1])
        found_coords = (index_coords[2], index_coords[3])
        
        requested_lon = float(reqested_coords[1])
        requested_lat = float(reqested_coords[0])
        found_lon = float(found_coords[1])
        found_lat = float(found_coords[0])
        
        
        def find_distance(lon1, lat1, lon2, lat2 ):
            R=6371000                               # radius of Earth in meters
            phi_1=math.radians(lat1)
            phi_2=math.radians(lat2)

            delta_phi=math.radians(lat2-lat1)
            delta_lambda=math.radians(lon2-lon1)
            
            a=math.sin(delta_phi/2.0)**2+\
               math.cos(phi_1)*math.cos(phi_2)*\
               math.sin(delta_lambda/2.0)**2
            c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))
            
            meters=R*c                         # output distance in meters
            return meters

        def bearing(lon1, lat1, lon2, lat2):
            lon1 = math.radians(lon1)
            lat1 = math.radians(lat1)
            lon2 = math.radians(lon2)
            lat2 = math.radians(lat2)
            dlon = lon2 - lon1

            y = math.sin(dlon) * math.cos(lat2);
            x = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dlon);
            degrees = math.degrees(math.atan2(y, x))
            if degrees < 0:
                degrees = degrees + 360
                
            return degrees
        
        def get_compass_symbol(degree):
            compass_brackets = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW", "N"]

            compass_lookup = round(degree / (45/2))
            symbol = compass_brackets[compass_lookup] 
            return symbol
        
        meters = find_distance(requested_lon, requested_lat, found_lon, found_lat)
        degrees = bearing(requested_lon, requested_lat, found_lon, found_lat)
        symbol = get_compass_symbol(degrees)

        offset = meters, degrees, symbol
        return offset
        
        
        
        
        
    def get_direction_speed(self, indexes, keys, url, date, hour):
        vector_date = datetime.date(2019, 7, 2) # wind_direction and speed from 2019/07/02/kl.08:00 to present, x,y vectors before then.
        
        if date >= vector_date: # If the date is after the vector date
            outlay = 1 # Get'em directly!
            
            if date == vector_date: # Unless it's the switch day, then the switch happens at 8 o'Clock! The last vector sighted at 07 o'Clock!
                if hour < 8: # The last vector sighted at 07 o'Clock! 
                    outlay = 2 # Do vectors!
        else:
            outlay = 2 # Get the vectors!
            
        if outlay == 1: # Get speed and direction directly
            action1 = 'wind_direction_10m'
            action2 = 'wind_speed_10m'
            wind_direction = self.get_wind_direction(indexes, keys, url, action1)
            wind_speed = self.get_wind_speed(indexes, keys, url, action2)
#            print(wind_direction, wind_speed)
            
        if outlay == 2: # get and format wind vectors
            
            action1 = 'x_wind_10m'
            action2 = 'y_wind_10m'
            
            x_wind = self.get_x_wind(indexes, keys, url, action1)
            y_wind = self.get_y_wind(indexes, keys, url, action2)
            
            magnitude = math.sqrt(float(x_wind)*float(x_wind) + float(y_wind)*float(y_wind))
            
            degrees_temp = math.atan2(-float(x_wind), -float(y_wind))/math.pi*180
            if degrees_temp < 0:
                degrees_temp = 360 + degrees_temp
            direction = degrees_temp
                        
            wind_direction = str(direction)
            wind_speed = str(magnitude)
            
        return [wind_direction, wind_speed]
        

    
    
    def get_x_wind(self, indexes, keys, url, action):
        if self.ensemble == 0:
            outlay = 1
            inquiry_type = '{}[0][{}][{}]'
        elif self.ensemble == 1:
            outlay = 3
            inquiry_type = '{}[0][0][{}][{}]'
        url = url + inquiry_type
        
        x_index = indexes[0]
        y_index = indexes[1]
        x_wind_url = url.format(action, x_index, y_index)
        try:
            x_wind = self.get_info_from_url(x_wind_url, keys, outlay)
        except:
            return 0
        return x_wind
    
    def get_y_wind(self, indexes, keys, url, action):
        if self.ensemble == 0:
            outlay = 1
            inquiry_type = '{}[0][{}][{}]'
        elif self.ensemble == 1:
            outlay = 3
            inquiry_type = '{}[0][0][{}][{}]'
        url = url + inquiry_type
        
        x_index = indexes[0]
        y_index = indexes[1]
        y_wind_url = url.format(action, x_index, y_index)
        try:
            y_wind = self.get_info_from_url(y_wind_url, keys, outlay)
        except:
            return 0
        return y_wind
    
    
    def get_wind_speed(self, indexes, keys, url, action):

        if self.ensemble == 0:
            outlay = 1
            inquiry_type = '{}[0][{}][{}]'
        elif self.ensemble == 1:
            outlay = 3
            inquiry_type = '{}[0][0][{}][{}]'
        
        url = url + inquiry_type
        
        x_index = indexes[0]
        y_index = indexes[1]
        speed_url = url.format(action, x_index, y_index)
        
        try:
            wind_speed = self.get_info_from_url(speed_url, keys, outlay)
        except:
            return ("wind_speed")
        return wind_speed
    
    def get_wind_direction(self, indexes, keys, url, action):
        
        if self.ensemble == 0:
            outlay = 1
            inquiry_type = '{}[0][{}][{}]'
        elif self.ensemble == 1:
            outlay = 3
            inquiry_type = '{}[0][0][{}][{}]'
        url = url + inquiry_type
        
        x_index = indexes[0]
        y_index = indexes[1]
        direction_url = url.format(action, x_index, y_index)
        try:
            wind_direction = self.get_info_from_url(direction_url, keys, outlay)
        except:
            return ("wind_direction")
        return wind_direction
        
    def get_temperature(self, indexes, keys, url):
        action = 'air_temperature_2m'
        if self.ensemble == 0:
            outlay = 1
            inquiry_type = '{}[0][{}][{}]'
        elif self.ensemble == 1:
            outlay = 3
            inquiry_type = '{}[0][0][{}][{}]'
        url = url + inquiry_type
        
        x_index = indexes[0]
        y_index = indexes[1]
        temperature_url = url.format(action, x_index, y_index)
        try:
            temp = self.get_info_from_url(temperature_url, keys, outlay)
            temperature = str(float(temp) - 273.15)
            
            
        except:
            return ("temperature")
        return temperature
        
    def get_cloud_cover(self, indexes, keys, url):
        action = 'cloud_area_fraction'
        if self.ensemble == 0: # Some urls has an extra dimention: ensemble, of 10 (0-9) possible values of the same time
            outlay = 1
            inquiry_type = '{}[0][{}][{}]'
        elif self.ensemble == 1:
            outlay = 3
            inquiry_type = '{}[0][0][{}][{}]'
        url = url + inquiry_type
        
        x_index = indexes[0]
        y_index = indexes[1]
        cloud_cover_url = url.format(action, x_index, y_index)
        try:
            cloud_cover = self.get_info_from_url(cloud_cover_url, keys, outlay)
        except:
            return ("cloud_cover")
        return cloud_cover
        
    def get_precipitation(self, indexes, keys, url):
        action = 'precipitation_amount'
        if self.ensemble == 0:
            outlay = 1
            inquiry_type = '{}[0][{}][{}]'
        elif self.ensemble == 1:
            outlay = 3
            inquiry_type = '{}[0][0][{}][{}]'
        url = url + inquiry_type
        
        x_index = indexes[0]
        y_index = indexes[1]
        precipitation_url = url.format(action, x_index, y_index)
        try:
            precipitation = self.get_info_from_url(precipitation_url, keys, outlay)
        except:
            return ("precipitation")
        return precipitation
        
    def get_altitude(self, indexes, keys, url):
        action = 'altitude'
        inquiry_type = '{}[{}][{}]'
        url = url + inquiry_type
        
        x_index = indexes[0]
        y_index = indexes[1]
        altitude_url = url.format(action, x_index, y_index)
        try:
            altitude = self.get_info_from_url(altitude_url, keys, 2)
        except:
            return ("altitude")
        return altitude
    
    
    

    
    
    
    
    

    def get_info_from_url(self, url, keys, outlay):
        if outlay == 1: # the url page has a few different numbers of lines depending on their content,
            x, y, z, f= 12, 18, 21, 8
        elif outlay == 2:
            x, y, z, f = 11, 14, 17, 5
        elif outlay == 3:
            x, y, z, f = 13, 22, 25, 11
                
        open('info_data.txt', 'wb').write(request.urlopen(url).read())
        with open('info_data.txt', 'r') as file:
            for index, line in enumerate(file.readlines()):
#                print(index, ";", line.strip())
                if index == x or index == y or index == z:
                    if index == x: # This line contains the given information
                        line = line.strip()
                        line = line[f:] # Removing "[0][0], " in the beginning of each line.
                        info = line
                    if index == y: # This line contains the x-key
                        line = line.strip()
                        x_key = line
                    if index == z: # This line contains the y-key
                        line = line.strip()
                        y_key = line
        info_keys = [x_key, y_key]
#        print("info_keys", type(info_keys), info_keys)
#        print("keys:", type(keys), keys)
        if info_keys == keys: # By retrieving the same keys from each document opened, i asure the information retrieved is correct
            return info
        else:
            pass
            print("The keys and therefore info retrieved from following url is not matching the index_coords: ", url)







    def setup_XML(self):
        sites = ET.Element('sites')
        mydata = ET.tostring(sites)
        myfile = open("weather_history.xml", "wb")
        myfile.write(mydata)
        myfile.close()


            
#place = ['61.562161', '7.997203', "Sognefjellshytta"]
#date, start_hour, end_hour, previus_year, previus_month = [datetime.date(2015, 8, 15), 9, 22, 2019, 12]
#Write_history(place, date, start_hour, end_hour, previus_year, previus_month)
