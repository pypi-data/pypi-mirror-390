import re
import numpy as np
from sympy import Matrix
from collections import defaultdict
import math
from typing import Dict, List, Any, Tuple, Optional
from itertools import combinations

# --- Global Constants ---
STANDARD_TEMPERATURE_K = 298.15 # 25°C in Kelvin
R_GAS_CONSTANT = 8.314 / 1000.0  # Gas Constant (kJ/mol·K)
F_FARADAY_CONSTANT = 96.485  # Faraday's Constant (kJ/V·mol)
TOLERANCE = 1e-4 # Numerical tolerance for balancing and comparison

# -----------------------------------------------------------------------------
# 1. CORE DATASET: Elements (Z=1 to Z=118 - COMPLETE, NON-TRUNCATED SET)
# Mass, EN, Type, and Standard Entropy (S°) for all 118 elements.
# Note: Data for synthetic/radioactive elements (S°=0, EN=0) are placeholders 
# to ensure mass calculation and parsing functionality for all Z.
# -----------------------------------------------------------------------------
ELEMENTS = {
    # Period 1
    "H":{"Z":1,"name":"Hydrogen","mass":1.008,"EN":2.20,"type":"nonmetal","oxidation":[1,-1], "S":130.7},
    "He":{"Z":2,"name":"Helium","mass":4.003,"EN":0.00,"type":"noble gas","oxidation":[], "S":126.2},
    # Period 2
    "Li":{"Z":3,"name":"Lithium","mass":6.94,"EN":0.98,"type":"metal","oxidation":[1], "S":29.1},
    "Be":{"Z":4,"name":"Beryllium","mass":9.012,"EN":1.57,"type":"metal","oxidation":[2], "S":9.5},
    "B":{"Z":5,"name":"Boron","mass":10.81,"EN":2.04,"type":"metalloid","oxidation":[3], "S":5.9},
    "C":{"Z":6,"name":"Carbon","mass":12.011,"EN":2.55,"type":"nonmetal","oxidation":[4,-4], "S":5.7},
    "N":{"Z":7,"name":"Nitrogen","mass":14.007,"EN":3.04,"type":"nonmetal","oxidation":[-3,5,3], "S":191.6},
    "O":{"Z":8,"name":"Oxygen","mass":15.999,"EN":3.44,"type":"nonmetal","oxidation":[-2], "S":205.1},
    "F":{"Z":9,"name":"Fluorine","mass":18.998,"EN":3.98,"type":"nonmetal","oxidation":[-1], "S":202.8},
    "Ne":{"Z":10,"name":"Neon","mass":20.180,"EN":0.00,"type":"noble gas","oxidation":[], "S":146.3},
    # Period 3
    "Na":{"Z":11,"name":"Sodium","mass":22.990,"EN":0.93,"type":"metal","oxidation":[1], "S":51.3},
    "Mg":{"Z":12,"name":"Magnesium","mass":24.305,"EN":1.31,"type":"metal","oxidation":[2], "S":32.7},
    "Al":{"Z":13,"name":"Aluminium","mass":26.982,"EN":1.61,"type":"metal","oxidation":[3], "S":28.3},
    "Si":{"Z":14,"name":"Silicon","mass":28.085,"EN":1.90,"type":"metalloid","oxidation":[4], "S":18.8},
    "P":{"Z":15,"name":"Phosphorus","mass":30.974,"EN":2.19,"type":"nonmetal","oxidation":[-3,5,3], "S":41.1},
    "S":{"Z":16,"name":"Sulfur","mass":32.06,"EN":2.58,"type":"nonmetal","oxidation":[-2,6,4], "S":32.1},
    "Cl":{"Z":17,"name":"Chlorine","mass":35.45,"EN":3.16,"type":"nonmetal","oxidation":[-1,7,5,3,1], "S":223.1},
    "Ar":{"Z":18,"name":"Argon","mass":39.948,"EN":0.00,"type":"noble gas","oxidation":[], "S":154.8},
    # Period 4
    "K":{"Z":19,"name":"Potassium","mass":39.098,"EN":0.82,"type":"metal","oxidation":[1], "S":64.7},
    "Ca":{"Z":20,"name":"Calcium","mass":40.078,"EN":1.00,"type":"metal","oxidation":[2], "S":41.4},
    "Sc":{"Z":21,"name":"Scandium","mass":44.956,"EN":1.36,"type":"metal","oxidation":[3], "S":34.6},
    "Ti":{"Z":22,"name":"Titanium","mass":47.867,"EN":1.54,"type":"metal","oxidation":[4,3], "S":30.7},
    "V":{"Z":23,"name":"Vanadium","mass":50.942,"EN":1.63,"type":"metal","oxidation":[5,4,3,2], "S":28.9},
    "Cr":{"Z":24,"name":"Chromium","mass":51.996,"EN":1.66,"type":"metal","oxidation":[3,6,2], "S":23.8},
    "Mn":{"Z":25,"name":"Manganese","mass":54.938,"EN":1.55,"type":"metal","oxidation":[2,4,7], "S":32.0},
    "Fe":{"Z":26,"name":"Iron","mass":55.845,"EN":1.83,"type":"metal","oxidation":[3,2], "S":27.3},
    "Co":{"Z":27,"name":"Cobalt","mass":58.933,"EN":1.88,"type":"metal","oxidation":[2,3], "S":30.0},
    "Ni":{"Z":28,"name":"Nickel","mass":58.693,"EN":1.91,"type":"metal","oxidation":[2,3], "S":29.9},
    "Cu":{"Z":29,"name":"Copper","mass":63.546,"EN":1.90,"type":"metal","oxidation":[2,1], "S":33.1},
    "Zn":{"Z":30,"name":"Zinc","mass":65.38,"EN":1.65,"type":"metal","oxidation":[2], "S":41.6},
    "Ga":{"Z":31,"name":"Gallium","mass":69.723,"EN":1.81,"type":"metal","oxidation":[3], "S":41.6},
    "Ge":{"Z":32,"name":"Germanium","mass":72.63,"EN":2.01,"type":"metalloid","oxidation":[4,2], "S":31.1},
    "As":{"Z":33,"name":"Arsenic","mass":74.922,"EN":2.18,"type":"metalloid","oxidation":[3,5,-3], "S":35.1},
    "Se":{"Z":34,"name":"Selenium","mass":78.971,"EN":2.55,"type":"nonmetal","oxidation":[-2,4,6], "S":42.3},
    "Br":{"Z":35,"name":"Bromine","mass":79.904,"EN":2.96,"type":"nonmetal","oxidation":[-1,1,3,5,7], "S":152.2},
    "Kr":{"Z":36,"name":"Krypton","mass":83.798,"EN":0.00,"type":"noble gas","oxidation":[], "S":164.1},
    # Period 5
    "Rb":{"Z":37,"name":"Rubidium","mass":85.468,"EN":0.82,"type":"metal","oxidation":[1], "S":76.8},
    "Sr":{"Z":38,"name":"Strontium","mass":87.62,"EN":0.95,"type":"metal","oxidation":[2], "S":52.9},
    "Y":{"Z":39,"name":"Yttrium","mass":88.906,"EN":1.22,"type":"metal","oxidation":[3], "S":48.9},
    "Zr":{"Z":40,"name":"Zirconium","mass":91.224,"EN":1.33,"type":"metal","oxidation":[4], "S":39.4},
    "Nb":{"Z":41,"name":"Niobium","mass":92.906,"EN":1.6,"type":"metal","oxidation":[5,3], "S":36.4},
    "Mo":{"Z":42,"name":"Molybdenum","mass":95.96,"EN":2.16,"type":"metal","oxidation":[6,4,3], "S":28.7},
    "Tc":{"Z":43,"name":"Technetium","mass":98.0,"EN":1.9,"type":"metal","oxidation":[7,4], "S":0.0},
    "Ru":{"Z":44,"name":"Ruthenium","mass":101.07,"EN":2.2,"type":"metal","oxidation":[4,3], "S":28.9},
    "Rh":{"Z":45,"name":"Rhodium","mass":102.91,"EN":2.28,"type":"metal","oxidation":[3,4], "S":31.8},
    "Pd":{"Z":46,"name":"Palladium","mass":106.42,"EN":2.20,"type":"metal","oxidation":[2,4], "S":39.4},
    "Ag":{"Z":47,"name":"Silver","mass":107.87,"EN":1.93,"type":"metal","oxidation":[1], "S":42.6},
    "Cd":{"Z":48,"name":"Cadmium","mass":112.41,"EN":1.69,"type":"metal","oxidation":[2], "S":51.8},
    "In":{"Z":49,"name":"Indium","mass":114.82,"EN":1.78,"type":"metal","oxidation":[3,1], "S":57.8},
    "Sn":{"Z":50,"name":"Tin","mass":118.71,"EN":1.96,"type":"metal","oxidation":[4,2], "S":51.2},
    "Sb":{"Z":51,"name":"Antimony","mass":121.76,"EN":2.05,"type":"metalloid","oxidation":[3,5], "S":45.7},
    "Te":{"Z":52,"name":"Tellurium","mass":127.60,"EN":2.1,"type":"metalloid","oxidation":[4,6], "S":49.8},
    "I":{"Z":53,"name":"Iodine","mass":126.90,"EN":2.66,"type":"nonmetal","oxidation":[-1,1,3,5,7], "S":116.1},
    "Xe":{"Z":54,"name":"Xenon","mass":131.29,"EN":0.00,"type":"noble gas","oxidation":[2,4,6], "S":169.7},
    # Period 6 (Full set including Lanthanides)
    "Cs":{"Z":55,"name":"Cesium","mass":132.91,"EN":0.79,"type":"metal","oxidation":[1], "S":85.2},
    "Ba":{"Z":56,"name":"Barium","mass":137.33,"EN":0.89,"type":"metal","oxidation":[2], "S":69.4},
    "La":{"Z":57,"name":"Lanthanum","mass":138.91,"EN":1.1,"type":"metal","oxidation":[3], "S":56.9},
    "Ce":{"Z":58,"name":"Cerium","mass":140.12,"EN":1.12,"type":"metal","oxidation":[3,4], "S":56.9},
    "Pr":{"Z":59,"name":"Praseodymium","mass":140.91,"EN":1.13,"type":"metal","oxidation":[3], "S":66.9},
    "Nd":{"Z":60,"name":"Neodymium","mass":144.24,"EN":1.14,"type":"metal","oxidation":[3], "S":71.5},
    "Pm":{"Z":61,"name":"Promethium","mass":145.0,"EN":1.13,"type":"metal","oxidation":[3], "S":0.0},
    "Sm":{"Z":62,"name":"Samarium","mass":150.36,"EN":1.17,"type":"metal","oxidation":[3,2], "S":70.9},
    "Eu":{"Z":63,"name":"Europium","mass":151.96,"EN":1.2,"type":"metal","oxidation":[3,2], "S":70.3},
    "Gd":{"Z":64,"name":"Gadolinium","mass":157.25,"EN":1.2,"type":"metal","oxidation":[3], "S":66.5},
    "Tb":{"Z":65,"name":"Terbium","mass":158.93,"EN":1.2,"type":"metal","oxidation":[3], "S":73.2},
    "Dy":{"Z":66,"name":"Dysprosium","mass":162.50,"EN":1.22,"type":"metal","oxidation":[3], "S":73.0},
    "Ho":{"Z":67,"name":"Holmium","mass":164.93,"EN":1.23,"type":"metal","oxidation":[3], "S":71.5},
    "Er":{"Z":68,"name":"Erbium","mass":167.26,"EN":1.24,"type":"metal","oxidation":[3], "S":74.6},
    "Tm":{"Z":69,"name":"Thulium","mass":168.93,"EN":1.25,"type":"metal","oxidation":[3,2], "S":74.0},
    "Yb":{"Z":70,"name":"Ytterbium","mass":173.05,"EN":1.27,"type":"metal","oxidation":[3,2], "S":74.0},
    "Lu":{"Z":71,"name":"Lutetium","mass":174.97,"EN":1.27,"type":"metal","oxidation":[3], "S":51.5},
    "Hf":{"Z":72,"name":"Hafnium","mass":178.49,"EN":1.3,"type":"metal","oxidation":[4], "S":43.9},
    "Ta":{"Z":73,"name":"Tantalum","mass":180.95,"EN":1.5,"type":"metal","oxidation":[5], "S":41.4},
    "W":{"Z":74,"name":"Tungsten","mass":183.84,"EN":2.36,"type":"metal","oxidation":[6,4], "S":33.2},
    "Re":{"Z":75,"name":"Rhenium","mass":186.21,"EN":1.9,"type":"metal","oxidation":[7,4], "S":31.7},
    "Os":{"Z":76,"name":"Osmium","mass":190.23,"EN":2.2,"type":"metal","oxidation":[4,8], "S":31.5},
    "Ir":{"Z":77,"name":"Iridium","mass":192.22,"EN":2.20,"type":"metal","oxidation":[3,4], "S":35.2},
    "Pt":{"Z":78,"name":"Platinum","mass":195.08,"EN":2.28,"type":"metal","oxidation":[2,4], "S":41.6},
    "Au":{"Z":79,"name":"Gold","mass":196.97,"EN":2.54,"type":"metal","oxidation":[1,3], "S":47.4},
    "Hg":{"Z":80,"name":"Mercury","mass":200.59,"EN":2.00,"type":"metal","oxidation":[1,2], "S":75.9},
    "Tl":{"Z":81,"name":"Thallium","mass":204.38,"EN":1.62,"type":"metal","oxidation":[1,3], "S":64.1},
    "Pb":{"Z":82,"name":"Lead","mass":207.2,"EN":1.87,"type":"metal","oxidation":[2,4], "S":64.8},
    "Bi":{"Z":83,"name":"Bismuth","mass":208.98,"EN":2.02,"type":"metal","oxidation":[3,5], "S":53.4},
    "Po":{"Z":84,"name":"Polonium","mass":209.0,"EN":2.0,"type":"metalloid","oxidation":[2,4], "S":0.0},
    "At":{"Z":85,"name":"Astatine","mass":210.0,"EN":2.2,"type":"nonmetal","oxidation":[-1,1], "S":0.0},
    "Rn":{"Z":86,"name":"Radon","mass":222.0,"EN":0.00,"type":"noble gas","oxidation":[], "S":176.2},
    # Period 7 (Full set including Actinides and Superheavies)
    "Fr":{"Z":87,"name":"Francium","mass":223.0,"EN":0.7,"type":"metal","oxidation":[1], "S":0.0},
    "Ra":{"Z":88,"name":"Radium","mass":226.0,"EN":0.9,"type":"metal","oxidation":[2], "S":0.0},
    "Ac":{"Z":89,"name":"Actinium","mass":227.0,"EN":1.1,"type":"metal","oxidation":[3], "S":0.0},
    "Th":{"Z":90,"name":"Thorium","mass":232.04,"EN":1.3,"type":"metal","oxidation":[4], "S":51.8},
    "Pa":{"Z":91,"name":"Protactinium","mass":231.04,"EN":1.5,"type":"metal","oxidation":[5,4], "S":0.0},
    "U":{"Z":92,"name":"Uranium","mass":238.03,"EN":1.38,"type":"metal","oxidation":[3,4,6], "S":50.3},
    "Np":{"Z":93,"name":"Neptunium","mass":237.0,"EN":1.36,"type":"metal","oxidation":[5,4,6], "S":0.0},
    "Pu":{"Z":94,"name":"Plutonium","mass":244.0,"EN":1.28,"type":"metal","oxidation":[4,3,6], "S":0.0},
    "Am":{"Z":95,"name":"Americium","mass":243.0,"EN":1.3,"type":"metal","oxidation":[3], "S":0.0},
    "Cm":{"Z":96,"name":"Curium","mass":247.0,"EN":1.3,"type":"metal","oxidation":[3], "S":0.0},
    "Bk":{"Z":97,"name":"Berkelium","mass":247.0,"EN":1.3,"type":"metal","oxidation":[3,4], "S":0.0},
    "Cf":{"Z":98,"name":"Californium","mass":251.0,"EN":1.3,"type":"metal","oxidation":[3], "S":0.0},
    "Es":{"Z":99,"name":"Einsteinium","mass":252.0,"EN":1.3,"type":"metal","oxidation":[3], "S":0.0},
    "Fm":{"Z":100,"name":"Fermium","mass":257.0,"EN":1.3,"type":"metal","oxidation":[3,2], "S":0.0},
    "Md":{"Z":101,"name":"Mendelevium","mass":258.0,"EN":1.3,"type":"metal","oxidation":[3,2], "S":0.0},
    "No":{"Z":102,"name":"Nobelium","mass":259.0,"EN":1.3,"type":"metal","oxidation":[2,3], "S":0.0},
    "Lr":{"Z":103,"name":"Lawrencium","mass":262.0,"EN":1.3,"type":"metal","oxidation":[3], "S":0.0},
    "Rf":{"Z":104,"name":"Rutherfordium","mass":267.0,"EN":0.0,"type":"metal","oxidation":[4], "S":0.0},
    "Db":{"Z":105,"name":"Dubnium","mass":268.0,"EN":0.0,"type":"metal","oxidation":[5], "S":0.0},
    "Sg":{"Z":106,"name":"Seaborgium","mass":271.0,"EN":0.0,"type":"metal","oxidation":[6], "S":0.0},
    "Bh":{"Z":107,"name":"Bohrium","mass":272.0,"EN":0.0,"type":"metal","oxidation":[7], "S":0.0},
    "Hs":{"Z":108,"name":"Hassium","mass":270.0,"EN":0.0,"type":"metal","oxidation":[8], "S":0.0},
    "Mt":{"Z":109,"name":"Meitnerium","mass":276.0,"EN":0.0,"type":"metal","oxidation":[3], "S":0.0},
    "Ds":{"Z":110,"name":"Darmstadtium","mass":281.0,"EN":0.0,"type":"metal","oxidation":[2], "S":0.0},
    "Rg":{"Z":111,"name":"Roentgenium","mass":280.0,"EN":0.0,"type":"metal","oxidation":[1,3], "S":0.0},
    "Cn":{"Z":112,"name":"Copernicium","mass":285.0,"EN":0.0,"type":"metal","oxidation":[2], "S":0.0},
    "Nh":{"Z":113,"name":"Nihonium","mass":286.0,"EN":0.0,"type":"metal","oxidation":[1], "S":0.0},
    "Fl":{"Z":114,"name":"Flerovium","mass":289.0,"EN":0.0,"type":"metal","oxidation":[4,2], "S":0.0},
    "Mc":{"Z":115,"name":"Moscovium","mass":290.0,"EN":0.0,"type":"metal","oxidation":[3,1], "S":0.0},
    "Lv":{"Z":116,"name":"Livermorium","mass":293.0,"EN":0.0,"type":"nonmetal","oxidation":[4,2], "S":0.0},
    "Ts":{"Z":117,"name":"Tennessine","mass":294.0,"EN":0.0,"type":"nonmetal","oxidation":[1,3,5], "S":0.0},
    "Og":{"Z":118,"name":"Oganesson","mass":294.21,"EN":0.00,"type":"noble gas","oxidation":[], "S":0.0},
}

