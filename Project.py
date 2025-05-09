"""
Project for Week 4 of "Python Data Visualization".
Unify data via common country codes.

Be sure to read the project description page for further information
about the expected behavior of the program.
"""
import csv
import math
import pygal


def build_country_code_converter(codeinfo):
    """
    Builds a dictionary mapping pygal plot codes to World Bank codes.
    """
    code_dict = {}
    with open(codeinfo["codefile"], newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile,
                                delimiter=codeinfo["separator"],
                                quotechar=codeinfo["quote"])
        for row in reader:
            plot_code = row[codeinfo["plot_codes"]].strip()  # Ensure original case is kept
            data_code = row[codeinfo["data_codes"]].strip()
            code_dict[plot_code] = data_code
    return code_dict


def reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries):
    """
    Returns a tuple:
    - Dictionary mapping pygal plot codes to matching GDP country codes.
    - Set of plot codes with no corresponding match in GDP data.
    """
    converter = build_country_code_converter(codeinfo)
    matched = {}
    unmatched = set()

    for plot_code, plot_country_name in plot_countries.items():
        norm_code = plot_code.lower()
        for converter_plot_code, gdp_code in converter.items():
            if converter_plot_code.lower() == norm_code:
                for original_gdp_key in gdp_countries.keys():
                    if original_gdp_key.upper() == gdp_code.upper():
                        matched[plot_code] = original_gdp_key
                        break
                else:
                    unmatched.add(plot_code)
                break
        else:
            unmatched.add(plot_code)

    return matched, unmatched


def read_gdp_data(gdpinfo):
    """
    Reads GDP CSV into a dictionary mapping country codes to full data rows.
    """
    gdp_data = {}
    with open(gdpinfo["gdpfile"], newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile,
                                delimiter=gdpinfo["separator"],
                                quotechar=gdpinfo["quote"])
        for row in reader:
            code = row[gdpinfo["country_code"]].strip().upper()
            gdp_data[code] = row
    return gdp_data


def build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year):
    """
    Creates a dictionary suitable for plotting GDP log values on a world map.

    Returns:
    - Dictionary of {plot_code: log10(GDP)} for valid countries
    - Set of plot codes not found in GDP file
    - Set of plot codes with no GDP data for that year
    """
    gdp_data = read_gdp_data(gdpinfo)
    matched, unmatched = reconcile_countries_by_code(codeinfo, plot_countries, gdp_data)

    result = {}
    no_data_for_year = set()

    for plot_code, gdp_code in matched.items():
        gdp_value = gdp_data[gdp_code].get(year, '').strip()
        try:
            gdp = float(gdp_value)
            if gdp > 0:
                result[plot_code] = math.log10(gdp)
            else:
                no_data_for_year.add(plot_code)
        except (ValueError, TypeError):
            no_data_for_year.add(plot_code)

    return result, unmatched, no_data_for_year


def render_world_map(gdpinfo, codeinfo, plot_countries, year, map_file):
    """
    Renders the GDP world map using pygal.
    """
    gdp_map, no_match, no_data = build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year)

    chart = pygal.maps.world.World()
    chart.title = f'GDP by Country in {year} (Log Scale)'

    chart.add('GDP (log10)', gdp_map)
    chart.add('No match in GDP file', list(no_match))
    chart.add('No GDP for year', list(no_data))

    chart.render_to_file(map_file)

    # Optional: render in browser (local testing only)
    #chart.render_in_browser()


def test_render_world_map():
    """
    Runs render_world_map for selected years and generates SVG maps.
    """
    gdpinfo = {
        "gdpfile": "isp_gdp.csv",
        "separator": ",",
        "quote": '"',
        "min_year": 1960,
        "max_year": 2015,
        "country_name": "Country Name",
        "country_code": "Country Code"
    }

    codeinfo = {
        "codefile": "isp_country_codes.csv",
        "separator": ",",
        "quote": '"',
        "plot_codes": "ISO3166-1-Alpha-2",
        "data_codes": "ISO3166-1-Alpha-3"
    }

    pygal_countries = pygal.maps.world.COUNTRIES

    for yr in ["1960", "1980", "2000", "2010"]:
        render_world_map(gdpinfo, codeinfo, pygal_countries, yr, f"isp_gdp_world_code_{yr}.svg")


