import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS

mappings = {
    'reserve_requirements_percent': 'Reserve Requirements Percentage',
    'transmission_network_losses': 'System Line Losses Percentage',
    'water_rentals_CAD_per_MWh': 'Water Rentals',
}

provinces_to_keep = [
    'British Columbia_02',
    'Alberta',
    'Manitoba_02',
    'Saskatchewan',
    'Ontario_02',
    'Quebec_01',
    'New Brunswick',
    'Nova Scotia',
    'Prince Edward Island',
    'Newfoundland and Labrador',
]

short_to_long = {
    'AB': 'Alberta',
    'BC': 'British Columbia',
    'MB': 'Manitoba',
    'NB': 'New Brunswick',
    'NL': 'Newfoundland and Labrador',
    'NS': 'Nova Scotia',
    'ON': 'Ontario',
    'PE': 'Prince Edward Island',
    'QC': 'Quebec',
    'SK': 'Saskatchewan',
}

def get_data(api_key: str, year=2021):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"{CODERS}/reserve_requirements?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        reserve_modeled_attributes = pd.json_normalize(json_response)

    reserve_modeled_attributes = reserve_modeled_attributes[['province', f'year_{year}']].rename(columns={f'year_{year}': 'reserve_requirements_percent'})
    reserve_modeled_attributes['province'] = reserve_modeled_attributes['province'].map(short_to_long)
    reserve_modeled_attributes = reserve_modeled_attributes.melt(id_vars=['province'], var_name='variable', value_name='value')

    with urlopen(f"{CODERS}/transmission_losses?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        trs_modeled_attributes = pd.json_normalize(json_response).drop(columns=['notes']).melt(id_vars=['province'], var_name='variable', value_name='value')
        trs_modeled_attributes['province'] = trs_modeled_attributes['province'].map(short_to_long)


    with urlopen(f"{CODERS}/water_rentals_energy_based?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        water_modeled_attributes = pd.json_normalize(json_response)
    water_modeled_attributes = water_modeled_attributes[['province', f'year_{year}']].rename(columns={f'year_{year}': 'water_rentals_CAD_per_MWh'})
    water_modeled_attributes = water_modeled_attributes[water_modeled_attributes['province'].isin(provinces_to_keep)].melt(id_vars=['province'], var_name='variable', value_name='value')
    water_modeled_attributes['province'] = water_modeled_attributes['province'].apply(lambda x: x.split('_')[0] if '_' in x else x)

    melted = pd.concat([reserve_modeled_attributes, trs_modeled_attributes, water_modeled_attributes], ignore_index=True)
    melted['variable'] = melted['variable'].map(mappings)
    melted = melted.rename(columns={'province': 'region'})
    return melted


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
