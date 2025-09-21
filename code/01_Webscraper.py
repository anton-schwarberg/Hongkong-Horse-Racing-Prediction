from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import sys

def get_dates(start, end):
    delta = timedelta(days=1)

    date_list = []
    current = start
    while current <= end:
        formatted_date = current.strftime('%Y/%m/%d')
        date_list.append(formatted_date)
        current += delta
    return date_list

def page_checker(soup, scrape, url):
    try:
        content = soup.find('span', class_='f_fl f_fs13')
        if scrape.status_code != 200:
            return False
        if not content:
            return False
        try:
            teile = content.get_text(strip=True).split('\xa0')
            date = teile[1].strip() if len(teile)>1 else None
            location = teile[3].strip() if len(teile)>3 else None
            if date == "16/07/2025" and location == "Happy Valley":
                return False
        except Exception as e:
            print(f"Error extracting date/location in page_checker: {e}")
        try:
            if soup.find('span', class_='f_fl f_fs13'):
                parts = soup.find_all('span', attrs={'class':'f_fl f_fs13'})
                location = parts[0].get_text(strip=True).split('\xa0')[3].strip() if len(parts)>0 else None
                return race_sub_scraper(url, location)
        except Exception as e:
            print(f"Error calling race_sub_scraper in page_checker: {e}")
        if soup.find('div', id='errorContainer'):
            return False
        return False
    except Exception as e:
        print(f"Error in page_checker: {e}")
        return False
    
    # Check if the race number subpage exists
def raceno_checker(soup):
    message = "Information will be released shortly."
    result = message in soup.get_text()
    return result
# returns True if the number doesnt exists

def info_scraper(soup):
    try:
        try:
            race_no = soup.find('tr', attrs={'class':'bg_blue color_w font_wb'}).get_text(strip=True)
        except Exception as e:
            print(f"Error extracting race_no: {e}")
            race_no = None

        try:
            information = soup.find_all('span', attrs={'class':'f_fl f_fs13'})
            teile = information[0].get_text(strip=True).split('\xa0')
            date = teile[1].strip() if len(teile)>1 else None
            location = teile[3].strip() if len(teile)>3 else None
        except Exception as e:
            print(f"Error extracting date/location: {e}")
            date = None
            location = None

        race_info = {
            'date': date,
            'location': location,
            'race_no': race_no
        }

        try:
            table = soup.find_all('div', attrs={'class':'race_tab'})
            elements = table[0].find_all('td') if len(table)>0 else []
            el_list = []
            for element in elements:
                if len(element) >0 :
                    el_list.append(element.get_text(strip=True))
            final_dict = {
                'info':el_list[1] if len(el_list)>1 else None,
                'going':el_list[3] if len(el_list)>3 else None,
                'course':el_list[6] if len(el_list)>6 else None
            }
            sec_start = el_list.index('Time :') + 1 if 'Time :' in el_list else None
            sec_end = el_list.index('Sectional Time :') if 'Sectional Time :' in el_list else None
            sec_values = el_list[sec_start:sec_end] if sec_start is not None and sec_end is not None else []
            sec_dict = {f'sec{i+1}': val for i, val in enumerate(sec_values)}
        except Exception as e:
            print(f"Error extracting table/sectional times: {e}")
            final_dict = {}
            sec_dict = {}

        race_info.update(final_dict)
        race_info.update(sec_dict)

        return race_info
    except Exception as e:
        print(f"Error in info_scraper: {e}")
        return {}

def HR_scraper(soup):
    try:
        try:
            table = soup.find_all('tbody', attrs={'class':'f_fs12'})
            first_table = table[0]
            rows = first_table.find_all('tr')
        except Exception as e:
            print(f"Error extracting table/rows: {e}")
            return []

        results_data = []
        for row in rows:
            try:
                element = row.find_all('td')
                row_data = {
                    "place": element[0].get_text(strip=True) if len(element)>0 else None,
                    "horse_number": element[1].get_text(strip=True) if len(element)>1 else None,
                    "horse_name": element[2].get_text(strip=True) if len(element)>2 else None,
                    "jockey": element[3].get_text(strip=True) if len(element)>3 else None,
                    "trainer": element[4].get_text(strip=True) if len(element)>4 else None,
                    "weight": element[5].get_text(strip=True) if len(element)>5 else None,
                    "on_date_horse_weight": element[6].get_text(strip=True) if len(element)>6 else None,
                    "draw": element[7].get_text(strip=True) if len(element)>7 else None,
                    "length_behind_winner": element[8].get_text(strip=True) if len(element)>8 else None,
                    "running_position": element[9].get_text(strip=True) if len(element)>9 else None,
                    "finish_time": element[10].get_text(strip=True) if len(element)>10 else None,
                    "win_odds": element[11].get_text(strip=True) if len(element)>11 else None
                }
                results_data.append(row_data)
            except Exception as e:
                print(f"Error extracting row data: {e}")
                continue
        return results_data
    except Exception as e:
        print(f"Error in HR_scraper: {e}")
        return []

def race_sub_scraper(url, location):
    i = 1
    end = False
    loc_dict = {
        'Happy Valley': 'HV',
        'Sha Tin': 'ST'
    }
    loc = loc_dict.get(location)
    all_data = []

    while end == False:
        try:
            sub_url = f"{url}&Racecourses={loc}&RaceNo={i}"
            req = requests.get(sub_url)
            soup = BeautifulSoup(req.text, "html.parser")
            end = raceno_checker(soup)
            time.sleep(random.uniform(1, 3))
            if not end:
                print(f"Scraping Race {i} ...")
                try:
                    info = info_scraper(soup)
                    results = HR_scraper(soup)
                    combined_data = [{**info, **observation} for observation in results]
                    all_data.extend(combined_data)
                except Exception as e:
                    print(f"Error scraping race {i}: {e}")
                i += 1
            else:
                print(f"Done with Race {i-1}")
        except Exception as e:
            print(f"Error in race_sub_scraper loop for Race {i}: {e}")
            break
    return all_data

#Execution Part

# Creating the date list

year = int(sys.argv[1]) # Enter the year you want to scrape here
# If you want to scrape multiple years, you can run the script multiple times with different year arguments
#It ist important that you combine the csv files afterwards to prepare them for preprocessing

start_date = datetime(year, 1, 1)
end_date = datetime(year, 12, 31)

dates = get_dates(start_date, end_date)

final_dict = []
for element in dates:
    try:
        url = f"https://racing.hkjc.com/racing/information/english/Racing/LocalResults.aspx?RaceDate={element}"
        print(f"Working on date {element}")
        scrape = requests.get(url)
        soup = BeautifulSoup(scrape.text, "html.parser")
        results = page_checker(soup, scrape, url)
        if results != False:
            final_dict.extend(results)
            print(f"{element} successfully added!")
        else:
            print(f"{results}: {element} is not scrapable")
    except Exception as e:
        print(f"Error scraping date {element}: {e}")
print("DONE")
print(f"Successfully scraped for year {year}")

file_name = f"HKHJC - {str(year)}.csv"

df = pd.DataFrame(final_dict)
df.to_csv(file_name, index=False)

print(f"Successfully scraped year {year}")
