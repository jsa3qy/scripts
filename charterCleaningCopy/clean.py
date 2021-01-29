import copy
import sys

class Entity:
    def __init__(self, id, city, state, entitytype):
        self.entityid = id
        self.city = city
        self.state = state
        self.type = entitytype

    def toString(self):
        print("id: " + self.entityid)
        print("city: " + self.city)
        print("state: " + self.state)
        print("entityType: " + self.type)

class Bucket:
    def __init__(self):
        self.locations = []
        self.packages = []
        self.tvs = []
        self.internets = []
    
    def addEntity(self, eType, entity):
        if eType == "Location":
            self.locations.append(entity)
        elif eType == "Package":
            self.packages.append(entity)
        elif eType == "TV":
            self.tvs.append(entity)
        elif eType == "Internet City/State":
            self.internets.append(entity)
        else:
            print('oops')
    
    def toString(self):
        print("locations: ")
        for location in self.locations:
            print(location.entityid)
        print("packages: ")
        for package in self.packages:
            print(package.entityid)
        print("tvs: ")
        for tv in self.tvs:
            print(tv.entityid)
        print("internets: ")
        for internet in self.internets:
            print(internet.entityid)

inv_map = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

def csvConvert(city, state, entity):
    tmpString = ""
    tmpString += city + "," + state + ",\"["
    for index,loc in enumerate(entity.locations):
        tmpString+=loc.entityid
        if index != len(entity.locations) -1:
            tmpString += ","
    tmpString+="]\",\"["
    for index,pac in enumerate(entity.packages):
        tmpString+=pac.entityid
        if index != len(entity.packages) -1:
            tmpString += ","
    tmpString+="]\",\"["
    for index,inte in enumerate(entity.internets):
        tmpString+=inte.entityid
        if index != len(entity.internets) -1:
            tmpString += ","
    tmpString+="]\",\"["
    for index,tv in enumerate(entity.tvs):
        tmpString+=tv.entityid
        if index != len(entity.tvs) -1:
            tmpString += ","
    tmpString+="]\""
    print(tmpString)

us_state_abbrev = {v: k for k, v in inv_map.iteritems()}

myFile = open("spectrum_csv.csv")
theMap = {}
entities = []
listOfCities = []
for index,line in enumerate(myFile):
    if index == 0:
        continue
    line = line.replace("\"\"", "null")
    line = line.replace("\"", "")
    curLine = line.split(',')
    entityid = curLine[1]
    entitytype = curLine[2]
    city = curLine[3] if (curLine[3] != "null") else curLine[5]
    state = us_state_abbrev[curLine[4]] if (curLine[4] != "null") else curLine[6]
    newEntity = Entity(entityid, city.strip(), state.strip(), entitytype.strip())
    entities.append(copy.deepcopy(newEntity))
    listOfCities.append(city.strip() + " " + state.strip())

cities = sorted(list(dict.fromkeys(listOfCities)))

print(len(entities))
for entity in entities:
    curVal = theMap.get(entity.city + " " + entity.state)
    if not curVal:
        theMap[entity.city + " " + entity.state] = Bucket()
        theMap[entity.city + " " + entity.state].addEntity(entity.type, copy.deepcopy(entity))
    else:
        theMap[entity.city + " " + entity.state].addEntity(entity.type, copy.deepcopy(entity))

print(len(theMap))
sys.stdout = open("output.csv","w") 
i = 0
print('City,State,Locations,Packages,Internets,TVs')
for key in theMap:
    if not len(theMap[key].locations) and (len(theMap[key].packages) and len(theMap[key].internets) and len(theMap[key].tvs)):
            csvConvert(theMap[key].packages[0].city, theMap[key].packages[0].state,theMap[key])
for key in theMap:
    if not len(theMap[key].locations) and (not len(theMap[key].packages) or not len(theMap[key].internets) or not len(theMap[key].tvs)):
        csvConvert(theMap[key].locations[0].city, theMap[key].locations[0].state,theMap[key])
