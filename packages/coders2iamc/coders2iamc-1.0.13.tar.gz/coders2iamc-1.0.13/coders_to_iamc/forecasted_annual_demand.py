import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS

mappings = {
    'latitude': 'Generators|Latitude|',
    'longitude': 'Generators|Longitude|',
    'unit_installed_capacity': 'Generators|Capacity|',
    'network_node_code': 'Generators|Node Code|',
}


def get_data(api_key: str):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    print(f"{CODERS}/historic_and_forecasted_annual_energy_demand?key={api_key}")
    with urlopen(f"{CODERS}/historic_and_forecasted_annual_energy_demand?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

        # rename columns to take out year_ prefix
        modeled_attributes.rename(columns=lambda x: x.replace('year_', '') if x.startswith('year_') else x,
                                  inplace=True)

        # drop note columns if they exist
        modeled_attributes = modeled_attributes.drop(columns='notes',
                                                     errors='ignore')

        melted = modeled_attributes.melt(id_vars=['province', 'unit'],
                                         var_name='time', value_name='value')

        melted['variable'] = 'Forecasted Annual Demand'
        melted.rename(columns={'province': 'region'}, inplace=True)
        return melted


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
