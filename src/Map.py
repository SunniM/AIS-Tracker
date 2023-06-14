import math

earthCir = 40075016.686
degreesPerMeter = 360 / earthCir

class Map():

    def __init__(self,latitude,longitude,zoom):
        self.latitude = latitude
        self.longitude = longitude
        self.zoom = zoom
   
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
