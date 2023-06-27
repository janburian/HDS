from dialog import SpeechCloudWS, Dialog
import logging
from pathlib import Path
from datetime import datetime, timedelta
import data_acquisition
import os
import re
import math
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


    async def get_data(self):
        # Historical
        historical_data_nove_divadlo = data_acquisition.load_historical_data(Path('./data/data-pd-novedivadlo.csv'))
        historical_data_rychtarka = data_acquisition.load_historical_data(Path('./data/data-pd-rychtarka.csv'))
        
        # Actual 
        url_nove_divadlo = 'https://onlinedata.plzen.eu/data-pd-novedivadlo-actual.php'
        url_rychtarka = 'https://onlinedata.plzen.eu/data-pd-rychtarka-actual.php'

        actual_data_nove_divadlo = data_acquisition.get_actual_data(url_nove_divadlo)
        actual_data_rychtarka = data_acquisition.get_actual_data(url_rychtarka)

        return historical_data_nove_divadlo, historical_data_rychtarka, actual_data_nove_divadlo, actual_data_rychtarka


    async def prepare_grammars(self):
        grammars = self.grammar_from_dict("command", {
                "end": {"konec","skonči","ukončit"}, 
                "continue": {"pokračuj", "pokračovat", "další"},
                "help": {"nápověda", "pomoc", "help", "jsem ztracen"}}) 
        
        grammars += self.grammar_from_dict("confirm", 
                {"confirm":{"potvrzuji", "potvrzuju", "potvrzuje", "přesně tak", "ano"}})

        grammars += self.grammar_from_dict("not_confirm", 
                {"not_confirm":{"nepotvrzuji", "nepotvrzuju", "nepotvrzuje", "ne"}})

        grammars += self.grammar_from_dict("change", 
                {"change":{"změnit", "změnil", "a v"}})

        grammars += self.grammar_from_dict("parking_houses", {
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
                "tomorrow":{"zítra", "další den", "následující den", "v dalším dni", "v následujícím dni"}, 
                "day_after_tomorrow":{"pozítří"},
                "day_before_yesterday":{"předevčírem"},
                "yesterday":{"včera", "předchozí den", " v předchozím dni"},
                "last_monday":{"minulé pondělí"},
                "last_tuesday":{"minulé úterý"},
                "last_wednesday":{"minulou středu"},
                "last_thursday":{"minulý čtvrtek"},
                "last_friday":{"minulý pátek"},
                "last_saturday":{"minulou sobotu"},
                "last_sunday":{"minulou neděli"}
                })
        
        grammars += self.grammar_from_dict("time", {
                "now": {"aktuálně", "aktuální", "právě teď", "nyní", "v tento čas", "teď", "v současné době", "současná doba", "v tomto čase"}, 
                "01:00:00": {"v jednu ráno", "jedna ráno", "v jednu ráno", "jedna ráno", "v jedna nula nula", "v jednu nula nula"},
                "01:30:00": {"v jednu třicet ráno", "jedna třicet ráno", "v jedna třicet", "v jednu třicet", "půl druhé ráno"},
                "02:00:00": {"ve dvě ráno", "ve dvě nula nula", "dvě ráno", "dvě hodiny ráno"},
                "02:30:00": {"ve dvě třicet ráno", "ve dvě třicet", "půl třetí ráno"},
                "03:00:00": {"ve tři ráno", "tři hodiny ráno", "ve tři nula nula"},
                "03:30:00": {"ve tři třicet ráno", "ve tři třicet", "půl čtvrté ráno"},
                "04:00:00": {"ve čtyři ráno", "ve čtyři hodiny ráno", "ve čtyři nula nula"},
                "04:30:00": {"ve čtyři třicet ráno", "ve čtyři třicet", "půl páté ráno"},
                "05:00:00": {"v pět ráno", "pět ráno", "pět hodin ráno", "v pět nula nula"},
                "05:30:00": {"v pět třicet ráno", "pět třicet ráno", "půl šesté ráno"},
                "06:00:00": {"v šest ráno", "šest ráno", "šest hodin ráno", "v šest nula nula"},
                "06:30:00": {"v šest třicet ráno", "šest třicet ráno", "v šest třicet", "šest třicet", "půl sedmé ráno"},
                "07:00:00": {"sedm ráno", "sedm hodin ráno", "v sedm ráno", "sedm", "v sedm"},
                "07:30:00": {"sedm třicet", "půl osmé ráno", "o půl osmé ráno", "sedm třicet ráno", "v sedm třicet ráno"},
                "08:00:00": {"v osm ráno", "osm ráno", "osm hodin ráno", "v osm nula nula", "osm nula nula"},
                "08:30:00": {"osm třicet ráno", "v osm třicet ráno", "půl deváté ráno", "v půl deváté ráno", "o půl deváté ráno"},
                "09:00:00": {"devět ráno", "v devět ráno", "v devět hodin ráno",  "devět nula nula ráno", "v devět nula nula"},
                "09:30:00": {"devět třicet ráno", "v devět třicet ráno", "půl desátá ráno", "v půl desáté ráno"},
                "10:00:00": {"deset ráno", "deset hodin ráno", "deset nula nula ráno", "v deset nula nula ráno", "v deset ráno"},
                "10:30:00": {"deset třicet ráno", "v deset třicet ráno", "v půl jedenácté ráno", "půl jedenáctá ráno"},
                "11:00:00": {"jedenáct ráno", "jedenáct hodin ráno", "jedenáct ráno", "jedenáct nula nula ráno", "jedenáct nula nula ráno"},
                "11:30:00": {"jedenáct třicet ráno", "v jedenáct třicet ráno", "v půl dvanácté ráno", "o půl dvanácté ráno"},
                "12:00:00": {"poledne", "v poledne", "o poledni", "dvanáct nula nula", "dvanáct hodin v poledne"},
                "12:30:00": {"dvanáct třicet", "dvanáct třicet odpoledne", "ve dvanáct třicet", "v půl jedné odpoledne"},
                "13:00:00": {"třináct", "třináct hodin", "třináct nula nula", "ve třináct", "ve třináct nula nula", "v jednu odpoledne"},
                "13:30:00": {"ve třináct třicet", "třináct třicet", "půl druhé odpoledne"},
                "14:00:00": {"čtrnáct nula nula", "čtrnáct", "čtrnáct hodin", "ve dvě odpoledne", "dvě odpoledne", "ve čtrnáct"},
                "14:30:00": {"čtrnáct třicet", "ve čtrnáct třicet", "v půl třetí odpoledne", "půl třetí odpoledne"},
                "15:00:00": {"v patnáct nula nula", "patnáct hodin", "ve tři odpoledne", "v patnáct"},
                "15:30:00": {"v patnáct třicet", "patnáct třicet", "půl čtvrté odpoledne", "v půl čtvrté odpoledne"},
                "16:00:00": {"šestnáct nula nula", "v šestnáct nula nula", "v šestnáct", "v šestnáct hodin", "ve čtyři hodiny odpoledne", "čtyři hodiny odpoledne"},
                "16:30:00": {"šestnáct třicet", "v šestnáct třicet", "v půl páté odpoledne", "o půl páté odpoledne"},
                "17:00:00": {"sedmnáct nula nula", "v sedmnáct nula nula", "sedmnáct hodin", "pět hodin odpoledne", "v pět hodin odpoledne"},
                "17:30:00": {"sedmnáct třicet", "v sedmnáct třicet", "v půl šesté odpoledne", "v půl šesté večer", "o půl šesté večer"},
                "18:00:00": {"osmnáct", "osmnáct nula nula", "šest večer", "osmnáct hodin"},
                "18:30:00": {"osmnáct třicet", "o půl sedmé večer", "půl sedmá večer"},
                "19:00:00": {"devatenáct nula nula", "sedm večer", "devatenáct hodin", "sedm hodin večer"},
                "19:30:00": {"devatenáct třicet", "půl osmá večer", "v půl osmé večer", "sedm třicet večer"},
                "20:00:00": {"dvacet nula nula", "osm večer", "ve dvacet hodin", "osm hodin večer", "osmá večerní"},
                "20:30:00": {"dvacet třicet", "půl devátá večer", "o půl deváté večer", "v půl deváté večer"},
                "21:00:00": {"dvacet jedna nula nula", "devět hodin večer", "dvacet jedna hodin"},
                "21:30:00": {"dvacet jedna třicet", "půl desátá večer", "o půl desáté večer", "v půl desátý večer"},
                "22:00:00": {"dvacet dva nula nula", "ve dvacet dva hodin", "v deset hodin večer"},
                "22:30:00": {"dvacet dva třicet", "půl jedenáctá večer", "o půl jedenácté večer", "v půl jedenácté večer", "půl jedenáctá večerní"},
                "23:00:00": {"dvacet tři nula nula", "jedenáct večer", "jedenáct hodin večer"},
                "23:30:00": {"dvacet tři třicet", "o půl dvanácté večer", "v půl dvanácté večer"},
                "00:00:00": {"dvacet čtyři nula nula", "půlnoc", "o půlnoci", "nula nula nula nula"}, 
                "00:30:00": {"nula třicet", "o půl jedné v noci", "o půl jedné ráno", "v půl jedné v noci", "v půl jedné ráno"}, 
                "rel_1_hour": {"za hodinu", "za jednu hodinu"}, 
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
                "occupied_spaces": {"počet obsazených míst", "obsazená místa", "zaplněnost", "obsazená", "zaplněná", "obsazenost", "aktuální počet aut", "obsazeno"},
                "capacity": {"kapacita", "kapacitou", "maximální kapacita", "celkový počet míst"},
                "occupied_spaces_%": {"obsazená místa %", "obsazenost %", "zaplněná kapacita %"},
                })
        
        grammars += self.grammar_from_dict("yes_no_questions", {
                "available": {"jsou volná místa", "jsou dostupná", "je volno", "je místo", "je k dispozici", "vejdu se do", "je ještě místo"},
                "nonavailable": {"je plno", "je narváno"}
                })
        
        return grammars
    

    async def get_frame_dictionary(self, result: list):
        relative_times_list = ["now", "rel_1_hour", "rel_2_hours", "rel_3_hours", "rel_4_hours", "rel_5_hours", "rel_6_hours", "rel_7_hours", "rel_8_hours",
                "rel_9_hours", "rel_10_hours", "rel_11_hours", "rel_12_hours", "rel-0.5-hour", "rel-1-hour", "rel-1.5-hours", "rel-2-hours"]
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        recognized_entities = result.entity_types
        frame_dict = {"parking_house": "", 
                      "time": "", 
                      "weekday": "", 
                      "statistics": ""}
                             
        if len(recognized_entities) == 0:
            await self.synthesize_and_wait(text=f"Nebyla rozpoznána žádná informace.")
            return None
        
        if "parking_houses" in recognized_entities:
            parking_house = result.parking_houses.first
            frame_dict["parking_house"] = parking_house

        if "time" in recognized_entities:
            time = result.time.first
            frame_dict["time"] = time

            if frame_dict["time"] in relative_times_list:
                dt_now = datetime.now()
                weekday_idx = dt_now.weekday()
                print(weekday_idx)
                frame_dict["weekday"] = weekdays[weekday_idx]

        if "weekday" in recognized_entities:
            weekday = result.weekday.first
            frame_dict["weekday"] = weekday

        if "statistics" in recognized_entities:
            statistics = result.statistics.first
            frame_dict["statistics"] = statistics

        return frame_dict
    
    
    async def determine_missing_info(self, data_frame: dict):
        missing_info = []
        for key in data_frame:
            if data_frame[key] == "":
                missing_info.append(key)
        
        return missing_info
    

    # Function to convert
    async def listToString(self, s):
    
        # initialize an empty string
        str1 = " "
    
        # return string
        return (str1.join(s))


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
            await self.synthesize_and_wait(text=await self.listToString(missing_entities_text_list))
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
                    

    async def check_frame_complete(self, data_frame: dict):
        num_missing_entities = 0
        missing_entities = []
        relative_times_list = ["now", "rel_1_hour", "rel_2_hours", "rel_3_hours", "rel_4_hours", "rel_5_hours", "rel_6_hours", "rel_7_hours", "rel_8_hours",
                "rel_9_hours", "rel_10_hours", "rel_11_hours", "rel_12_hours", "rel-0.5-hour", "rel-1-hour", "rel-1.5-hours", "rel-2-hours"]

        for key in data_frame:
            if data_frame[key] == "":
                if data_frame["time"] in relative_times_list:
                    data_frame["weekday"] = "Today"
                else:
                    num_missing_entities += 1
                    missing_entities.append(key)
            
        if num_missing_entities == 0:
            return True, []
        else:
            return False, missing_entities
        

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
        statistics_data = []

        if re.match(time_regex, time): # Historical data
            res = data_acquisition.get_data_weekday_time(historical_data, weekday, [time])
            statistics_data = data_acquisition.count_statistics(res)

        elif time == "now": # Actual
            statistics_data = data_acquisition.get_actual_info(actual_data)

        elif "rel_" in time: # Future (based on historical data) - approximation
            relative_time_hours = re.findall(r'\d+', time)[0]
            time_delta = (datetime.now() + timedelta(hours=int(relative_time_hours))).strftime('%H:%M:%S')

            res = data_acquisition.get_data_weekday_time(historical_data, weekday, [time_delta])
            statistics_data = data_acquisition.count_statistics(res)

        elif "rel-" in time: # Past (based on actual data) - approximation # TODO
            relative_time_hours = re.findall(r'[-+]?\d*\.\d+|\d+', time)[0]
            time_delta = (datetime.now() - timedelta(hours=int(relative_time_hours))).strftime('%H:%M:%S')

        print(statistics_data)

        return statistics_data


    async def tell_data_according_to_query(self, data_frame: dict, statistics_data: tuple):
        time = data_frame["time"]
        statistics = data_frame["statistics"]
        parking_house = data_frame["parking_house"]
        weekday = data_frame["weekday"]

        if time == "now":
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
            
        elif "rel_" in time:
            #relative_time_hours = re.findall(r'[-+]?\d*\.\d+|\d+', time)[0]
            relative_time_cz_str = translator.get_czech_text_time_day(time)
        
            if statistics == "free_spaces":
                num_free_spaces = statistics_data[1]
                await self.synthesize_and_wait(text=("Pravděpodobný počet volných míst v parkovacím domě {} {} je {}.").format(parking_house, relative_time_cz_str, num_free_spaces))

            elif statistics == "occupied_spaces":
                num_occupied_spaces = statistics_data[0]
                await self.synthesize_and_wait(text=("Pravděpodobný počet obsazených míst v parkovacím domě {} za {} je {}.").format(parking_house, relative_time_cz_str, num_occupied_spaces))

            elif statistics == "occupied_spaces_%":
                num_occupied_spaces_percent = statistics_data[2]
                await self.synthesize_and_wait(text=("{} bude v parkovacím domě {} pravděpodobně obsazeno {} procent parkovacích míst.").format(relative_time_cz_str, parking_house, num_occupied_spaces_percent))

            elif statistics == "free_spaces_%":
                num_free_spaces_percent = statistics_data[3]
                await self.synthesize_and_wait(text=("{} bude v parkovacím domě {} pravděpodobně volných {} procent parkovacích míst.").format(relative_time_cz_str, parking_house, num_free_spaces_percent))

            elif statistics == "capacity":
                capacity = statistics_data[0] + statistics_data[1]
                await self.synthesize_and_wait(text=("Pravděpodobná maximální kapacita parkovacího domu {} {} je {} parkovacích míst.").format(parking_house, relative_time_cz_str, capacity))

        elif "rel-" in time:
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

        else: 
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


    async def change_state(self):
        pass


    async def slu(self, data: tuple):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        grammars = await self.prepare_grammars()
        await self.define_slu_grammars(grammars)
        end = False

        while True:
            await self.synthesize_and_wait(text="Prosím, řekněte svůj požadavek.")
            result = await self.recognize_and_wait_for_slu_result(timeout=10.)

            if result.command:

                command = result.command

                if "end" in command:
                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz konec, ukončuji dialog. Přeji hezký zbytek dne.")
                    break

                elif "continue" in command:
                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz pokračovat, pokračuji v dialogu.")
                    continue

                elif "help" in command:
                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz nápověda. Řekněte prosím alespoň jednu z následujících informací: den v týdnu, čas, parkovací dům (Rychtářka nebo Nové divadlo) nebo statistika, která vás zajímá.")
                    continue

            else:
                if "yes_no_questions" not in result.entity_types:
                    frame_dict = await self.get_frame_dictionary(result)
                    if frame_dict == None:
                        continue
                    missing_info = await self.determine_missing_info(frame_dict)
                    if len(missing_info) >= 1:
                        complete_info = await self.tell_missing_info(missing_info, frame_dict)
                        print(complete_info)
                    print(frame_dict)
                    statistics_data = await self.process_data(frame_dict, data) # Zjisteni statistiky
                    await self.tell_data_according_to_query(frame_dict, statistics_data) # Oznameni dat uzivateli



    if __name__ == '__main__':
        logging.basicConfig(format='%(asctime)s %(levelname)-10s %(message)s',level=logging.DEBUG)

        SpeechCloudWS.run(ParkingHouseDialog, 
                        address="0.0.0.0", 
                        port=8888)