# -----------------------------------------------------------------------------
# 2. RULESETS (Polyatomic Ions, Solubility, Reactivity)
# -----------------------------------------------------------------------------
POLYATOMIC_IONS = {
    "hydroxide": ("OH", -1), "nitrate": ("NO3", -1), "sulfate": ("SO4", -2), 
    "carbonate": ("CO3", -2), "phosphate": ("PO4", -3), "ammonium": ("NH4", 1),
    "chlorate": ("ClO3", -1), "permanganate": ("MnO4", -1), "chromate": ("CrO4", -2),
    "bicarbonate": ("HCO3", -1), "bisulfate": ("HSO4", -1), "acetate": ("CH3COO", -1),
    "dichromate": ("Cr2O7", -2), "cyanide": ("CN", -1),
}
SOLUBILITY_RULES = {
    "always_soluble_cations": ["Na", "K", "NH4", "Li", "Rb"],
    "always_soluble_anions": ["NO3", "CH3COO", "ClO4"],
    "mostly_soluble_anions": {"Cl": ["Ag", "Pb", "Hg"], "SO4": ["Ba", "Sr", "Pb", "Ca"]},
    "mostly_insoluble_anions": ["CO3", "PO4", "S", "OH", "CrO4"],
    "hydroxides": ["Ca", "Sr", "Ba"],
}
REACTIVITY_SERIES = {
    "highly_reactive_metals": ["K", "Na", "Li", "Ba", "Ca"], 
    "moderately_reactive_metals": ["Mg", "Al", "Zn", "Fe"],
    "low_reactive_metals": ["Cu", "Ag", "Hg"],
    "inert_metals": ["Ir", "Pt", "Au"], 
}

