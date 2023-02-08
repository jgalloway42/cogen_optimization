"""
Created on Mon May 01 08:49:46 2017

Desuperheater FF/Sizing calcs
PRV with desuperheating after PRV

IAWPS 97 Docs
Dict with calculated properties. The available properties are:

T: Saturated temperature, [K]
P: Saturated pressure, [MPa]
x: Vapor quality, [-]
v: Specific volume, [m³/kg]
h: Specific enthalpy, [kJ/kg]
s: Specific entropy, [kJ/kgK]

@author: joshua
"""
from iapws import IAPWS97

# Constants
PSI2MPA = 0.101325/14.69
MPA2PSI = 1./PSI2MPA
BAR2MPA = 0.1
MPA2BAR = 1./BAR2MPA
KJKG2BTULB = 0.42992
BTULB2KJKG = 1./ KJKG2BTULB
KJKGK2BTULBR = 0.238846
BTULBR2KJKGK = 1./KJKGK2BTULBR
LBGAL2KGCM = 119.826
KGCM2LBGAL = 1./LBGAL2KGCM
KGS2LBHR = 7937 # kg/s steam to lb/hr
LBHR2KGS = 1/KGS2LBHR
SCFPERLBMOL = 379.3
LIQUID = 0.
SATSTEAM = 1.

# Functions
def F2K(f):
    """ Fahrenheit to Kelvin """
    return 5./9.*(f + 459.67)

def K2F(k):
    """ Kelvin to Fahrenheit """
    return k*9./5. - 459.67
def C2K(c):
    """ Celcius to Kelvin """
    return c + 273.15
def K2C(k):
    """ Kelvin to Celcius """
    return k - 273.15

def psia(p):
    """ PSIG to PSIA """
    return p + 14.69

def psig(p):
    """ PSIA to PSIG """
    return p - 14.69


def superheatedSteamEnthalpy(psig,degF, returnS = False):
    '''Takes psig and degF of superheated steam and returns
    enthalpy'''
    # System Parameters converted to metric units
    AdhocPress = PSI2MPA*psia(psig)            # Up stream header pressure
    AdhocTemp = F2K(degF)                       # Up stream header temperature

    # get steam in properties
    steamProps = IAPWS97(P = AdhocPress, T = AdhocTemp)
    S = steamProps.s*KJKGK2BTULBR
    H = steamProps.h*KJKG2BTULB
    if returnS:
        ret = (H,S)
    else:
        ret = H
        
    return ret

def liquidPhaseEnthalpy(psig,degF):
    waterTemp = F2K(degF)            # Water Temperature
    waterPress = PSI2MPA*psia(psig)   # Water pressure
    water = IAPWS97(P = waterPress, T = waterTemp, x = LIQUID)
    return water.h*KJKG2BTULB
    
    