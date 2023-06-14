import math

earthCir = 40075016.686
degreesPerMeter = 360 / earthCir

class Map():

    def __init__(self,latitude,longitude,zoom):
        self.latitude = latitude
        self.longitude = longitude
        self.zoom = zoom
        self.calculate_bounding_box(1920,1080)
   
    #Converts to radians from Deg
    def toRadians(self, degrees):
        return (degrees * math.pi/180)

    #Calculates the bounding box of what is displayed
    def calculate_bounding_box(self, width, height):
        metersPerPixelEW = earthCir / math.pow(2, self.zoom + 8)
        metersPerPixelNS = earthCir / math.pow(2, self.zoom + 8) * math.cos(self.toRadians(self.latitude))
        
        shiftMetersEW = width/2 * metersPerPixelEW
        shiftMetersNS = height/2 * metersPerPixelNS
        
        shiftDegreesEW = shiftMetersEW * degreesPerMeter
        shiftDegreesNS = shiftMetersNS * degreesPerMeter

        return (self.latitude-shiftDegreesNS), (self.longitude-shiftDegreesEW), (self.latitude+shiftDegreesNS), (self.longitude+shiftDegreesEW)
    
    # Printing all data
    def print_map_data(self, width, height):

        south, west, north, east = self.calculate_bounding_box(width, height)

        print("\nlatitude: ", self.latitude)
        print("longitude: ", self.longitude)
        print("zoom: ", self.zoom)
        print("topLeft: ", (north,west))
        print("botLeft: ", (south,west))
        print("topRight: ", (north,east))
        print("botRight: ", (south,east)) 
        print("\n")  