# -----------------------------------------------------------------------------
# 3. THERMODYNAMIC DATASET (Sufficient for all examples/features)
# -----------------------------------------------------------------------------
THERMO_DATA = {
    # Compounds relevant to core examples
    "H2O(l)": {"ΔHf": -285.8, "ΔGf": -237.1, "S": 69.9},
    "H2O(g)": {"ΔHf": -241.8, "ΔGf": -228.6, "S": 188.8},
    "CO2(g)": {"ΔHf": -393.5, "ΔGf": -394.4, "S": 213.7},
    "CO(g)": {"ΔHf": -110.5, "ΔGf": -137.2, "S": 197.6},
    "CaCO3(s)": {"ΔHf": -1207.6, "ΔGf": -1128.8, "S": 92.9},
    "CaO(s)": {"ΔHf": -635.1, "ΔGf": -604.0, "S": 39.8},
    "C2H5OH(l)": {"ΔHf": -277.6, "ΔGf": -174.8, "S": 160.7}, # Ethanol
    "AgNO3(aq)": {"ΔHf": -124.4, "ΔGf": -33.7, "S": 140.9},
    "NaCl(aq)": {"ΔHf": -407.3, "ΔGf": -393.1, "S": 115.5},
    "NaNO3(aq)": {"ΔHf": -446.2, "ΔGf": -367.0, "S": 205.0},
    "AgCl(s)": {"ΔHf": -127.1, "ΔGf": -109.8, "S": 96.2},
    "HI(g)": {"ΔHf": 26.5, "ΔGf": 1.7, "S": 206.6},
    "NOCl(g)": {"ΔHf": 51.7, "ΔGf": 66.3, "S": 261.6},
    "NO(g)": {"ΔHf": 90.3, "ΔGf": 86.6, "S": 210.8},
    # Other common substances
    "NH3(g)": {"ΔHf": -46.1, "ΔGf": -16.5, "S": 192.8},
    "CH4(g)": {"ΔHf": -74.8, "ΔGf": -50.8, "S": 186.3}, 
    "Fe2O3(s)": {"ΔHf": -824.2, "ΔGf": -742.2, "S": 87.4},
    "HCl(aq)": {"ΔHf": -167.2, "ΔGf": -131.2, "S": 56.5},
    "NaOH(aq)": {"ΔHf": -470.1, "ΔGf": -419.2, "S": 48.2},
    "FeCl3(aq)": {"ΔHf": -400.0, "ΔGf": -310.0, "S": 280.0},
    "H2(g)": {"ΔHf": 0.0, "ΔGf": 0.0, "S": 130.7},
    "I2(s)": {"ΔHf": 0.0, "ΔGf": 0.0, "S": 116.1},
    "Cl2(g)": {"ΔHf": 0.0, "ΔGf": 0.0, "S": 223.1},
    "O2(g)": {"ΔHf": 0.0, "ΔGf": 0.0, "S": 205.1},
}

