def calculate_emissions(fuel=0, electricity=0, livestock=0, fertilizer=0):
    CO2_PER_LITER_FUEL = 2.68
    CO2_PER_KWH_ELECTRICITY = 0.5
    CO2_PER_LIVESTOCK = 100
    CO2_PER_KG_FERTILIZER = 1.8

    emission_details = {
        'Fuel': round(fuel * CO2_PER_LITER_FUEL, 2),
        'Electricity': round(electricity * CO2_PER_KWH_ELECTRICITY, 2),
        'Livestock': round(livestock * CO2_PER_LIVESTOCK, 2),
        'Fertilizer': round(fertilizer * CO2_PER_KG_FERTILIZER, 2),
    }
    emission_total = sum(emission_details.values())
    return emission_details, emission_total


def calculate_absorption(trees=0, crops=0, soil=0):
    CO2_ABSORPTION_TREE = 21.77
    CO2_ABSORPTION_CROP_HA = 3000
    CO2_ABSORPTION_SOIL_HA = 1500

    absorption_details = {
        'Trees': round(trees * CO2_ABSORPTION_TREE, 2),
        'Crops': round(crops * CO2_ABSORPTION_CROP_HA, 2),
        'Soil': round(soil * CO2_ABSORPTION_SOIL_HA, 2),
    }
    absorption_total = sum(absorption_details.values())
    return absorption_details, absorption_total


def compare_emission_absorption(emission_total, absorption_total):
    if emission_total > absorption_total:
        return "Your farm emits more CO₂ than it absorbs"
    elif absorption_total > emission_total:
        return "Your farm absorbs more CO₂ than it emits"
    else:
        return "Your farm’s CO₂ is balanced"