# Comment out the following lines:
# ###  Example 0 plot_countries lc:UC, code _converter UC:UC
# codeinfo = {'separator': ',', 'quote': '"', 'codefile': 'code4.csv', 'data_codes': 'ISO3166-1-Alpha-3',
#             'plot_codes': 'ISO3166-1-Alpha-2'}
# plot_countries = {'no': 'Norway', 'pr': 'Puerto Rico', 'us': 'United States'}
# gdp_countries =  {'USA': {'Country Code': 'USA', 'Country Name': 'United States'}, 'NOR': {'Country Code': 'NOR', 'Country Name': 'Norway'}}
# print("Example 0\nExpected: ({'no': 'NOR', 'us': 'USA'}, {'pr'})")
# print(reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries))
# print("******************************************\n")
#
# ###     Example 1 plot_countries lc:UC, code _converter UC:UC
# codeinfo = {'codefile': 'code4.csv', 'plot_codes': 'ISO3166-1-Alpha-2',
#             'data_codes': 'ISO3166-1-Alpha-3', 'quote': '"', 'separator': ','}
# plot_countries = {'pr': 'Puerto Rico', 'no': 'Norway', 'us': 'United States'}
# gdp_countries =  {'USA': {'Country Name': 'United States', 'Country Code': 'USA'},
#                   'PRI': {'Country Name': 'Puerto Rico', 'Country Code': 'PRI'},
#                   'NOR': {'Country Name': 'Norway', 'Country Code': 'NOR'}}
# print("Example 1\nExpected:   ({'pr': 'PRI', 'no': 'NOR', 'us': 'USA'}, set())")
# print(reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries))
# print("******************************************\n")
#
# ##    Example 2   plot_countries UC:lc, code _converter lc:UC
# codeinfo  =  {'separator': ',', 'quote': "'", 'plot_codes': 'Cd2',
#               'data_codes': 'Cd3', 'codefile': 'code2.csv'}
# plot_countries = {'C2': 'c2', 'C5': 'c5', 'C4': 'c4', 'C3': 'c3', 'C1': 'c1'}
# gdp_countries = {'ABC': {'Country Name': 'Country1', 'Code': 'ABC', '2000': '1', '2001': '2', '2002': '3', '2003': '4', '2004': '5', '2005': '6'},
#                 'GHI': {'Country Name': 'Country2', 'Code': 'GHI', '2000': '10', '2001': '11', '2002': '12', '2003': '13', '2004': '14', '2005': '15'}}
# print("Example 2\nExpected:  ({'C3': 'GHI', 'C1': 'ABC'}, {'C5', 'C2', 'C4'})")
# print(reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries))
# print("******************************************\n")
#
#
# ##    Example 3 plot_countries lc:UC, code _converter UC:UC, no countries in gdp_countries
# codeinfo = {'quote': '"', 'data_codes': 'ISO3166-1-Alpha-3',
#             'plot_codes': 'ISO3166-1-Alpha-2', 'separator': ',', 'codefile': 'code4.csv'}
# plot_countries = {'jp': 'Japan', 'cn': 'China', 'ru': 'Russian Federation'}
# gdp_countries = {}
# print("Example 3\nExpected: ({}, {'jp', 'cn', 'ru'})")
# print(reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries))
# print("******************************************\n")
#
#
# ##   Example 4     plot countries UC:lc, code_converter lc:MixED
# codeinfo =  {'quote': "'", 'separator': ',', 'plot_codes': 'Code4', 'codefile': 'code1.csv', 'data_codes': 'Code3'}
# plot_countries =  {'C4': 'c4', 'C3': 'c3', 'C2': 'c2', 'C1': 'c1', 'C5': 'c5'}
# gdp_countries =  {
# 'qR': {'ID': 'A 5 ', 'CC': 'qR'},
# 'Kl': {'ID': 'B 6', 'CC': 'Kl'},
# 'WX': {'ID': 'C 7 ', 'CC': 'WX'},
# 'ef': {'ID': 'D 8', 'CC': 'ef'}
# }
# print("Example 4\nExpected ({'C4': 'ef', 'C3': 'Kl', 'C2': 'qR', 'C1': 'WX'}, {'C5'})")
# print(reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries))
# print("******************************************\n")
