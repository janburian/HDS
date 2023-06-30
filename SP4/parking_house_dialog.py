# Modules import 
from dialog import SpeechCloudWS, Dialog
import logging
from pathlib import Path
from datetime import datetime, timedelta
import re

# Own modules import 
import data_acquisition
import translator

class ParkingHouseDialog(Dialog):
    async def main(self):
        await self.welcome()

        data = await self.get_data()

        await self.slu(data)

        await self.synthesize_and_wait(text="Konec dialogu. Přeji pěkný zbytek dne a nashledanou.", voice="Jiri210")
    
    async def welcome(self):
        pass
        #await self.synthesize_and_wait("Dobrý den. Jsem hlasový dialogový systém, který pro Vás zjišťuje zaplněnost plzeňských parkovacích domů Rychtářka a Nové divadlo.", voice="Jiri210")


    # Getting data
    async def get_data(self):
        print("Getting data...Please wait.")
        # Historical
        #historical_data_nove_divadlo = data_acquisition.load_historical_data(Path('./data/data-pd-novedivadlo.csv'))
        #historical_data_rychtarka = data_acquisition.load_historical_data(Path('./data/data-pd-rychtarka.csv'))

        url_nove_divadlo_historical = 'https://onlinedata.plzen.eu/data-pd-novedivadlo.php'
        url_rychtarka_historical = 'https://onlinedata.plzen.eu/data-pd-rychtarka.php'

        historical_data_nove_divadlo = data_acquisition.get_data(url_nove_divadlo_historical, 'historical')
        historical_data_rychtarka = data_acquisition.get_data(url_rychtarka_historical, 'historical')
        
        # Actual data
        url_nove_divadlo_actual = 'https://onlinedata.plzen.eu/data-pd-novedivadlo-actual.php'
        url_rychtarka_actual = 'https://onlinedata.plzen.eu/data-pd-rychtarka-actual.php'

        actual_data_nove_divadlo = data_acquisition.get_data(url_nove_divadlo_actual, 'actual')
        actual_data_rychtarka = data_acquisition.get_data(url_rychtarka_actual, 'actual')

        return historical_data_nove_divadlo, historical_data_rychtarka, actual_data_nove_divadlo, actual_data_rychtarka


    # Defining grammars
    async def prepare_grammars(self):
        grammars = self.grammar_from_dict("command", {
                "end": {"konec","skonči","ukončit"}, 
                "continue": {"pokračuj", "pokračovat", "další"},
                "help": {"nápověda", "pomoc", "help", "jsem ztracen"},
                "bye": {"nashledanou", "děkuji a nashledanou"}}) 
        
        grammars += self.grammar_from_dict("confirm", 
                {"confirm":{"potvrzuji", "potvrzuju", "potvrzuje", "přesně tak", "ano"}})

        grammars += self.grammar_from_dict("not_confirm", 
                {"not_confirm":{"nepotvrzuji", "nepotvrzuju", "nepotvrzuje", "ne"}})

        grammars += self.grammar_from_dict("parking_house", {
                "Rychtářka": {"Rychtářce", "v rychtářce", "na Rychtářce", "na rychtářce", "Rychtářka", "Rychtářky"},
                "Nové divadlo": {"Novém divadle", "v novém divadle", "na Novém divadle", "na novém divadle", "Nové_divadlo", "nové_divadlo", "Novém_divadle", "Nového_divadla", "nového_divadla"}})
        
        grammars += self.grammar_from_dict("weekday", {
                "Monday":{"pondělí", "pondělím"}, 
                "Tuesday":{"úterý", "úterým", "úterek"}, 
                "Wednesday":{"středa", "středu", "středo", "středě", "středou", "středy"}, 
                "Thursday": {"čtvrtek", "čtvrtka", "čtvrtku", "čtvrtkem"},
                "Friday": {"pátek", "pátkem", "pátku"}, 
                "Saturday": {"sobota", "soboty", "sobotě", "sobotu", "soboto", "sobotou"},
                "Sunday": {"neděle", "nedělí", "neděli"},
                "today_1":{"zítra", "další den", "následující den", "v dalším dni", "v následujícím dni"}, 
                "today_2":{"pozítří"},
                "today_-1":{"včera", "předchozí den", " v předchozím dni"},
                "today_-2":{"předevčírem"},
                "last_Monday":{"minulé pondělí"},
                "last_Tuesday":{"minulé úterý"},
                "last_Wednesday":{"minulou středu", "minulá středa"},
                "last_Thursday":{"minulý čtvrtek"},
                "last_Friday":{"minulý pátek"},
                "last_Saturday":{"minulou sobotu", "minulá sobota"},
                "last_Sunday":{"minulou neděli", "minulá neděle"}
                })
        
        grammars += self.grammar_from_dict("time", {
                "now": {"aktuálně", "aktuální", "právě teď", "nyní", "v tento čas", "teď", "v současné době", "současná doba", "v tomto čase"}, 
                "01:00:00": {"v jednu ráno", "jedna ráno", "v jednu ráno", "jedna ráno", "v jedna nula nula", "v jednu nula nula", "jedna hodina", "jednu hodinu"},
                "01:30:00": {"v jednu třicet ráno", "jedna třicet ráno", "v jedna třicet", "v jednu třicet", "půl druhé ráno"},
                "02:00:00": {"ve dvě ráno", "ve dvě nula nula", "dvě ráno", "dvě hodiny ráno", "dvě hodiny"},
                "02:30:00": {"ve dvě třicet ráno", "ve dvě třicet", "půl třetí ráno"},
                "03:00:00": {"ve tři ráno", "tři hodiny ráno", "ve tři nula nula", "tři hodiny"},
                "03:30:00": {"ve tři třicet ráno", "ve tři třicet", "půl čtvrté ráno"},
                "04:00:00": {"ve čtyři ráno", "ve čtyři hodiny ráno", "ve čtyři nula nula", "čtyři hodiny"},
                "04:30:00": {"ve čtyři třicet ráno", "ve čtyři třicet", "půl páté ráno"},
                "05:00:00": {"v pět ráno", "pět ráno", "pět hodin ráno", "v pět nula nula", "pět hodin"},
                "05:30:00": {"v pět třicet ráno", "pět třicet ráno", "půl šesté ráno"},
                "06:00:00": {"v šest ráno", "šest ráno", "šest hodin ráno", "v šest nula nula", "šest hodin"},
                "06:30:00": {"v šest třicet ráno", "šest třicet ráno", "v šest třicet", "šest třicet", "půl sedmé ráno"},
                "07:00:00": {"sedm ráno", "sedm hodin ráno", "v sedm ráno", "sedm", "v sedm", "sedm hodin"},
                "07:30:00": {"sedm třicet", "půl osmé ráno", "o půl osmé ráno", "sedm třicet ráno", "v sedm třicet ráno"},
                "08:00:00": {"v osm ráno", "osm ráno", "osm hodin ráno", "v osm nula nula", "osm nula nula", "osm hodin"},
                "08:30:00": {"osm třicet ráno", "v osm třicet ráno", "půl deváté ráno", "v půl deváté ráno", "o půl deváté ráno"},
                "09:00:00": {"devět ráno", "v devět ráno", "v devět hodin ráno",  "devět nula nula ráno", "v devět nula nula", "devět hodin"},
                "09:30:00": {"devět třicet ráno", "v devět třicet ráno", "půl desátá ráno", "v půl desáté ráno"},
                "10:00:00": {"deset ráno", "deset hodin ráno", "deset nula nula ráno", "v deset nula nula ráno", "v deset ráno", "deset hodin"},
                "10:30:00": {"deset třicet ráno", "v deset třicet ráno", "v půl jedenácté ráno", "půl jedenáctá ráno"},
                "11:00:00": {"jedenáct ráno", "jedenáct hodin ráno", "jedenáct ráno", "jedenáct nula nula ráno", "jedenáct nula nula ráno", "jedenáct hodin"},
                "11:30:00": {"jedenáct třicet ráno", "v jedenáct třicet ráno", "v půl dvanácté ráno", "o půl dvanácté ráno"},
                "12:00:00": {"poledne", "v poledne", "o poledni", "dvanáct nula nula", "dvanáct hodin v poledne", "dvanáct hodin"},
                "12:30:00": {"dvanáct třicet", "dvanáct třicet odpoledne", "ve dvanáct třicet", "v půl jedné odpoledne"},
                "13:00:00": {"třináct", "třináct hodin", "třináct nula nula", "ve třináct", "ve třináct nula nula", "v jednu odpoledne", "třináct hodin"},
                "13:30:00": {"ve třináct třicet", "třináct třicet", "půl druhé odpoledne"},
                "14:00:00": {"čtrnáct nula nula", "čtrnáct", "čtrnáct hodin", "ve dvě odpoledne", "dvě odpoledne", "ve čtrnáct", "čtrnáct hodin"},
                "14:30:00": {"čtrnáct třicet", "ve čtrnáct třicet", "v půl třetí odpoledne", "půl třetí odpoledne"},
                "15:00:00": {"v patnáct nula nula", "patnáct hodin", "ve tři odpoledne", "v patnáct", "patnáct hodin"},
                "15:30:00": {"v patnáct třicet", "patnáct třicet", "půl čtvrté odpoledne", "v půl čtvrté odpoledne"},
                "16:00:00": {"šestnáct nula nula", "v šestnáct nula nula", "v šestnáct", "v šestnáct hodin", "ve čtyři hodiny odpoledne", "čtyři hodiny odpoledne", "šestnáct hodin"},
                "16:30:00": {"šestnáct třicet", "v šestnáct třicet", "v půl páté odpoledne", "o půl páté odpoledne"},
                "17:00:00": {"sedmnáct nula nula", "v sedmnáct nula nula", "sedmnáct hodin", "pět hodin odpoledne", "v pět hodin odpoledne", "sedmnáct hodin"},
                "17:30:00": {"sedmnáct třicet", "v sedmnáct třicet", "v půl šesté odpoledne", "v půl šesté večer", "o půl šesté večer"},
                "18:00:00": {"osmnáct", "osmnáct nula nula", "šest večer", "osmnáct hodin"},
                "18:30:00": {"osmnáct třicet", "o půl sedmé večer", "půl sedmá večer"},
                "19:00:00": {"devatenáct nula nula", "sedm večer", "devatenáct hodin", "sedm hodin večer", "devatenáct hodin"},
                "19:30:00": {"devatenáct třicet", "půl osmá večer", "v půl osmé večer", "sedm třicet večer"},
                "20:00:00": {"dvacet nula nula", "osm večer", "ve dvacet hodin", "osm hodin večer", "osmá večerní", "dvacet hodin"},
                "20:30:00": {"dvacet třicet", "půl devátá večer", "o půl deváté večer", "v půl deváté večer"},
                "21:00:00": {"dvacet jedna nula nula", "devět hodin večer", "dvacet jedna hodin"},
                "21:30:00": {"dvacet jedna třicet", "půl desátá večer", "o půl desáté večer", "v půl desátý večer"},
                "22:00:00": {"dvacet dva nula nula", "ve dvacet dva hodin", "v deset hodin večer", "dvacet dva hodin"},
                "22:30:00": {"dvacet dva třicet", "půl jedenáctá večer", "o půl jedenácté večer", "v půl jedenácté večer", "půl jedenáctá večerní"},
                "23:00:00": {"dvacet tři nula nula", "jedenáct večer", "jedenáct hodin večer", "dvacet tři hodin"},
                "23:30:00": {"dvacet tři třicet", "o půl dvanácté večer", "v půl dvanácté večer"},
                "00:00:00": {"dvacet čtyři nula nula", "půlnoc", "půlnoci", "nula nula nula nula"}, 
                "00:30:00": {"nula třicet", "o půl jedné v noci", "o půl jedné ráno", "v půl jedné v noci", "v půl jedné ráno"}, 
                "rel_1_hour": {"za hodinu","za jednu hodinu"}, 
                "rel_2_hours": {"za dvě hodiny", "za sto dvacet minut"},
                "rel_3_hours": {"za tři hodiny", "za tři_hodiny", "za sto osmdesát minut"},
                "rel_4_hours": {"za čtyři_hodiny", "za dvě stě čyřicet minut"},
                "rel_5_hours": {"za pět_hodin", "za tři sta minut"},
                "rel_6_hours": {"za šest_hodin", "za šest_hodin"},
                "rel_7_hours": {"za sedm_hodin", "za sedm_hodin"},
                "rel_8_hours": {"za osm_hodin", "za osm_hodin"},
                "rel_9_hours": {"za devět_hodin", "za devět hodin"},
                "rel_10_hours": {"za deset_hodin", "za deset_hodin"},
                "rel-0.5-hour": {"před půl hodinou"},
                "rel-1-hour": {"před hodinou"},
                "rel-1.5-hours": {"před hodinou a půl"}, 
                "rel-2-hours": {"před dvěma hodinami", "před dvouma hodinama"},
                })
        
        grammars += self.grammar_from_dict("statistics", {
                "free_spaces_%": {"volná místa v %", "volná kapacita v %", "volná v %"},
                "free_spaces": {"počet volných míst","volná místa","volno", "neprázdná místa", "volných míst", "volná kapacita", "volná", "volných"}, 
                "occupied_spaces": {"počet obsazených míst", "obsazená místa", "obsazených parkovacích míst", "obsazených míst", "zaplněnost", "obsazená", "zaplněná", "obsazenost", "aktuální počet aut", "obsazeno"},
                "capacity": {"kapacita", "kapacitou", "maximální kapacita", "celkový počet míst"},
                "occupied_spaces_%": {"obsazená místa %", "obsazenost %", "zaplněná kapacita %"},
                })
        
        grammars += self.grammar_from_dict("yes_no_questions", {
                "available": {"jsou volná místa", "jsou dostupná", "je volno", "je tam místo", "je místo", "jsou volná místa", "je k dispozici", "ještě volno", "vejdu se do", "je ještě místo", "je tam ještě místo", "je tam volno", "je tam volná kapacita"},
                "nonavailable": {"je plno", "je narváno", "je tam plno"}
                })
        
        return grammars
    

    # Returns string of the todays day 
    async def get_todays_day(self):
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dt_now = datetime.now()
        weekday_idx = dt_now.weekday()
        print(weekday_idx)

        return weekdays[weekday_idx]
    

    # Returns weekday according to index (Monday = 0, Tuesday = 1,...)
    async def get_weekday_string(self, idx: int):
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        return weekdays[idx]


    # Returns frame dictionary with the recognized entities
    async def get_frame_dictionary(self, result: list):
        relative_times_list = ["now", "rel_1_hour", "rel_2_hours", "rel_3_hours", "rel_4_hours", "rel_5_hours", "rel_6_hours", "rel_7_hours", "rel_8_hours",
                "rel_9_hours", "rel_10_hours", "rel_11_hours", "rel_12_hours", "rel-0.5-hour", "rel-1-hour", "rel-1.5-hours", "rel-2-hours"]
        recognized_entities = result.entity_types

        frame_dict = {"parking_house": "", # Frame dictionary inicialization
                      "time": "now", 
                      "weekday": await self.get_todays_day(), 
                      "statistics": "free_spaces"}

        idx = 0           
        if len(recognized_entities) == 0:
            while idx < 4:
                await self.synthesize_and_wait(text=f"Nebyla rozpoznána žádná informace. Prosím řekněte alespoň název parkovacího domu.")
                result = await self.recognize_and_wait_for_slu_result(timeout=10.)
                recognized_entities = result.entity_types
                if len(recognized_entities) == 0:
                    idx += 1
                else: 
                    break
        
        if "parking_house" in recognized_entities:
            parking_house = result.parking_house.first
            frame_dict["parking_house"] = parking_house

        if "time" in recognized_entities:
            time = result.time.first
            frame_dict["time"] = time

            if frame_dict["time"] in relative_times_list:
                frame_dict["weekday"] = await self.get_todays_day()

        if "weekday" in recognized_entities:
            weekday = result.weekday.first
            frame_dict["weekday"] = weekday

        if "statistics" in recognized_entities:
            statistics = result.statistics.first
            frame_dict["statistics"] = statistics

        return frame_dict
    
    
    # Returns missing information which is missing in dictionary
    async def determine_missing_info(self, data_frame: dict):
        missing_info = []
        for key in data_frame:
            if data_frame[key] == "":
                missing_info.append(key)
        
        return missing_info
    

    # Function to convert list to string
    async def list_to_string(self, s):
    
        # initialize an empty string
        str1 = " "
    
        # return string
        return (str1.join(s))


    # Tell the user the info which is missing
    async def tell_missing_info(self, missing_info: list, data_frame: dict):
        translate_dictionary = {
            "parking_house": "parkovací dům", 
            "time": "čas nebo relativní čas", 
            "weekday": "den v týdnu", 
            "statistics": "statistika která vás zajímá například volná či obsazená místa"
        }

        missing_entities_text_list = []

        while True: 
            for i in range(len(missing_info)):
                print(str(len(missing_info)))
                text = translate_dictionary[missing_info[i]]
                missing_entities_text_list.append(text)
                
            await self.synthesize(text="Prosím, řekněte mi následující chybějící údaj či údaje")
            await self.synthesize_and_wait(text=await self.list_to_string(missing_entities_text_list))
            result = await self.recognize_and_wait_for_slu_result(timeout=15.)
            recognized_entities = result.entity_types

            for entity in recognized_entities:
                if entity in missing_info:
                    data_frame[entity] = result.entities[entity].first

            print(data_frame)

            res = await self.check_frame_complete(data_frame)

            if res[0] == True:
                return data_frame
            
            else:
                new_missing_info = res[1] 
                print(new_missing_info)
                missing_info = new_missing_info
                missing_entities_text_list.clear()
                    

    # Checks if data frame is complete
    async def check_frame_complete(self, data_frame: dict):
        num_missing_entities = 0
        missing_entities = []

        for key in data_frame:
            if data_frame[key] == "":
                num_missing_entities += 1
                missing_entities.append(key)
            
        if num_missing_entities == 0:
            return True, []
        else:
            return False, missing_entities
        

    # Returns the date of the previous day, for example the date of last Sunday
    async def get_date_previous_day(self, input_day, start_date=None):
        # https://www.tutorialspoint.com/how-to-determine-last-friday-s-date-using-python
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday','Friday', 'Saturday', 'Sunday']
        if start_date is None:
            # assiging today's date(current date) to the start date
            start_date = datetime.today()
            # getting the weekday number
            day_number = start_date.weekday()
            # Get the index of the target weekday
            day_number_target = weekdays.index(input_day)
            # getting the last weekday
            days_ago = (7 + day_number - day_number_target) % 7

        # checking whether the above days ago result is equal to 0
        if days_ago == 0:
            # assigning 7 to the days ago
            days_ago = 7

        # Subtract the above number of days from the current date(start date)
        # to get the last week's date of the given day
        target_date = start_date - timedelta(days=days_ago)

        # returning the last week's date of the input date
        return target_date


    # Data processing based on user's input
    async def process_data(self, data_frame: dict, data):
        translate_dict = {
            "free_spaces": "volná místa", 
            "occupied_spaces": "obsazená místa",
            "capacity": "kapacitu",
            "free_spaces_%": "volná místa v procentech",
            "occupied_spaces_%": "obsazená místa v procentech",
        }

        statistics = data_frame["statistics"]
        translation_statistics = translate_dict[statistics]

        print(data_frame["parking_house"])

        await self.synthesize_and_wait(text=("Vstupní data kompletní. Nyní pro vás zjišťuji {} na základě zadaných informací pro parkovací dům {}").format(translation_statistics, data_frame["parking_house"]))
        time = data_frame["time"]
        statistics = data_frame["statistics"]
        parking_house = data_frame["parking_house"]
        weekday = data_frame["weekday"]

        data_idx = 0

        if parking_house == "Nové divadlo":
            data_idx = 0
        else:
            data_idx = 1

        time_regex = r'^\d{2}:\d{2}:\d{2}$'
        historical_data = data[data_idx]
        actual_data = data[data_idx + 2]
        todays_weekday = await self.get_todays_day()
        statistics_data = []

        if re.match(time_regex, time) and "_" not in weekday: # Historical data (checking if time is in correct format: 00:00:00)
            res = data_acquisition.get_data_weekday_time(historical_data, weekday, [time])
            statistics_data = data_acquisition.count_statistics(res)

        elif time == "now" and weekday != todays_weekday and "_" not in weekday: # Undefined time, defined weekday
            res = data_acquisition.get_data_weekday_time(historical_data, weekday, [(datetime.now()).strftime('%H:%M:%S')])
            statistics_data = data_acquisition.count_statistics(res)

        elif time == "now" and weekday == todays_weekday: # Actual
            statistics_data = data_acquisition.get_actual_info(actual_data)

        elif "rel_" in time and weekday == todays_weekday: # Future (based on historical data) - approximation
            relative_time_hours = re.findall(r'\d+', time)[0]
            time_delta = (datetime.now() + timedelta(hours=int(relative_time_hours))).strftime('%H:%M:%S')

            res = data_acquisition.get_data_weekday_time(historical_data, weekday, [time_delta])
            statistics_data = data_acquisition.count_statistics(res)

        elif "rel-" in time and weekday == todays_weekday: # Past (based on actual data) - approximation
            relative_time_hours = re.findall(r'\d+', time)[0]
            #time_delta = (datetime.now() - timedelta(hours=int(relative_time_hours))).strftime('%H:%M:%S')
            time_delta = (datetime.now() - timedelta(hours=int(relative_time_hours)))

            res = data_acquisition.get_data_certain_date_time(actual_data, time_delta.year, time_delta.month, time_delta.day, time_delta.hour, time_delta.minute, 0)
            statistics_data = data_acquisition.count_statistics(res)

        elif "_" in weekday:
            rel_day = weekday

            if "today_" in rel_day:
                number_days_from_today = int(re.findall(r'[-+]?\d+', rel_day)[0])
                print(number_days_from_today)
                if number_days_from_today > 0: # Future (Approximation)
                    current_date = datetime.now().date()
                    next_day_date = current_date + timedelta(days=number_days_from_today)
                    next_weekday_idx = next_day_date.weekday()
                    next_weekday_str = await self.get_weekday_string(next_weekday_idx)
                    if time == "now": # unspecified time -> getting statistics in current time # TODO
                        res = data_acquisition.get_data_weekday_time(historical_data, next_weekday_str, [(datetime.now()).strftime('%H:%M:%S')])
                        statistics_data = data_acquisition.count_statistics(res)
                    elif re.match(time_regex, time):
                        res = data_acquisition.get_data_weekday_time(historical_data, next_weekday_str, [time])
                        statistics_data = data_acquisition.count_statistics(res)
                   
                elif number_days_from_today < 0: # Past (know exact statistics)
                    current_date = datetime.now().date()
                    previous_weekday_date = current_date - timedelta(days=abs(number_days_from_today))
                    print(previous_weekday_date)
                    day = previous_weekday_date.day
                    month = previous_weekday_date.month
                    year = previous_weekday_date.year
                    if time == "now": # TODO
                        res = data_acquisition.get_data_certain_date_time(historical_data, year, month, day, datetime.now().hour, datetime.now().minute, 0)
                        statistics_data = data_acquisition.count_statistics(res)
                    elif re.match(time_regex, time):
                        time_datetime = datetime.strptime(time, "%H:%M:%S")
                        res = data_acquisition.get_data_certain_date_time(historical_data, year, month, day, time_datetime.hour, time_datetime.minute, 0) 
                        statistics_data = data_acquisition.count_statistics(res)
            else:
                rel_weekday = weekday.split("_")[1] 
                previous_date = await self.get_date_previous_day(rel_weekday)
                day = previous_date.day
                month = previous_date.month
                year = previous_date.year
                print(day)
                print(month)
                print(year)
                if time == "now": # TODO
                    res = data_acquisition.get_data_certain_date_time(historical_data, year, month, day, datetime.now().hour, datetime.now().minute, 0)
                    statistics_data = data_acquisition.count_statistics(res)
                elif re.match(time_regex, time):
                    time_datetime = datetime.strptime(time, "%H:%M:%S")
                    res = data_acquisition.get_data_certain_date_time(historical_data, year, month, day, time_datetime.hour, time_datetime.minute, 0) 
                    statistics_data = data_acquisition.count_statistics(res)

        print(statistics_data)

        return statistics_data


    # Tells result to the user
    async def tell_data_according_to_query(self, data_frame: dict, statistics_data: tuple):
        time = data_frame["time"]
        statistics = data_frame["statistics"]
        parking_house = data_frame["parking_house"]
        weekday = data_frame["weekday"]

        time_regex = time_regex = r'^\d{2}:\d{2}:\d{2}$'
        todays_weekday = await self.get_todays_day()

        if time == "now" and weekday == todays_weekday: # Actual
            if statistics == "free_spaces":
                num_free_spaces = statistics_data[1]
                print(num_free_spaces)
                await self.synthesize_and_wait(text=("Aktuální počet volných míst v parkovacím domě {} činí {}.").format(parking_house, num_free_spaces))

            elif statistics == "occupied_spaces":
                num_occupied_spaces = statistics_data[0]
                await self.synthesize_and_wait(text=("Aktuální počet obsazených míst v parkovacím domě {} činí {}.").format(parking_house, num_occupied_spaces))

            elif statistics == "occupied_spaces_%":
                num_occupied_spaces_percent = statistics_data[2]
                await self.synthesize_and_wait(text=("Aktuálně je obsazeno v parkovacím domě {} {} procent parkovacích míst.").format(parking_house, num_occupied_spaces_percent))

            elif statistics == "free_spaces_%":
                num_free_spaces_percent = statistics_data[3]
                await self.synthesize_and_wait(text=("Aktuálně je volných v parkovacím domě {} {} procent parkovacích míst.").format(parking_house, num_free_spaces_percent))

            elif statistics == "capacity":
                capacity = statistics_data[0] + statistics_data[1]
                await self.synthesize_and_wait(text=("Maximální kapacita parkovacího domu {} je {} parkovacích míst.").format(parking_house, capacity))
            
        elif "rel_" in time: # Relative time based on actual data (Future)
            #relative_time_hours = re.findall(r'[-+]?\d*\.\d+|\d+', time)[0]
            relative_time_cz_str = translator.get_czech_text_time_day(time)
        
            if statistics == "free_spaces":
                num_free_spaces = statistics_data[1]
                await self.synthesize_and_wait(text=("Pravděpodobný počet volných míst v parkovacím domě {} {} je {}.").format(parking_house, relative_time_cz_str, num_free_spaces))

            elif statistics == "occupied_spaces":
                num_occupied_spaces = statistics_data[0]
                await self.synthesize_and_wait(text=("Pravděpodobný počet obsazených míst v parkovacím domě {} {} je {}.").format(parking_house, relative_time_cz_str, num_occupied_spaces))

            elif statistics == "occupied_spaces_%":
                num_occupied_spaces_percent = statistics_data[2]
                await self.synthesize_and_wait(text=("{} bude v parkovacím domě {} pravděpodobně obsazeno {} procent parkovacích míst.").format(relative_time_cz_str, parking_house, num_occupied_spaces_percent))

            elif statistics == "free_spaces_%":
                num_free_spaces_percent = statistics_data[3]
                await self.synthesize_and_wait(text=("{} bude v parkovacím domě {} pravděpodobně volných {} procent parkovacích míst.").format(relative_time_cz_str, parking_house, num_free_spaces_percent))

            elif statistics == "capacity":
                capacity = statistics_data[0] + statistics_data[1]
                await self.synthesize_and_wait(text=("Pravděpodobná maximální kapacita parkovacího domu {} {} je {} parkovacích míst.").format(parking_house, relative_time_cz_str, capacity))

        elif "rel-" in time: # Relative time based on actual data (Past)
            relative_time_cz_str = translator.get_czech_text_time_day(time)
            #relative_time_hours = re.findall(r'[-+]?\d*\.\d+|\d+', time)[0]
            if statistics == "free_spaces":
                num_free_spaces = statistics_data[1]
                await self.synthesize_and_wait(text=("Počet volných míst {} v parkovacím domě {} činil {} parkovacích míst.").format(relative_time_cz_str, parking_house, num_free_spaces))

            elif statistics == "occupied_spaces":
                num_occupied_spaces = statistics_data[0]
                await self.synthesize_and_wait(text=("Obsazenost parkovacího domu {} {} činila {} parkovacích míst.").format(parking_house, relative_time_cz_str, num_occupied_spaces))

            elif statistics == "occupied_spaces_%":
                num_occupied_spaces_percent = statistics_data[2]
                await self.synthesize_and_wait(text=("{} bylo v parkovacím domě {} obsazeno {} procent parkovacích míst.").format(relative_time_cz_str, parking_house, num_occupied_spaces_percent))

            elif statistics == "free_spaces_%":
                num_free_spaces_percent = statistics_data[3]
                await self.synthesize_and_wait(text=("{} bylo v parkovacím domě {} volných {} procent parkovacích míst.").format(relative_time_cz_str, parking_house, num_free_spaces_percent))

            elif statistics == "capacity":
                capacity = statistics_data[0] + statistics_data[1]
                await self.synthesize_and_wait(text=("Maximální kapacita parkovacího domu {} {} činila {} parkovacích míst.").format(parking_house, relative_time_cz_str, capacity))

        elif time == "now" and ("today_" in weekday or "last_" in weekday): # Undefined time, defined relative day
            if "today_" in weekday:
                number_days_from_today = int(re.findall(r'[-+]?\d+', weekday)[0])
            else:
                number_days_from_today = -10 # past in case of last Monday, Tuesday, etc.
            rel_day_cz_str = translator.get_czech_text_time_day(weekday)
            if number_days_from_today < 0: # Past
                if statistics == "free_spaces":
                    num_free_spaces = statistics_data[1]
                    await self.synthesize_and_wait(text=("Počet volných míst v parkovacím domě {} v tomto čase {} činil {} parkovacích míst.").format(parking_house, rel_day_cz_str, num_free_spaces))

                elif statistics == "occupied_spaces":
                    num_occupied_spaces = statistics_data[0]
                    await self.synthesize_and_wait(text=("Obsazenost parkovacího domu {} {} činila v tomto čase {} parkovacích míst.").format(parking_house, rel_day_cz_str, num_occupied_spaces))

                elif statistics == "occupied_spaces_%":
                    num_occupied_spaces_percent = statistics_data[2]
                    await self.synthesize_and_wait(text=("{} bylo v parkovacím domě {} v tomto čase obsazeno {} procent parkovacích míst.").format(rel_day_cz_str, parking_house, num_occupied_spaces_percent))

                elif statistics == "free_spaces_%":
                    num_free_spaces_percent = statistics_data[3]
                    await self.synthesize_and_wait(text=("{} bylo v parkovacím domě {} v tomto čase volných {} procent parkovacích míst.").format(rel_day_cz_str, parking_house, num_free_spaces_percent))

                elif statistics == "capacity":
                    capacity = statistics_data[0] + statistics_data[1]
                    await self.synthesize_and_wait(text=("Maximální kapacita parkovacího domu {} {} v tomto čase činila {} parkovacích míst.").format(parking_house, rel_day_cz_str, capacity))
        
            elif number_days_from_today >= 1: # Future
                if statistics == "free_spaces":
                    num_free_spaces = statistics_data[1]
                    await self.synthesize_and_wait(text=("{} bude pravděpodobně v tomto čase v parkovacím domě {} volných {} parkovacích míst.").format(rel_day_cz_str, parking_house, num_free_spaces))

                elif statistics == "occupied_spaces":
                    num_occupied_spaces = statistics_data[0]
                    await self.synthesize_and_wait(text=("{} bude pravděpodobně v tomto čase v parkovacím domě {} obsazených {} parkovacích míst.").format(rel_day_cz_str, parking_house, num_occupied_spaces))

                elif statistics == "occupied_spaces_%":
                    num_occupied_spaces_percent = statistics_data[2]
                    await self.synthesize_and_wait(text=("{} v tomto čase bude v parkovacím domě {} obsazeno pravděpodobně {} procent parkovacích míst.").format(rel_day_cz_str, parking_house, num_occupied_spaces_percent))

                elif statistics == "free_spaces_%":
                    num_free_spaces_percent = statistics_data[3]
                    await self.synthesize_and_wait(text=("{} v tomto čase bude v parkovacím domě {} pravděpodobně {} procent volných parkovacích míst.").format(rel_day_cz_str, parking_house, num_free_spaces_percent))

                elif statistics == "capacity":
                    capacity = statistics_data[0] + statistics_data[1]
                    await self.synthesize_and_wait(text=("Maximální kapacita parkovacího domu {} bude v tomto čase {} činit {} parkovacích míst.").format(parking_house, rel_day_cz_str, capacity))
        
        elif re.match(time_regex, time) and "today_" in weekday or "last_" in weekday: # Defined time, defined relative day
            if "today_" in weekday:
                number_days_from_today = int(re.findall(r'[-+]?\d+', weekday)[0])
            else:
                number_days_from_today = -10
            rel_day_cz_str = translator.get_czech_text_time_day(weekday)
            time_cz_str = translator.get_czech_text_time_day(time)

            if number_days_from_today < 0: # Past
                if statistics == "free_spaces":
                    num_free_spaces = statistics_data[1]
                    await self.synthesize_and_wait(text=("Počet volných míst v parkovacím domě {} {} {} činil {} parkovacích míst.").format(parking_house, rel_day_cz_str, time_cz_str, num_free_spaces))

                elif statistics == "occupied_spaces":
                    num_occupied_spaces = statistics_data[0]
                    await self.synthesize_and_wait(text=("Obsazenost parkovacího domu {} {} {} činila {} parkovacích míst.").format(parking_house, rel_day_cz_str, time_cz_str, num_occupied_spaces))

                elif statistics == "occupied_spaces_%":
                    num_occupied_spaces_percent = statistics_data[2]
                    await self.synthesize_and_wait(text=("{} {} bylo v parkovacím domě {} obsazeno {} procent parkovacích míst.").format(rel_day_cz_str, time_cz_str, parking_house, num_occupied_spaces_percent))

                elif statistics == "free_spaces_%":
                    num_free_spaces_percent = statistics_data[3]
                    await self.synthesize_and_wait(text=("{} {} bylo v parkovacím domě {} volných {} procent parkovacích míst.").format(rel_day_cz_str, time_cz_str, parking_house, num_free_spaces_percent))

                elif statistics == "capacity":
                    capacity = statistics_data[0] + statistics_data[1]
                    await self.synthesize_and_wait(text=("Maximální kapacita parkovacího domu {} {} {} činila {} parkovacích míst.").format(parking_house, rel_day_cz_str, time_cz_str, capacity))
        
            elif number_days_from_today >= 1: # Future
                if statistics == "free_spaces":
                    num_free_spaces = statistics_data[1]
                    await self.synthesize_and_wait(text=("{} {} bude pravděpodobně v parkovacím domě {} volných {} parkovacích míst.").format(rel_day_cz_str, time_cz_str, parking_house, num_free_spaces))

                elif statistics == "occupied_spaces":
                    num_occupied_spaces = statistics_data[0]
                    await self.synthesize_and_wait(text=("{} {} bude pravděpodobně v parkovacím domě {} obsazených {} parkovacích míst.").format(rel_day_cz_str, time_cz_str, parking_house, num_occupied_spaces))

                elif statistics == "occupied_spaces_%":
                    num_occupied_spaces_percent = statistics_data[2]
                    await self.synthesize_and_wait(text=("{} {} bude v parkovacím domě {} obsazeno pravděpodobně {} procent parkovacích míst.").format(rel_day_cz_str, time_cz_str, parking_house, num_occupied_spaces_percent))

                elif statistics == "free_spaces_%":
                    num_free_spaces_percent = statistics_data[3]
                    await self.synthesize_and_wait(text=("{} {} bude v parkovacím domě {} pravděpodobně {} procent volných parkovacích míst.").format(rel_day_cz_str, time_cz_str, parking_house, num_free_spaces_percent))

                elif statistics == "capacity":
                    capacity = statistics_data[0] + statistics_data[1]
                    await self.synthesize_and_wait(text=("Maximální kapacita parkovacího domu {} bude {} {} činit {} parkovacích míst.").format(parking_house, rel_day_cz_str, time_cz_str, capacity))
        

        else: # Defined time and weekday
            time_cz_str = translator.get_czech_text_time_day(time)
            weekday_cz_str = translator.get_czech_text_time_day(weekday)

            if statistics == "free_spaces":
                num_free_spaces = statistics_data[1]
                await self.synthesize_and_wait(text=("Obvyklý počet volných míst v parkovacím domě {} {} {} činí {} parkovacích míst.").format(parking_house, weekday_cz_str, time_cz_str, num_free_spaces))

            elif statistics == "occupied_spaces":
                num_occupied_spaces = statistics_data[0]
                await self.synthesize_and_wait(text=("Obvyklý počet obsazených míst v parkovacím domě {} ve dni {} {} činí {} parkovacích míst.").format(parking_house, weekday_cz_str, time_cz_str, num_occupied_spaces))

            elif statistics == "occupied_spaces_%":
                num_occupied_spaces_percent = statistics_data[2]
                await self.synthesize_and_wait(text=("Obvykle je v parkovacím domě {} ve dni {} {} obsazeno {} procent parkovacích míst.").format(parking_house, weekday_cz_str, time_cz_str, num_occupied_spaces_percent))

            elif statistics == "free_spaces_%":
                num_free_spaces_percent = statistics_data[3]
                await self.synthesize_and_wait(text=("Obvykle je v parkovacím domě {} ve dni {} {} obsazeno {} procent parkovacích míst.").format(parking_house, weekday_cz_str, time_cz_str, num_free_spaces_percent))

            elif statistics == "capacity":
                capacity = statistics_data[0] + statistics_data[1]
                await self.synthesize_and_wait(text=("Obvyklá maximálná kapacita parkovacího domu {} ve dni {} {} činí {} parkovacích míst.").format(parking_house, weekday_cz_str, time_cz_str, capacity))


    # Getting the frame dictionary for YES/NO questions
    async def get_frame_dict_yes_no_questions(self, result):
        recognized_entities = result.entity_types
        frame_dict = {"parking_house": "", # Frame dictionary inicialization
                      "time": "now", 
                      "weekday": await self.get_todays_day(), 
                      "statistics": ""}
        
        status = result.yes_no_questions.first

        if status == "available":
            frame_dict["statistics"] = "free_spaces"

        else:
            frame_dict["statistics"] = "occupied_spaces"

        idx = 0
        if "parking_house" not in recognized_entities:
            while idx < 4:
                await self.synthesize_and_wait(text=f"Který parkovací dům myslíte?")
                result = await self.recognize_and_wait_for_slu_result(timeout=10.)
                recognized_entities = result.entity_types
                if "parking_house" in recognized_entities:
                    frame_dict["parking_house"] = result.parking_house.first
                    break
                else: 
                    idx += 1
        else:
            frame_dict["parking_house"] = result.parking_house.first
    
        if (await self.check_frame_complete(frame_dict))[0] == False:
            await self.synthesize_and_wait(text=f"Nebyl specifikován parkovací dům. Nelze zjistit aktuální stav.")
            return None
        
        else:
            return frame_dict


    # Getting actual data
    async def get_actual_data(self, frame_dict_yes_no: dict, data):
        parking_house = frame_dict_yes_no["parking_house"]

        if parking_house == "Nové divadlo":
            data_idx = 0
        else:
            data_idx = 1

        actual_data = data[data_idx + 2]
        statistics_data = data_acquisition.get_actual_info(actual_data)

        return statistics_data
        

    # Tells the result of YES/NO question to the user
    async def tell_data_according_to_yes_no_questions(self, frame_dict_yes_no: dict, statistics_data):
        parking_house = frame_dict_yes_no["parking_house"]
        statistics = frame_dict_yes_no["statistics"]

        if statistics == "free_spaces":
            num_free_spaces = statistics_data[1]
            if num_free_spaces > 0:
                await self.synthesize_and_wait(text=("Ano, v parkovacím domě {} jsou ještě volná místa. Zbývá jich {}.").format(parking_house, num_free_spaces))
            else:
                 await self.synthesize_and_wait(text=("Ne, v parkovacím domě {} už bohužel nejsou žádná volná místa.").format(parking_house))

        elif statistics == "occupied_spaces":
            num_free_spaces = statistics_data[1]
            if num_free_spaces == 0:
                await self.synthesize_and_wait(text=("Ano, v parkovacím domě {} jsou všechna místa obsazená.").format(parking_house))
            else:
                await self.synthesize_and_wait(text=("Ne, v parkovacím domě {} ještě nejsou všechna místa obsazena. Volných míst zbývá ještě {}.").format(parking_house, num_free_spaces))


    # Updating frame dictionary, if user wants to continue in a dialog
    async def update_frame_dictionary(self, frame_dict: dict, result):
        recognized_entities = result.entity_types
        
        original_frame_dict = frame_dict.copy()
        
        if "parking_house" in recognized_entities:
            parking_house = result.parking_house.first
            frame_dict["parking_house"] = parking_house

        if "time" in recognized_entities:
            time = result.time.first
            frame_dict["time"] = time

            #if frame_dict["time"] in relative_times_list:
            #    frame_dict["weekday"] = await self.get_todays_day()

        if "weekday" in recognized_entities:
            weekday = result.weekday.first
            frame_dict["weekday"] = weekday

        if "statistics" in recognized_entities:
            statistics = result.statistics.first
            frame_dict["statistics"] = statistics

        if original_frame_dict == frame_dict:
            await self.synthesize_and_wait(text=("Vstupní informace zůstaly beze změn."))

        return frame_dict


    # Updating YES/NO frame dictionary, if user wants to continue in a dialog
    async def update_yes_no_frame_dictionary(self, frame_dict: dict, result):
        recognized_entities = result.entity_types
        original_frame_dict = frame_dict.copy()
        
        status = result.yes_no_questions.first
        
        if "parking_house" in recognized_entities:
            frame_dict["parking_house"] = result.parking_house.first

        if "status" in recognized_entities:
             if status == "available":
                frame_dict["statistics"] = "free_spaces"

             else:
                frame_dict["statistics"] = "occupied_spaces"

        if original_frame_dict == frame_dict:
            await self.synthesize_and_wait(text=("Vstupní informace zůstaly beze změn."))

        print(original_frame_dict)
        print(frame_dict)
        return frame_dict


    # Spoken language understanding
    async def slu(self, data: tuple):
        grammars = await self.prepare_grammars()
        await self.define_slu_grammars(grammars)

        num_iterations = 0
        temp_yes_no_quest = False
        temp_quest = False

        while True:
            result = []
            if num_iterations == 0:
                frame_dict = {}
                frame_dict_yes_no_quest = {}
                await self.synthesize_and_wait(text="Prosím, řekněte svůj požadavek.")
            else: 
                await self.synthesize_and_wait(text="Prosím, opět řekněte svůj požadavek.")

            result = await self.recognize_and_wait_for_slu_result(timeout=10.)

            if result.command:

                command = result.command

                if "end" in command:
                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz konec, ukončuji dialog. Přeji hezký zbytek dne.")
                    break

                elif "bye" in command:
                    await self.synthesize_and_wait(text=f"Konec dialogu a nashledanou. Přeji hezký zbutek dne.")
                    break

                elif "continue" in command:
                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz pokračovat, pokračuji v dialogu.")
                    num_iterations += 1
                    continue

                elif "help" in command:
                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz nápověda. Řekněte prosím alespoň jednu z následujících informací: den v týdnu, čas, parkovací dům (Rychtářka nebo Nové divadlo) nebo statistika, která vás zajímá.")
                    continue

            elif len(result.entity_types) == 0:
                await self.synthesize_and_wait(text=f"Nebyly zaznamenány žádné informace, zkuste to prosím znovu.")
                continue

            elif ("yes_no_questions" in result.entity_types) or (temp_yes_no_quest == True and temp_quest == False):
                if num_iterations == 0:
                    frame_dict_yes_no_quest = await self.get_frame_dict_yes_no_questions(result)
                    temp_yes_no_quest = True
                    #print(temp_yes_no_quest)
                    #print(temp_quest)
                else:
                    frame_dict_yes_no_quest = await self.update_yes_no_frame_dictionary(frame_dict_yes_no_quest, result)
                num_iterations += 1
                actual_data = await self.get_actual_data(frame_dict_yes_no_quest, data)
                await self.tell_data_according_to_yes_no_questions(frame_dict_yes_no_quest, actual_data)

            elif ("yes_no_questions" not in result.entity_types) or (temp_quest == True and temp_yes_no_quest == False):
                if num_iterations == 0:
                    frame_dict = await self.get_frame_dictionary(result)
                    temp_quest = True
                else:
                    frame_dict = await self.update_frame_dictionary(frame_dict, result)
                num_iterations += 1
                if frame_dict == None:
                    continue
                missing_info = await self.determine_missing_info(frame_dict)
                if len(missing_info) > 0:
                    complete_info = await self.tell_missing_info(missing_info, frame_dict)
                    print(complete_info)
                print(frame_dict)
                statistics_data = await self.process_data(frame_dict, data) # Zjisteni statistiky
                await self.tell_data_according_to_query(frame_dict, statistics_data) # Oznameni dat uzivateli

            await self.synthesize_and_wait(text=f"Mohu pro Vás ještě něco udělat?")
            res = await self.recognize_and_wait_for_slu_result(timeout=10.)
    
            if res.confirm.first:
                continue
            elif res.not_confirm.first:
                await self.synthesize_and_wait(text=f"Ukončuji dialog. Přeji hezký zbytek dne.")
                break
            else: 
                await self.synthesize_and_wait(text=f"Nebyl zaznamenán žádný příkaz. Ukončuji dialog. Přeji hezký zbytek dne.")
                break


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)-10s %(message)s',level=logging.DEBUG)

    SpeechCloudWS.run(ParkingHouseDialog, 
                      address="0.0.0.0", 
                      port=8888)