# -----------------------------------------------------------------------------
# 4. KINETIC & EQUILIBRIA DATASET
# -----------------------------------------------------------------------------
REACTION_KINETICS = {
    "CaCO3+heat": {"Ea": 178.3, "A": 1e12, "order": 1, "note": "Decomposition: High barrier."},
    "C2H5OH+O2": {"Ea": 120.0, "A": 1e15, "order": 3, "note": "Combustion: Moderately high barrier, high pre-exponential factor."},
    "AgNO3+NaCl": {"Ea": 1.0, "A": 1e18, "order": 2, "note": "Precipitation: Near zero activation energy (instantaneous)."},
    "2HI->H2+I2": {"Ea": 186.0, "A": 3.98e-1, "order": 2, "note": "Gas phase decomposition."},
    "2NOCl->2NO+Cl2": {"Ea": 98.0, "A": 1.2e13, "order": 2, "note": "Gas phase decomposition (moderate barrier)."},
}
ACID_PKA = {
    "HCl": -7.0, "H2SO4": -3.0, "HNO3": -1.3,
    "CH3COOH": 4.76, "HCN": 9.21, 
    "NH4+": 9.25, 
    "H2O": 15.7, 
    "HF": 3.17, 
}
REDOX_POTENTIALS = {
    "MnO4- + 8H+ + 5e- -> Mn2+ + 4H2O": 1.51,
    "Cl2 + 2e- -> 2Cl-": 1.36,
    "Cr2O7-2 + 14H+ + 6e- -> 2Cr3+ + 7H2O": 1.33,
    "Ag+ + e- -> Ag": 0.80,
    "Fe3+ + e- -> Fe2+": 0.77,
    "Cu2+ + 2e- -> Cu": 0.34,
    "2H+ + 2e- -> H2": 0.00,
    "Fe2+ + 2e- -> Fe": -0.44,
    "Zn2+ + 2e- -> Zn": -0.76,
    "Al3+ + 3e- -> Al": -1.66,
    "Na+ + e- -> Na": -2.71,
}

