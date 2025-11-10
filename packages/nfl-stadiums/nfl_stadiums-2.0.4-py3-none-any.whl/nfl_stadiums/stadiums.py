from lukhed_basic_utils import requestsCommon as rC
from lukhed_basic_utils import osCommon as osC
from lukhed_basic_utils import fileCommon as fC
from lukhed_basic_utils import timeCommon as tC
from nfl_stadiums.custom_libs.teamLists import city_short, alt_city_short, long, mascots, mascots_short
import urllib.parse
import math


class NFLStadiums:
    """
    This class scrapes from wikipedia main page:
    https://en.wikipedia.org/wiki/List_of_current_NFL_stadiums

    And various pages linked to on the main page.
    """
    def __init__(self, use_cache=True, verbose=True):
        """

        :param use_cache:   bool(), if True, the class will try to use cache from last time it scraped the web. Since
                            this data is fairly static, use_cache is on by default. Turn it off if you suspect
                            there were changes in the data to get the latest.
        """
        self.data = list()
        self._stadium_metadata = {}
        self.verbose = verbose

        # API Info
        self._header = {'User-Agent': 'NFLTeamStadiums/0.1 (https://github.com/lukhed/nfl_stadiums)'}
        self._main_url = "https://en.wikipedia.org/w/api.php"

        # Project Structure
        self._resources_dir = osC.create_file_path_string(["nfl_stadium_resources"])
        self._raw_soup = None

        self._potential_stadium_list_indices = []
        self._current_stadium_section_indice = None     #wikipedia section indice (to be found)
        self._current_stadium_soup = None
        self._current_stadium_file = osC.append_to_dir(self._resources_dir, "currentStadiumSoup.txt")

        self._potential_other_section_indices = []
        self._other_stadium_section_indice = None       #wikipedia section indice (to be found)
        self._other_stadium_soup = None
        self._other_stadium_file = osC.append_to_dir(self._resources_dir, "otherStadiumSoup.txt")

        self._parsed_soup_file = osC.append_to_dir(self._resources_dir, "parsedSoup.json")

        self._check_create_project_structure()

        # Used for team lookups
        self._teams_city_short = [x.lower() for x in city_short]
        self._teams_alt_city_short = [x.lower() for x in alt_city_short]
        self._teams_long = [x.lower() for x in long]
        self._teams_mascots = [x.lower() for x in mascots]
        self._teams_mascots_short = [x.lower() for x in mascots_short]
        self._team_lists = [self._teams_city_short, self._teams_alt_city_short, self._teams_long,
                            self._teams_mascots, self._teams_mascots_short]

        # Get the Data
        if use_cache:
            self._check_cache()

        if not self.data:
            self._get_section_indices()
            self._get_current_stadium_data()
            if self._potential_other_section_indices:
                self._get_other_stadium_data()

            self._add_normalized_current_team_to_data()
            self._add_stadium_coordinates_to_data()
            fC.dump_json_to_file(self._parsed_soup_file, self.data)

    def _check_print(self, print_txt):
        if self.verbose:
            print(print_txt)

    def _check_cache(self):

        self._current_stadium_soup = fC.read_file_content(self._current_stadium_file)
        self._other_stadium_soup = fC.read_file_content(self._other_stadium_file)
        parsed_soup = fC.load_json_from_file(self._parsed_soup_file)

        if parsed_soup == "" or parsed_soup == {}:
            self._check_print("INFO: No cache available. If this is first run this is normal.")
        else:
            self._check_print("INFO: Loaded data from cache. If the data needs to be refreshed, start the class with "
                              "parameter use_cache = False")
            self.data = parsed_soup

    @staticmethod
    def _get_table_rows(table_element):
        return table_element.find_all('tr')

    @staticmethod
    def _get_table_column_indices(table_rows):
        columns = [x.text.strip() for x in table_rows[0].find_all('th')]
        try:
            name_index = columns.index('Name')
        except ValueError:
            name_index = columns.index('Stadium')
        img_index = columns.index('Image')
        capacity_index = columns.index('Capacity')
        city_index = columns.index('Location')
        surface_index = columns.index('Surface')
        
        try:
            roof_index = columns.index('Roof type')
        except ValueError:
            roof_index = columns.index('Roof')

        try:
            teams_or_events = columns.index('Team(s)')
            is_teams = True
        except ValueError:
            try:
                teams_or_events = columns.index('Event(s)')
            except ValueError:
                teams_or_events = "N/A"
                is_teams = False

        date_opened_index = columns.index('Opened')

        return (name_index, img_index, capacity_index, city_index, surface_index, roof_index, teams_or_events,
                date_opened_index, is_teams)

    @staticmethod
    def _clean_wiki_text(text_to_extract_from):
        text_to_extract_from = text_to_extract_from.strip()
        ref_bracket_loc = text_to_extract_from.find('[')
        return text_to_extract_from[:ref_bracket_loc] if ref_bracket_loc > -1 else text_to_extract_from

    def _narrow_down_stadium_section_indices(self, current_or_other):
        """
        There are multiple sections that could contain the data we are looking for. Call the wiki api
        for each section and check the data if it is staddium data.
        """
        if current_or_other == 'current':
            section_indices = self._potential_stadium_list_indices
        else:
            section_indices = self._potential_other_section_indices

        for index in section_indices:
            params = {
                "action": "parse",
                "page": "List of current NFL stadiums",
                "format": "json",
                "prop": "text",
                "section": index
            }

            response = rC.make_request(self._main_url, params=params, headers=self._header)
            data = response.json()

            # Extract the HTML content
            html_content = data['parse']['text']['*']

            # Parse the HTML content with BeautifulSoup
            section_soup = rC.get_soup_from_html_content(html_content)

            table_element = section_soup.select_one("table.wikitable.sortable")

            if table_element:
                test_rows = self._get_table_rows(table_element)
                try:
                    test = self._get_table_column_indices(test_rows)
                    if current_or_other == 'current':
                        self._current_stadium_section_indice = index
                    else:
                        self._other_stadium_section_indice = index
                    break
                except Exception as e:
                    continue

            tC.sleep(0.5)
    
    def _parse_table_add_to_data(self, table_rows):
        (name_index, img_index, capacity_index, city_index, surface_index, roof_index, teams_or_events,
         date_opened_index, is_teams) = self._get_table_column_indices(table_rows)

        index_count = len(self.data)
        for row in table_rows[1:]:
            cells = row.find_all(['th', 'td'])
            name = self._clean_wiki_text(cells[name_index].text)
            temp_url = cells[name_index].find_all('a')[0].attrs['href']
            try:
                temp_class_list = cells[name_index].find_all('a')[0].attrs['class']
            except KeyError:
                temp_class_list = []

            if len([x for x in temp_class_list if 'redirect' in x]) > 0:
                has_redirect = True
            else:
                has_redirect = False
            title = urllib.parse.unquote(temp_url.rsplit('/', 1)[-1])
            self._stadium_metadata[title] = {}
            self._stadium_metadata[title]['name'] = name
            self._stadium_metadata[title]['url'] = f"https://en.wikipedia.org{temp_url}"
            self._stadium_metadata[title]['index'] = index_count
            self._stadium_metadata[title]['hasRedirect'] = has_redirect
            try:
                img_url = f"https://en.wikipedia.org{cells[img_index].find_all('a')[0].attrs['href']}"
            except:
                img_url = None

            capacity = self._clean_wiki_text(cells[capacity_index].text.replace(",", ""))
            city = self._clean_wiki_text(cells[city_index].text)
            surface = self._clean_wiki_text(cells[surface_index].text)
            roof_type = self._clean_wiki_text(cells[roof_index].text)
            if is_teams:
                teams = [self._clean_wiki_text(x.text) for x in cells[teams_or_events].find_all('a')]
            else:
                teams = []

            year_opened = self._clean_wiki_text(cells[date_opened_index].text)

            temp_dict = {
                "name": name,
                "capacity": int(capacity),
                "imgUrl": img_url,
                "city": city,
                "surface": surface,
                "roofType": roof_type,
                "teams": teams,
                "yearOpened": int(year_opened)
            }

            self.data.append(temp_dict.copy())
            index_count = index_count + 1

    def _get_section_indices(self):
        # Get the relevant section indices for current stadiums and other stadiums

        # Parameters for the API request
        params = {
            "action": "parse",
            "page": "List of current NFL stadiums",
            "format": "json",
            "prop": "sections"
        }

        # Make the API request to view page sections
        self._check_print("INFO: Retrieving base stadium data from wikipedia")

        response = rC.make_request(self._main_url, params=params, headers=self._header)
        data = response.json()

        for section in data['parse']['sections']:
            section_line = section['line'].lower()
            section_line = section_line.replace("_", "")
            if 'list' in section_line:
                self._potential_stadium_list_indices.append(section["index"])
            if 'special' in section_line:
                self._potential_other_section_indices.append(section["index"])

        if not self._potential_stadium_list_indices:
            print("ERROR: Couldn't find current stadium section at wikipedia page. Please make an issue below:\n"
                    "https://github.com/lukhed/nfl_stadiums/issues")
            quit()

        if not self._potential_other_section_indices:
            print("ERROR: Couldn't find special event stadium section at wikipedia page. Please make an issue below:\n"
                    "https://github.com/lukhed/nfl_stadiums/issues")

    def _get_current_stadium_data(self):
        if len(self._potential_stadium_list_indices) > 1:
            self._narrow_down_stadium_section_indices('current')
        else:
            self._current_stadium_section_indice = self._potential_stadium_list_indices[0]

        # Make api request to get the section data
        params = {
            "action": "parse",
            "page": "List of current NFL stadiums",
            "format": "json",
            "prop": "text",
            "section": self._current_stadium_section_indice
        }

        response = rC.make_request(self._main_url, params=params, headers=self._header)
        data = response.json()

        # Extract the HTML content
        html_content = data['parse']['text']['*']

        # Parse the HTML content with BeautifulSoup
        self._current_stadium_soup = rC.get_soup_from_html_content(html_content)
        fC.write_content_to_file(self._current_stadium_file, str(self._current_stadium_soup))

        table_element = self._current_stadium_soup.select_one("table.wikitable.sortable")


        if not table_element:
            print("ERROR: Couldn't find current stadium table at the wikipedia page. Please make an issue below:\n"
                  "https://github.com/lukhed/nfl_stadiums/issues")
            quit()

        table_rows = self._get_table_rows(table_element)
        self._parse_table_add_to_data(table_rows)

    def _get_other_stadium_data(self):
        if len(self._potential_other_section_indices) > 1:
            self._narrow_down_stadium_section_indices("other")
        else:
            self._other_stadium_section_indice = self._potential_other_section_indices[0]

        # Make api request to get the section data
        params = {
            "action": "parse",
            "page": "List of current NFL stadiums",
            "format": "json",
            "prop": "text",
            "section": self._other_stadium_section_indice
        }

        response = rC.make_request(self._main_url, params=params, headers=self._header)
        data = response.json()

        # Extract the HTML content
        html_content = data['parse']['text']['*']

        # Parse the HTML content with BeautifulSoup
        self._other_stadium_soup = rC.get_soup_from_html_content(html_content)
        fC.write_content_to_file(self._other_stadium_file, str(self._other_stadium_soup))

        table_element = self._other_stadium_soup.select_one("table.wikitable.sortable")

        if not table_element:
            print("ERROR: Couldn't find special event stadium table at wikipedia page. Please make an issue below:\n"
                  "https://github.com/lukhed/nfl_stadiums/issues")
            return None

        table_rows = self._get_table_rows(table_element)
        self._parse_table_add_to_data(table_rows)
    
    def _add_normalized_current_team_to_data(self):
        """
        This function adds the 'sharedStadium' and 'currentTeams' data
        :return:
        """
        for stadium in self.data:
            found_current_teams = []
            for team in stadium['teams']:
                found_team = self._get_normalized_team(team)
                if found_team:
                    found_current_teams.append(found_team)

            stadium['sharedStadium'] = False if len(found_current_teams) <= 1 else True
            stadium['currentTeams'] = found_current_teams.copy()

    def _resolve_redirects(self, titles):
        batch_size = 10
        final_titles = {}
        for i in range(0, len(titles), batch_size):
            batch_titles = titles[i:i + batch_size]
            batch_titles_str = '|'.join(batch_titles)

            params = {
                'action': 'query',
                'format': 'json',
                'titles': batch_titles_str,
                'redirects': 1
            }

            response = rC.make_request(self._main_url, params=params)

            if response.status_code == 200:
                data = response.json()
                redirects = data.get('query', {}).get('redirects', [])

                # Map original titles to final titles
                for redirect in redirects:
                    final_titles[redirect['from'].replace(" ", "_")] = redirect['to'].replace(" ", "_")

        return final_titles

    def _add_stadium_coordinates_to_data(self):
        titles = [x for x in self._stadium_metadata if self._stadium_metadata[x]['hasRedirect'] is False]
        redirects = [x for x in self._stadium_metadata if self._stadium_metadata[x]['hasRedirect']]
        resolved_redirects = self._resolve_redirects(redirects)
        redirect_titles = list(resolved_redirects.values())

        for from_title, to_title in resolved_redirects.items():
            self._stadium_metadata[from_title]['finalTitle'] = to_title
            titles.append(to_title)

        batch_size = 10     # adjust if some data is not coming back (wikipedia api currently works with 10)
        all_coordinates = {}

        for i in range(0, len(titles), batch_size):
            batch_titles = titles[i:i + batch_size]
            batch_titles_str = '|'.join(batch_titles)

            # API parameters to get the full HTML content
            params = {
                'action': 'query',
                'format': 'json',
                'prop': 'coordinates',
                'titles': batch_titles_str
            }

            response = rC.make_request(self._main_url, headers=self._header, params=params)
            if response.status_code != 200:
                self._check_print("ERROR: Could not complete the API request to get coordinates for stadiums")
                continue

            data = response.json()

            # Process each page in the API response
            pages = data['query']['pages']
            for page_id, page_data in pages.items():
                title = page_data['title'].replace(" ", "_")
                if "coordinates" in page_data:
                    coordinates = page_data["coordinates"][0]
                else:
                    coordinates = None
                all_coordinates[title] = coordinates

            for title, coordinates in all_coordinates.items():
                if title in redirect_titles:
                    for key, value in resolved_redirects.items():
                        if value == title:
                            title = key

                            break
                data_index = self._stadium_metadata[title]['index']
                # noinspection PyTypeChecker
                self.data[data_index]['coordinates'] = coordinates

    def _check_create_project_structure(self):
        osC.check_create_dir_structure(self._resources_dir, full_path=True)
        if not osC.check_if_file_exists(self._current_stadium_file):
            fC.create_blank_file(self._current_stadium_file)
        if not osC.check_if_file_exists(self._other_stadium_file):
            fC.create_blank_file(self._other_stadium_file)
        if not osC.check_if_file_exists(self._parsed_soup_file):
            fC.dump_json_to_file(self._parsed_soup_file, {})

    def _get_normalized_team(self, search_team):
        search_team = search_team.lower()
        for team_list in self._team_lists:
            if search_team in team_list:
                return self._teams_city_short[team_list.index(search_team)].upper()
        return None

    def get_list_of_stadium_names(self):
        """
        Use to get the names of all NFL stadiums

        :return: list() of str()
        """
        return [x['name'] for x in self.data]

    def get_stadium_by_team(self, team):
        """
        Provide the team you want stadium information for.

        :param team:    str(), team in which you want stadium information for. One of the following formats:
                        City + Mascot - e.g., Detroit Lions
                        Mascot - e.g., Lions
                        Team Abbreviation - e.g, DET

        :return:        dict(), JSON format of all available data for the given stadium for the provided team
        """

        team = self._get_normalized_team(team)
        if team is None:
            self._check_print("ERROR: The team you provided to get_stadium_by_team was not recognized. Try "
                              "one of the following formats:\n\n"
                              "City + Mascot - e.g., Detroit Lions\n"
                              "Mascot - e.g., Lions\n"
                              "Team Abbreviation - e.g, DET\n"
                              )
            return None

        teams = [x for x in self.data if team in x['currentTeams']]

        if len(teams) == 1:
            return teams[0]
        elif len(teams) > 1:
            self._check_print("WARNING: the team you provided plays at more than one stadium according to the data. "
                              "Both stadiums are returned in a list")
            return teams
        else:
            self._check_print("ERROR: the team you provided was recognized as a legitimate team, but there is no "
                              "data for them in the Wikipedia content.")
            return None

    def get_stadium_by_name(self, name):
        name = name.lower()

        try:
            return [x for x in self.data if x['name'].lower() == name][0]
        except IndexError:
            self._check_print(f"ERROR: {name} does not match a stadium name in the data. Use get_list_of_stadium_names"
                              f" to get a list of valid stadium names.")
            return None

    def get_stadium_coordinates_by_team(self, team):
        try:
            # noinspection PyTypeChecker
            return self.get_stadium_by_team(team)["coordinates"]
        except TypeError or KeyError:
            return None

    def get_stadium_coordinates_by_name(self, name):
        try:
            # noinspection PyTypeChecker
            return self.get_stadium_by_name(name)["coordinates"]
        except TypeError or KeyError:
            return None

    def calculate_distance_between_stadiums(self, team_stadium1, team_stadium2, name_stadium1=None, name_stadium2=None):
        """
        Calculates the distance in miles from away team stadium to home team stadium by using stadium coordinates
        and the haversine formula (https://en.wikipedia.org/wiki/Haversine_formula)

        :param team_stadium1:    str(), used to get coordinates for corresponding stadium e.g., Detroit Lions
        :param team_stadium2:    str(), used to get coordinates for corresponding stadium e.g., Chiefs
        :param name_stadium1:    str(), optional. Used in place of team_stadium1.
        :param name_stadium2:    str(), optional. Used in place of team_stadium1.

        To use name instead of a team, call the function like below example:
        stadiums.calculate_distance_between_stadiums('', '', stadium1_name='ford field', stadium2_name='at&t stadium')

        :return:                 float(), distance in miles calculated utilizing haversine formula
                                 https://en.wikipedia.org/wiki/Haversine_formula
        """

        def calculate_haversine_distance(coord1, coord2):
            # Radius of the Earth in miles
            radius = 3958.8

            # Coordinates in decimal degrees
            lat1, lon1 = coord1['lat'], coord1['lon']
            lat2, lon2 = coord2['lat'], coord2['lon']

            # Convert latitude and longitude from degrees to radians
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            c = 2 * math.asin(math.sqrt(a))

            # Distance in miles
            distance = radius * c

            return distance

        if name_stadium1 is not None:
            stadium1_coords = self.get_stadium_coordinates_by_name(name_stadium1)
        else:
            stadium1_coords = self.get_stadium_coordinates_by_team(team_stadium1)

        if name_stadium2 is not None:
            stadium2_coords = self.get_stadium_coordinates_by_name(name_stadium2)
        else:
            stadium2_coords = self.get_stadium_coordinates_by_team(team_stadium2)

        if stadium1_coords is None or stadium2_coords is None:
            return None
        else:
            return calculate_haversine_distance(stadium1_coords, stadium2_coords)

    def get_weather_forecast_for_stadium(self, team, day, hour_start=0, hour_end=23, day_format="%Y-%m-%d",
                                         timezone='America/New_York', stadium_name=None):
        """
        :param team:            str(), used to retrieve the stadium for which you want weather. Alternatively, use
                                the stadium_name parameter.

        :param day:             str(), day you want weather in format specified by the day_format parameter
                                (default %Y-%m-%d). E.g., 2024-06-02
                                specified by day_format parameter.

        :param hour_start:      int(), hour in 24-hour format corresponding to the timezone specified in the timezone
                                parameter (default America/New_York). Weather data will be retrieved starting with the
                                hour specified here and through the hour in hour_end (default 0)

        :param hour_end:        int(), hour in 24-hour format corresponding to the timezone specified in the timezone
                                parameter (default America/New_York). Weather data will be retrieved through the
                                hour specified here and starting with the hour in hour_start (default 23)

        :param day_format:      str(), datetime format for parameter day. https://strftime.org/

        :param timezone:        str(), Open Meteo API timezone utilized for hour parameter (default America/New_York).
                                See timezone options here: https://open-meteo.com/en/docs

        :param stadium_name:    str(), optional, If provided, will utilize this parameter instead of team parameter to
                                retrieve stadium information.
        """
        base_url = "https://api.open-meteo.com/v1/forecast"

        if stadium_name is not None:
            coords = self.get_stadium_coordinates_by_name(stadium_name)
        else:
            coords = self.get_stadium_coordinates_by_team(team)

        lat = coords['lat']
        lon = coords['lon']

        
        start_datetime_str = f"{day} {hour_start}:00:00"
        end_datetime_str = f"{day} {hour_end}:00:00"
        start_datetime_obj = tC.convert_string_to_datetime(start_datetime_str, f"{day_format} %H:%M:%S")
        end_datetime_obj = tC.convert_string_to_datetime(end_datetime_str, f"{day_format} %H:%M:%S")
        start_date = tC.convert_date_to_string(start_datetime_obj, "%Y-%m-%dT%H:00:00Z")
        end_date = tC.convert_date_to_string(end_datetime_obj, "%Y-%m-%dT%H:00:00Z")

        params = {
            'latitude': lat,
            'longitude': lon,
            'hourly': 'temperature_2m,apparent_temperature,precipitation_probability,precipitation,rain,'
                      'showers,snowfall,snow_depth,wind_speed_10m,wind_speed_80m,wind_direction_10m,cloud_cover,'
                      'wind_direction_10m,wind_direction_80m,wind_gusts_10m,weather_code,visibility,is_day',
            'temperature_unit': 'fahrenheit',
            'wind_speed_unit': 'mph',
            'precipitation_unit': 'inch',
            'start_date': start_date.split('T')[0],
            'end_date': end_date.split('T')[0],
            'timezone': timezone
        }

        response = rC.make_request(base_url, params=params)

        if response.status_code == 200:
            weather_data = response.json()

            indices = []
            re_structure = False
            for i, t in enumerate(weather_data['hourly']['time']):
                tc = tC.convert_string_to_datetime(t, '%Y-%m-%dT%H:%M')
                if start_datetime_obj <= tc <= end_datetime_obj:
                    indices.append(i)
                else:
                    re_structure = True

            if re_structure:
                for key in weather_data['hourly']:
                    new_list = [weather_data['hourly'][key][x] for x in indices]
                    weather_data['hourly'][key] = new_list.copy()

            return weather_data
        else:
            print(f"Error: Unable to get weather data. Status code: {response.status_code}")
            return None

