def get_times(hours, minutes):
    f = open("times_output.txt", 'w', encoding='utf-8')
    for hour in hours:
        f.write(hour + "\n")
        for minute in minutes:
            time = hour + " " + minute
            f.write(time + "\n")
    f.close()

def get_relative_times(hours_relative):
    f = open("rel_times_output.txt", 'w', encoding='utf-8')

    hours_1 = hours_relative[0]
    hours_2 = hours_relative[1:4]
    hours_3 = hours_relative[4:]

    for hour in hours_relative:
        if hour in hours_1:
            time = hour + " " + "hodinu"
            f.write(time + '\n')
        elif hour in hours_2:
            time = hour + " " + "hodiny"
            f.write(time + '\n')
        elif hour in hours_3:
            time = hour + " " + "hodin"
            f.write(time + '\n')

    f.close()


hours = ["jedna", "jednu", "dvě", "tři", "čtyři", "pět", "šest", "sedm", "osm", "devět", "deset", "jedenáct", "dvanáct",
         "třináct", "čtrnáct", "patnáct", "šestnáct", "sedmnáct", "osmnáct", "devatenáct", "dvacet", "dvacet jedna",
         "dvacet dva", "dvacet tři"]

minutes = ["pět", "nula pět", "deset", "patnáct", "dvacet", "dvacet pět", "třicet",
           "třicet pět", "čtyřicet", "čtyřicet pět", "padesát", "padesát pět"]

hours_relative = ["jednu", "dvě", "tři", "čtyři", "pět", "šest", "sedm", "osm", "devět", "deset", "jedenáct", "dvanáct",
         "třináct", "čtrnáct", "patnáct", "šestnáct", "sedmnáct", "osmnáct", "devatenáct", "dvacet", "dvacet jedna",
         "dvacet dva", "dvacet tři"]


get_times(hours, minutes)
get_relative_times(hours_relative)