# -----------------------------------------------------------------------------
# 5. CORE CLASS IMPLEMENTATION (Complete and Non-Truncated)
# -----------------------------------------------------------------------------

class chi:
    """
    A comprehensive utility for chemical mass balance, dynamic thermodynamics, 
    kinetics, pH simulation, and redox potential analysis. Fully self-contained 
    with a complete 118 element dataset and all necessary compound data.
    """
    def __init__(self, T_K: float = STANDARD_TEMPERATURE_K, verbose: bool = True):
        self.ELEMENTS = ELEMENTS
        self.THERMO_DATA = THERMO_DATA
        self.KINETIC_DATA = REACTION_KINETICS
        self.ACID_PKA = ACID_PKA
        self.REDOX_POTENTIALS = REDOX_POTENTIALS
        self.VERBOSE = verbose
        self.T = T_K
        self.R = R_GAS_CONSTANT
        self.F = F_FARADAY_CONSTANT
        self.TOLERANCE = TOLERANCE

    def _vprint(self, *args, **kwargs):
        """Prints output only if verbosity is enabled."""
        if self.VERBOSE:
            print(*args, **kwargs)

    # --- Utility Methods ---
    def _parse_formula(self, formula: str) -> Dict[str, int]:
        """Parses a chemical formula and returns a dictionary of element counts."""
        comp = defaultdict(int)
        formula = formula.replace('[', '(').replace(']', ')')
        formula = formula.replace('·', '.')
        # FIXED: Correct regex pattern for state removal
        formula_no_state = re.sub(r'\([slgaq]\)', '', formula)
        
        # Handle Hydrates
        hydrate_match = re.search(r'\.(\d+)(H2O)', formula_no_state)
        if hydrate_match:
            h2o_count = int(hydrate_match.group(1))
            comp["H"] += 2 * h2o_count
            comp["O"] += 1 * h2o_count
            formula_no_state = formula_no_state[:hydrate_match.start()]

        formula_stack = [(formula_no_state, 1)] 
        element_pattern = re.compile(r'([A-Z][a-z]?)(\d*)')
        
        while formula_stack:
            segment, multiplier = formula_stack.pop()
            if not segment: continue

            # Handle Polyatomic Groups
            group_match = re.search(r'\(([A-Za-z0-9]+)\)(\d*)', segment)
            
            if group_match:
                group_content = group_match.group(1)
                subscript = int(group_match.group(2)) if group_match.group(2) else 1
                formula_stack.append((group_content, multiplier * subscript))
                formula_stack.append((segment[:group_match.start()], multiplier))
                formula_stack.append((segment[group_match.end():], multiplier))
            else:
                # Handle simple elements
                for (el, num) in element_pattern.findall(segment):
                    if el not in self.ELEMENTS:
                        raise ValueError(f"Unknown element symbol '{el}' in formula '{formula}'.")
                    count = int(num) if num else 1
                    comp[el] += count * multiplier
        
        if not comp:
             raise ValueError(f"Could not parse any elements from formula '{formula}'.")
             
        return dict(comp)

    def _get_species_state(self, formula: str) -> str:
        """Determines physical state using solubility rules and compound type."""
        # FIXED: Correct regex pattern for state removal
        formula_no_state = re.sub(r'\([slgaq]\)', '', formula)
        
        # Known states check
        if formula_no_state in ["H2O", "C6H6", "C2H5OH"]: return "(l)"
        if formula_no_state in ["H2", "O2", "N2", "CO2", "CH4", "C2H6", "C3H8"]: return "(g)"
        
        try:
            parsed = self._parse_formula(formula_no_state)
            elements = list(parsed.keys())
            
            # Cation detection (Metal or N for Ammonium)
            cation_el = next((el for el in elements if self.ELEMENTS.get(el, {}).get("type") == "metal" or el == "N"), None)
            
            if not cation_el: return "(s)"

            # Check general solubility rules
            if cation_el in SOLUBILITY_RULES["always_soluble_cations"] or any(anion in formula_no_state for anion in SOLUBILITY_RULES["always_soluble_anions"]): 
                return "(aq)"
                
            # Check exceptions for mostly soluble anions (Cl, SO4)
            if "Cl" in parsed and cation_el in SOLUBILITY_RULES["mostly_soluble_anions"]["Cl"]: return "(s)"
            
            # Check exceptions for mostly insoluble anions (CO3, PO4, S, OH)
            if any(anion in formula_no_state for anion in SOLUBILITY_RULES["mostly_insoluble_anions"]):
                if cation_el not in SOLUBILITY_RULES["always_soluble_cations"]:
                    return "(s)"
            
        except:
             return "(s)"

        return "(aq)"

    def _calculate_thermodynamic_value(self, balanced_equation: str, thermo_type: str) -> float:
        r"""Calculates $\Delta H$, $\Delta G$, or $\Delta S$ of reaction using Hess's Law."""
        try:
            left, right = balanced_equation.split("->")
        except ValueError:
            raise ValueError("Invalid equation format. Must use '->' to separate reactants and products.")
            
        # FIXED: Correct regex pattern without spaces in character class
        pattern = r'(\d*)([A-Za-z0-9]+)\(([slgaq])\)'
        reactants = re.findall(pattern, left)
        products = re.findall(pattern, right)

        total_reactants = 0.0
        total_products = 0.0

        for part, sign in [(reactants, -1), (products, 1)]:
            for coeff_str, formula, state in part:
                coeff = int(coeff_str) if coeff_str else 1
                key = f"{formula}({state})"
                
                value = self.THERMO_DATA.get(key, {}).get(thermo_type, 0.0)
                
                # Use elemental standard entropy if compound data is missing and it's an element
                if thermo_type == 'S' and formula in self.ELEMENTS and value == 0.0 and coeff == 1:
                    value = self.ELEMENTS[formula].get("S", 0.0)
                
                # Standard state elements: $\Delta H_f^{\circ} = 0$, $\Delta G_f^{\circ} = 0$
                is_elemental_standard_state = (formula in self.ELEMENTS) and (thermo_type in ['ΔHf', 'ΔGf'])
                
                if value == 0.0 and not is_elemental_standard_state and self.VERBOSE:
                    self._vprint(f"Warning: Missing data for '{key}' ({thermo_type}). Assuming 0.0.")

                contribution = coeff * value
                
                if sign == -1: total_reactants += contribution
                else: total_products += contribution

        return total_products - total_reactants

    def _calculate_thermodynamics(self, balanced_equation: str, T_K: Optional[float] = None) -> Dict[str, Any]:
        r"""Calculates $\Delta H$, $\Delta S$, and T-dependent $\Delta G$."""
        T = T_K if T_K is not None else self.T
        
        delta_h = self._calculate_thermodynamic_value(balanced_equation, 'ΔHf')
        delta_s_J = self._calculate_thermodynamic_value(balanced_equation, 'S')
        delta_s_kJ = delta_s_J / 1000.0
        
        # Gibbs-Helmholtz: $\Delta G = \Delta H - T \Delta S$
        delta_g_calc = delta_h - (T * delta_s_kJ)
        
        spontaneity = "Spontaneous (Favorable)" if delta_g_calc < -self.TOLERANCE else "Non-spontaneous (Unfavorable)"
        if abs(delta_g_calc) < self.TOLERANCE:
             spontaneity = "Equilibrium or Near-Equilibrium"
             
        return {
            "Delta_H_kJ/mol": round(delta_h, 2),
            "Delta_S_J/molK": round(delta_s_J, 2),
            "Delta_G_kJ/mol": round(delta_g_calc, 2),
            "Spontaneity": spontaneity,
            "T_K": T,
        }

    # --- Core Public Methods ---
    
    def balance(self, equation: str, T_K: Optional[float] = None) -> None:
        """Balances equation, adds states, and prints full T-dependent thermodynamic report."""
        current_T = T_K if T_K is not None else self.T
        self._vprint(f"\n--- Running Mass Balance and T-Dependent Thermodynamic Analysis (T={current_T} K) ---")
        
        try:
            left, right = equation.replace(" ", "").split("->")
            reactants = left.split("+")
            products = right.split("+")
            species = reactants + products
            
            # Parse without states first
            parsed_species = [self._parse_formula(re.sub(r'\([slgaq]\)', '', s)) for s in species]
            all_elements = {el for p in parsed_species for el in p}
            elems = sorted(list(all_elements))
            
            # Construct the stoichiometric matrix A (Elements x Species)
            A = np.zeros((len(elems), len(species)), dtype=int)
            for i, el in enumerate(elems):
                for j, parsed in enumerate(parsed_species):
                    count = parsed.get(el, 0)
                    A[i, j] = count if j < len(reactants) else -count

            A_matrix = Matrix(A)
            nullspace = A_matrix.nullspace()
            
            if not nullspace: 
                raise ValueError("Equation cannot be balanced (no non-trivial solution). Check input format.")
                
            x = nullspace[0]
            
            # Convert coefficients to smallest integers (Clear fractions)
            denominators = [v.q for v in x]
            lcm = 1
            for d in denominators:
                lcm = abs(lcm * d) // math.gcd(lcm, d)

            coeffs = [int(abs(v) * lcm) for v in x]
            
            # Ensure proper sign convention (Reactants positive)
            first_nonzero_index = next((i for i, c in enumerate(coeffs) if c != 0), -1)
            if first_nonzero_index != -1 and x[first_nonzero_index] < 0:
                coeffs = [-c for c in coeffs]
            
            # Simplify coefficients by dividing by GCD
            gcd_val = coeffs[0]
            for c in coeffs[1:]:
                gcd_val = math.gcd(gcd_val, c)
            
            if gcd_val > 1:
                coeffs = [c // gcd_val for c in coeffs]
            
            # Add States and Format Equation
            def format_species(species_list: List[str], coeffs_list: List[int]) -> str:
                parts = []
                for coeff, spec in zip(coeffs_list, species_list):
                    c_str = "" if coeff == 1 else str(coeff)
                    state = self._get_species_state(spec)
                    parts.append(f"{c_str}{spec}{state}")
                return " + ".join(parts)
            
            lhs = format_species(reactants, coeffs[:len(reactants)])
            rhs = format_species(products, coeffs[len(reactants):])
            balanced_eqn = f"{lhs} -> {rhs}"
            
            # Calculate Thermodynamics
            delta_results = self._calculate_thermodynamics(balanced_eqn, T_K=current_T)

            # Print Comprehensive Report
            print("\n--- STOICHIOMETRIC & T-DEPENDENT THERMODYNAMIC REPORT ---")
            print(f"**Input Equation:** {equation}")
            print(f"**Balanced Equation (with States):** {balanced_eqn}")
            print(f"**Stoichiometric Coefficients:** Reactants ({coeffs[:len(reactants)]}) : Products ({coeffs[len(reactants):]})")
            print("--- Thermodynamic Analysis ---")
            print(f"**Temperature (T):** {current_T} K")
            print(fr"**Enthalpy ($\Delta H^{{\circ}}$):** {delta_results['Delta_H_kJ/mol']} kJ/mol ({'Exothermic' if delta_results['Delta_H_kJ/mol'] < 0 else 'Endothermic'})")
            print(fr"**Entropy ($\Delta S^{{\circ}}$):** {delta_results['Delta_S_J/molK']} J/mol·K")
            print(fr"**Gibbs Free Energy ($\Delta G$ at T):** {delta_results['Delta_G_kJ/mol']} kJ/mol")
            print(f"**Spontaneity:** {delta_results['Spontaneity']} (Reaction is {'Product-Favored' if delta_results['Delta_G_kJ/mol'] < 0 else 'Reactant-Favored'} at {current_T} K)")

        except ValueError as ve:
            print(f"❌ **Error (Balance/Parsing):** {ve}")
        except Exception as e:
            print(f"❌ **Error (System Failure):** An unexpected error occurred during balancing: {e}")

    def predict(self, *symbols) -> None:
        """Analyzes and prints all possible simple compound formations, bond types, and properties."""
        sym_list = [s for s in symbols if s in self.ELEMENTS]
        
        if len(sym_list) < 2:
            print("--- Compound Prediction Report ---")
            print("Error: Need at least two valid elements for compound formation analysis.")
            return

        print("\n" + "="*75)
        print(f"       COMPREHENSIVE COMPOUND PREDICTION REPORT for {', '.join(sym_list)}       ")
        print("="*75)
        
        results = []
        element_data = {s: self.ELEMENTS[s] for s in sym_list}
        
        for el1, el2 in combinations(sym_list, 2):
            data1, data2 = element_data[el1], element_data[el2]
            
            if data1["EN"] == data2["EN"]: continue

            # Electronegativity determines cation/anion roles
            cation_el, anion_el = (el1, el2) if data1["EN"] < data2["EN"] else (el2, el1)
            cation_data, anion_data = (data1, data2) if data1["EN"] < data2["EN"] else (data2, data1)

            delta_en = abs(data1["EN"] - data2["EN"])
            
            # 1. Determine Bond Type
            is_metal = cation_data["type"] in ["metal", "metalloid"]
            is_nonmetal = anion_data["type"] in ["nonmetal", "metalloid", "noble gas"] # Noble gas can still form bonds
            
            if is_metal and is_nonmetal and delta_en > 1.7:
                bond_type = "Ionic"
            elif delta_en > 1.7:
                bond_type = "Highly Polar Covalent (Approaching Ionic)"
            elif delta_en > 0.4:
                bond_type = "Polar Covalent"
            else:
                bond_type = "Nonpolar Covalent"
                
            # 2. Formula Generation (Criss-Cross Rule using primary oxidation states)
            ox1 = abs(cation_data.get("oxidation", [1])[0])
            ox2 = abs(anion_data.get("oxidation", [1])[0])
            
            if ox1 == 0 or ox2 == 0: # Handle noble gases/elements with no defined oxidation state
                formula = f"{cation_el}{anion_el}"
                sub1, sub2 = 1, 1
            else:
                lcm = (ox1 * ox2) // math.gcd(ox1, ox2)
                sub1 = lcm // ox1
                sub2 = lcm // ox2
                formula = f"{cation_el}{sub1 if sub1 > 1 else ''}{anion_el}{sub2 if sub2 > 1 else ''}"
            
            # 3. Nomenclature (IUPAC Heuristics)
            if bond_type.startswith("Ionic"):
                name = f"{cation_data['name']} {anion_data['name'][:-2]}ide"
            else:
                # Use prefixes for covalent compounds
                prefix_map = {1: "mono", 2: "di", 3: "tri", 4: "tetra", 5: "penta", 6: "hexa"}
                prefix1 = prefix_map.get(sub1, str(sub1))
                prefix2 = prefix_map.get(sub2, str(sub2))
                
                if sub1 == 1: prefix1 = ""
                
                # Simple heuristic for naming
                name = f"{prefix1}{cation_data['name']} {prefix2}{anion_data['name'][:-2]}ide".capitalize()
            
            # 4. Properties/Nature
            if bond_type.startswith("Ionic"):
                nature = "High melting point solid, strong lattice, conductive in melt/solution."
                detail = f"Bond is primarily electrostatic ($\\%\\text{{Ionicity}} \\approx {100*(1-math.exp(-0.25*delta_en**2)):.1f}\\%$)."
            else:
                nature = "Low melting point, gas/liquid/soft solid, non-conductive."
                detail = "Bond involves electron sharing. Compound is molecular."
                
            results.append({
                "Elements": f"{el1} & {el2}", "Formula": formula, "Name": name, 
                "Bond Type": bond_type, "ΔEN": round(delta_en, 2), "Nature": nature,
                "Applicable Detail": detail
            })

        for i, res in enumerate(results, 1):
            print(f"--- Possible Compound {i} ({res['Elements']}) ---")
            print(f"  **Formula:** {res['Formula']} | **IUPAC Name:** {res['Name']}")
            print(fr"  **Bond Type:** {res['Bond Type']} ($\Delta\text{{EN}} = {res['ΔEN']}$)")
            print(f"  **Typical Nature:** {res['Nature']}")
            print(f"  **Applicable Detail:** {res['Applicable Detail']}")

        print("="*75)

    def ReactionFeasibilityIndex(self, equation: str, T_K: Optional[float] = None) -> None:
        """Calculates a unified Feasibility Index (RFI), incorporating T-dependent kinetics and thermodynamics."""
        current_T = T_K if T_K is not None else self.T
        T_ref = STANDARD_TEMPERATURE_K
        
        print("\n" + "="*75)
        print(f"      REACTION FEASIBILITY INDEX (RFI) REPORT (T={current_T} K)     ")
        print("="*75)
        
        lookup_key = None
        
        # Mapping input equations to stored kinetic data and a pre-balanced equation for quick lookup
        if "CaCO3" in equation:
             balanced_eqn = "1CaCO3(s) -> 1CaO(s) + 1CO2(g)"
             lookup_key = "CaCO3+heat"
        elif "C2H5OH" in equation and "O2" in equation:
             balanced_eqn = "1C2H5OH(l) + 3O2(g) -> 2CO2(g) + 3H2O(l)"
             lookup_key = "C2H5OH+O2"
        elif "AgNO3" in equation and "NaCl" in equation:
             balanced_eqn = "1AgNO3(aq) + 1NaCl(aq) -> 1NaNO3(aq) + 1AgCl(s)"
             lookup_key = "AgNO3+NaCl"
        elif "HI" in equation and "H2" in equation:
             balanced_eqn = "2HI(g) -> 1H2(g) + 1I2(s)"
             lookup_key = "2HI->H2+I2"
        elif "NOCl" in equation:
             balanced_eqn = "2NOCl(g) -> 2NO(g) + 1Cl2(g)"
             lookup_key = "2NOCl->2NO+Cl2"
        else:
            print(f"❌ **Error (Feasibility):** Equation '{equation}' not found in kinetic models. Run 'balance()' first for basic analysis.")
            return

        delta_results = self._calculate_thermodynamics(balanced_eqn, T_K=current_T)
        delta_g = delta_results['Delta_G_kJ/mol']
        
        # Kinetics (T-dependence: Arrhenius Equation)
        kinetic_data = self.KINETIC_DATA.get(lookup_key, {})
        Ea = kinetic_data.get("Ea", 150.0)
        A = kinetic_data.get("A", 1e12)
        note = kinetic_data.get("note", "N/A")
        
        try:
            k_at_T = A * math.exp(-Ea / (self.R * current_T))
            k_at_ref = A * math.exp(-Ea / (self.R * T_ref))
            rate_factor = k_at_T / k_at_ref
        except OverflowError:
            k_at_T = float('inf')
            rate_factor = float('inf')
        except ZeroDivisionError:
             k_at_T = 0
             rate_factor = 0
        
        # RFI Scoring
        rfi = 0
        summary_points = []
        
        # Score 1: Thermodynamics (Weight: 50)
        if delta_g < -50: 
            rfi += 50
            summary_points.append(fr"Thermodynamics: **Highly Favorable $\Delta G$** ($\Delta G={delta_g}$ kJ/mol).")
        elif delta_g < 0: 
            rfi += 25
            summary_points.append(fr"Thermodynamics: Favorable $\Delta G$ (Spontaneous at $T={current_T}$ K).")
        else:
            rfi += 5
            summary_points.append(fr"Thermodynamics: Unfavorable $\Delta G$ (Non-spontaneous, requires external energy).")

        # Score 2: Kinetics (Weight: 45)
        if Ea < 50 and k_at_T > 1e1: 
            rfi += 45
            summary_points.append(f"Kinetics: **Extremely Fast** ($E_a={Ea}$ kJ/mol, $k \\approx {k_at_T:.2e}$).")
        elif Ea < 100 or k_at_T > 1e-1:
            rfi += 25
            summary_points.append(f"Kinetics: Moderate to Fast Rate. Proceeds readily at this temperature.")
        else:
            summary_points.append(f"Kinetics: Slow Rate ($E_a={Ea}$ kJ/mol). External factors like catalyst or higher T needed.")
            
        summary_points.append(f"T-dependence: Rate is **{rate_factor:.2f} times** the rate at 298.15 K.")
        
        rfi = min(100, max(0, rfi + 5))
        
        print(f"**Balanced Equation (used for calculation):** {balanced_eqn}")
        print("-" * 75)
        print(f"**Feasibility Index (RFI):** **{rfi}/100**")
        print(fr"**Thermodynamics:** $\Delta G = {delta_g:.2f}$ kJ/mol | **{delta_results['Spontaneity']}**")
        print(f"**Kinetics Data:** $E_a={Ea}$ kJ/mol | $A={A:.2e}$ | Note: {note}")
        print(f"**Calculated Rate Constant (k at T):** ${k_at_T:.2e}$")
        print("\n**Feasibility Breakdown:**")
        for point in summary_points:
            print(f"  - {point}")
        print("="*75 + "\n")

    def simulate_pH(self, acid_or_base: str, concentration: float = 0.1) -> None:
        """Simulates the pH of an aqueous solution using pKa data."""
        print("\n--- pH SIMULATION REPORT ---")
        
        if concentration <= self.TOLERANCE:
            print("❌ **Error (pH):** Concentration must be positive and significant.")
            return

        pKa = self.ACID_PKA.get(acid_or_base)
        
        if pKa is None:
            print(f"❌ **Error (pH):** pKa data for '{acid_or_base}' not found. Cannot simulate pH.")
            return

        pH = 0.0
        analysis_note = ""

        if pKa <= 0:
            # Strong acid assumed (full dissociation)
            H_plus = concentration
            pH = -math.log10(H_plus)
            analysis_note = f"Strong Acid (pKa $\\leq 0$). Full dissociation assumed: $[H^+] = {concentration}$ M."
        else:
            try:
                # Weak acid approximation: [H+] = sqrt(Ka * C)
                Ka = 10**(-pKa)
                H_plus = math.sqrt(Ka * concentration)
                pH = -math.log10(H_plus)
                analysis_note = f"Weak Acid (pKa > 0). Equilibrium calculation using $K_a={Ka:.2e}$ and $[H^+] = \\sqrt{{K_a \\cdot C_0}}$."
            except ValueError:
                print("❌ **Error (pH):** Invalid concentration or pKa value for calculation.")
                return

        print(f"Substance: {acid_or_base} | Initial Concentration: {concentration} M | pKa: {pKa}")
        print(f"Analysis: {analysis_note}")
        print(f"**Simulated pH:** **{pH:.2f}**")
        print(f"Solution Nature: {'Acidic' if pH < 7 - self.TOLERANCE else 'Basic/Neutral'}")
        print("----------------------------------\n")

    def balance_redox(self, reduction_half_rxn: str, oxidation_half_rxn: str) -> None:
        r"""Predicts spontaneity of a redox reaction using E° potentials and calculates $\Delta G^{\circ}$."""
        print("\n--- REDOX POTENTIAL ANALYSIS REPORT ---")
        
        E_cathode = self.REDOX_POTENTIALS.get(reduction_half_rxn)
        E_anode_red = self.REDOX_POTENTIALS.get(oxidation_half_rxn)
        
        if E_cathode is None or E_anode_red is None:
            print("❌ **Error (Redox):** One or both half-reactions not found in E° data. Check format/data.")
            return

        # Determine n (number of electrons transferred in each half-reaction)
        n_cathode_match = re.search(r'(\d+)e-', reduction_half_rxn)
        n_anode_match = re.search(r'(\d+)e-', oxidation_half_rxn)
        
        if not n_cathode_match or not n_anode_match:
            print("❌ **Error (Redox):** Could not reliably determine number of electrons (n) from format. Assuming n=1.")
            n_electrons = 1
        else:
            n_cathode = int(n_cathode_match.group(1))
            n_anode = int(n_anode_match.group(1))
            # Determine the LCM for 'n' which is the total electrons transferred in the balanced reaction
            n_electrons = (n_cathode * n_anode) // math.gcd(n_cathode, n_anode)

        # Calculate Overall E° and $\Delta G^{\circ}$
        E_cell = E_cathode - E_anode_red
        # $\Delta G^{\circ} = -n F E^{\circ}_{cell}$ (F in kJ/V·mol)
        delta_G_elec = -n_electrons * self.F * E_cell 
        
        spontaneity = "Spontaneous (Favorable)" if E_cell > self.TOLERANCE else "Non-spontaneous (Unfavorable)"
        
        print(f"Cathode (Reduction): {reduction_half_rxn} | $E^{{\\circ}}_{{red}} = {E_cathode:.2f}$ V")
        print(f"Anode (Oxidation): {oxidation_half_rxn} (Flipped) | $E^{{\\circ}}_{{red}} = {E_anode_red:.2f}$ V")
        print("-------------------------------------------------------")
        print(f"**Electron Transfer (n):** {n_electrons}")
        print(f"**Overall Cell Potential ($E^{{\\circ}}_{{cell}}$):** **{E_cell:.2f} V**")
        print(f"**Gibbs Free Energy ($\Delta G^{{\\circ}}$):** **{delta_G_elec:.2f} kJ/mol**")
        print(f"**Predicted Spontaneity:** {spontaneity}")
        print("-------------------------------------------------------\n")
        
    def calculate_molecular_mass(self, formula: str) -> None:
        """Calculates and prints the molecular mass for a given chemical formula."""
        try:
            counts = self._parse_formula(formula)
            total_mass = sum(self.ELEMENTS[el]["mass"] * count for el, count in counts.items())
            
            print("\n--- Molecular Mass Report ---")
            print(f"Formula: {formula}")
            print(f"Composition: {dict(counts)}")
            print(f"**Molar Mass (MM): {round(total_mass, 3)} g/mol**")
        except ValueError as ve:
            print(f"❌ **Error (Mass Calculation):** {ve}")
        except Exception as e:
            print(f"❌ **Error (Mass Calculation):** An unexpected error occurred: {e}")