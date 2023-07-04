import requests 
import json
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import oracledb
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from multiprocessing import  Pool,freeze_support
from webdriver_manager.chrome import ChromeDriverManager

def scrape_odds(data):
    """Scrape the odds from different bookies for a specific game

    Args:
        data (Row): Data of the match to scrape

    Returns:
        Dictionary: Information of the game with a dictionary of the odds
    """

    # Scrape 1x2 odds
    base_url = data['Url']
    match_code = base_url.split("/")[-2]


    url = f"https://www.betexplorer.com/match-odds/{match_code}/0/1x2/"
    payload = {}
    headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Sec-Fetch-Site': 'same-origin',
    'Accept-Language': 'es-419,es;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Sec-Fetch-Mode': 'cors',
    'Host': 'www.betexplorer.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15',
    'Connection': 'keep-alive',
    'Referer': base_url,
    'Cookie': '_ga_JCVB9K4MPH=GS1.1.1685676505.59.1.1685676617.60.0.0; _hjAbsoluteSessionInProgress=0; _hjSession_3335891=eyJpZCI6IjdjMmJiOTRjLTAyNjgtNDEzZi1hMmRjLWY0YWVmOThmZTAxZCIsImNyZWF0ZWQiOjE2ODU2NzY1MDU5MTEsImluU2FtcGxlIjpmYWxzZX0=; _hjIncludedInSessionSample_3335891=0; cto_bundle=VqNBI180c3Y5a3dxdmxIbWtGbkgzRnZxblJhRlVlRVJzZmtnaExveDk2T3UzbXgySGtSVlFIODh5WEloR2FDMzRjTCUyRjlCTFJVMXVmcnE0aHNyTjJnaDRqSmhlTmRRcW1OQ1JyZmxtV2d6dEhIenlJOE15VTdPSDBVWTNLM3QlMkI1ZVlJSmkxZU9Mb1JaeVd4bkdaTVhDaDhRamF0YUExOW56QU1LMVJYYVVCQk11TEg4JTNE; OptanonConsent=consentId=c73fdd65-a508-4e23-914e-1d2fef85b0f7&datestamp=Thu+Jun+01+2023+23%3A28%3A45+GMT-0400+(hora+de+verano+oriental)&version=202210.1.0&interactionCount=2&isGpcEnabled=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1%2CSTACK42%3A1&AwaitingReconsent=false&geolocation=US%3BFL; _ga=GA1.1.949265335.1682828444; _gid=GA1.2.1149246535.1685676506; _hjSessionUser_3335891=eyJpZCI6IjJlODY3MzQ2LTVhODItNTkxNS1iYzE3LWI2ODQ4NmE2YjIwNyIsImNyZWF0ZWQiOjE2ODI4Mjg0NDM5MjYsImV4aXN0aW5nIjp0cnVlfQ==; _session_UA-191939-1=true; eupubconsent-v2=CPrCw2APrCw2AAcABBENDGCsAP_AAAAAAChQJGtf_X__b2_j-_5_f_t0eY1P9_7_v-0zjhfdl-8N2f_X_L8X52M7vF36pq4KuR4ku3LBIQVlHOHcDUmw6okVryPsbk2cr7NKJ7PEmnMbO2dYGH9_n13T-ZKY7___f__z_v-v________7-3f3__p___-2_e_V_99zfn9_____9vP___9v-_9_3gAAAAAAAAAAAAD4AAABwkAIAGgC8xUAEBeYyACAvMdAEABoAGYAZQC8yEAIAMwAyiUAMAMwAygF5lIAgANAAzADKAXmAAA.f_gAAAAAAAAA; js_cookie=1; page_cached=1; nr_sort=2; my_timezone=-5; om-b=40; om-d=2; om-h=24; upcoming=1-6%2C1-8%2C1-198%2C1-81%2C1-98%2C2-5724%2C2-5725%2C4-8%2C4-6%2C4-200%2C3-6%2C3-200%2C7-6%2C7-81%2C12-6%2C12-8%2C12-106%2C6-200%2C6-100%2C6-106%2C1-200%2C3-200%2C4-200%2C6-200%2C12-200%2C1-53%2C1-176; infobox-next2=1; infobox-next1=1; OptanonAlertBoxClosed=2023-04-30T04:20:51.955Z; my_cookie_hash=bd9343a5cea7525e14bbc9fc8be7d95e; my_cookie_id=264753861',
    'Sec-Fetch-Dest': 'empty',
    'X-Requested-With': 'XMLHttpRequest'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response = json.loads(response.text)
    soup = BeautifulSoup(response['odds'], 'html.parser')

    # Find the table with odds
    table = soup.find('table', class_='table-main')

    # Find all rows within the table body
    rows = table.tbody.find_all('tr')

    odds_1x2 = {}


    # Extract bookmaker names and odds from each row
    for row in rows:
        try:
            # Find the bookmaker name
            bookmaker = row.find('a').text

            # Find the odds for Home Win (1), Draw (X), and Away Win (2)
            odds_row = row.find_all('td', class_='table-main__detail-odds')
            odds_values = [float(odd['data-odd']) for odd in odds_row]
            
            odds_1x2[bookmaker] = odds_values
        except:
            continue
    
    result = {
        'Date':data['Date']
        ,'Time' : data['Time']
        ,'Tournament' : data['Tournament']
        ,'Url' : data["Url"]
        ,'Match': data["Match"]
        ,'Odds_1x2':odds_1x2
    }

    try:
        # Scrape btts odds
        url = f"https://www.betexplorer.com/match-odds/{match_code}/0/bts/"
        headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Sec-Fetch-Site': 'same-origin',
        'Accept-Language': 'es-419,es;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-Fetch-Mode': 'cors',
        'Host': 'www.betexplorer.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15',
        'Connection': 'keep-alive',
        'Referer': base_url,
        'Cookie': '_ga_JCVB9K4MPH=GS1.1.1685676505.59.1.1685676617.60.0.0; _hjAbsoluteSessionInProgress=0; _hjSession_3335891=eyJpZCI6IjdjMmJiOTRjLTAyNjgtNDEzZi1hMmRjLWY0YWVmOThmZTAxZCIsImNyZWF0ZWQiOjE2ODU2NzY1MDU5MTEsImluU2FtcGxlIjpmYWxzZX0=; _hjIncludedInSessionSample_3335891=0; cto_bundle=VqNBI180c3Y5a3dxdmxIbWtGbkgzRnZxblJhRlVlRVJzZmtnaExveDk2T3UzbXgySGtSVlFIODh5WEloR2FDMzRjTCUyRjlCTFJVMXVmcnE0aHNyTjJnaDRqSmhlTmRRcW1OQ1JyZmxtV2d6dEhIenlJOE15VTdPSDBVWTNLM3QlMkI1ZVlJSmkxZU9Mb1JaeVd4bkdaTVhDaDhRamF0YUExOW56QU1LMVJYYVVCQk11TEg4JTNE; OptanonConsent=consentId=c73fdd65-a508-4e23-914e-1d2fef85b0f7&datestamp=Thu+Jun+01+2023+23%3A28%3A45+GMT-0400+(hora+de+verano+oriental)&version=202210.1.0&interactionCount=2&isGpcEnabled=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1%2CSTACK42%3A1&AwaitingReconsent=false&geolocation=US%3BFL; _ga=GA1.1.949265335.1682828444; _gid=GA1.2.1149246535.1685676506; _hjSessionUser_3335891=eyJpZCI6IjJlODY3MzQ2LTVhODItNTkxNS1iYzE3LWI2ODQ4NmE2YjIwNyIsImNyZWF0ZWQiOjE2ODI4Mjg0NDM5MjYsImV4aXN0aW5nIjp0cnVlfQ==; _session_UA-191939-1=true; eupubconsent-v2=CPrCw2APrCw2AAcABBENDGCsAP_AAAAAAChQJGtf_X__b2_j-_5_f_t0eY1P9_7_v-0zjhfdl-8N2f_X_L8X52M7vF36pq4KuR4ku3LBIQVlHOHcDUmw6okVryPsbk2cr7NKJ7PEmnMbO2dYGH9_n13T-ZKY7___f__z_v-v________7-3f3__p___-2_e_V_99zfn9_____9vP___9v-_9_3gAAAAAAAAAAAAD4AAABwkAIAGgC8xUAEBeYyACAvMdAEABoAGYAZQC8yEAIAMwAyiUAMAMwAygF5lIAgANAAzADKAXmAAA.f_gAAAAAAAAA; js_cookie=1; page_cached=1; nr_sort=2; my_timezone=-5; om-b=40; om-d=2; om-h=24; upcoming=1-6%2C1-8%2C1-198%2C1-81%2C1-98%2C2-5724%2C2-5725%2C4-8%2C4-6%2C4-200%2C3-6%2C3-200%2C7-6%2C7-81%2C12-6%2C12-8%2C12-106%2C6-200%2C6-100%2C6-106%2C1-200%2C3-200%2C4-200%2C6-200%2C12-200%2C1-53%2C1-176; infobox-next2=1; infobox-next1=1; OptanonAlertBoxClosed=2023-04-30T04:20:51.955Z; my_cookie_hash=bd9343a5cea7525e14bbc9fc8be7d95e; my_cookie_id=264753861',
        'Sec-Fetch-Dest': 'empty',
        'X-Requested-With': 'XMLHttpRequest'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        response = json.loads(response.text)
        soup = BeautifulSoup(response['odds'], 'html.parser')

        # Find the table with odds
        table = soup.find('table', class_='table-main')

        # Find all rows within the table body
        rows = table.tbody.find_all('tr')

        odds_bts = {}


        # Extract bookmaker names and odds from each row
        for row in rows:
            try:
                # Find the bookmaker name
                bookmaker = row.find('a').text

                # Find the odds for Home Win (1), Draw (X), and Away Win (2)
                odds_row = row.find_all('td', class_='table-main__detail-odds')
                odds_values = [float(odd['data-odd']) for odd in odds_row]
                
                odds_bts[bookmaker] = odds_values
            except:
                continue
        # Print the extracted bookmakers and odds
        result['Odds_bts'] = odds_bts
    except:
        result['Odds_bts'] = {}
    
    return result

def expected_value(result,market):   
    """Calculate the expected value of a bet and return a bet if there is value

    Args:
        result (dictionary): Information of the match and the odds

    Returns:
        List: list with the information of the bet
    """
    if market == "1x2":
        odds_dictionary = result['Odds_1x2']
        labels=["Home","Draw",'Away']
    elif market =="bts":
        odds_dictionary = result['Odds_bts']
        labels=["bts-yes","bts-no"]
    try:
        pinnacle_odds = odds_dictionary.get("Pinnacle")
        if pinnacle_odds:
            probabilities = [1/float(o) for o in pinnacle_odds]
            probabilities = [float(i)/sum(probabilities) for i in probabilities]
            
            # Calculate the expected value for each outcome and each bookmaker
            evs = {}
            for bookmaker, odds in odds_dictionary.items():
                if bookmaker!='Pinnacle':
                    ev = [probabilities[i]*float(odds[i]) - 1 for i in range(len(odds))]
                    evs[bookmaker] = {label: value for label, value in zip(labels, ev)}
            
            # Determine the bookmaker and outcome with the highest expected value
            max_ev = -math.inf
            for bookmaker, outcomes in evs.items():
                for outcome, ev in outcomes.items():
                    if ev > max_ev:
                        max_ev = ev
                        max_bookie = bookmaker
                        max_outcome = outcome
            if max_ev >= 0.01:
                # Calculate the suggested stake using Kelly criterion
                bookie_probs = [float(1/o )for o in odds_dictionary[max_bookie]]
                norm_factor = sum(bookie_probs)
                bookie_probs = [p / norm_factor for p in bookie_probs]

                suggested_prob = probabilities[labels.index(max_outcome)]
                suggested_odds = round(odds_dictionary[max_bookie][labels.index(max_outcome)],2)

                P = suggested_prob
                Q = 1-suggested_prob
                B = suggested_odds -1
                kelly_fraction = (B*P-Q)/B
            

                bet = [
                    result['Date']
                    ,result['Time']
                    ,result['Tournament']
                    ,result['Url']
                    ,result["Match"]
                    ,max_outcome
                    ,max_bookie
                    ,suggested_odds
                    ,kelly_fraction
                    ,max_ev
                    ,suggested_prob
                    ,''
                    ,market
                ]
            
                return bet
            else:
                pass
        else:
            pass
    except:
        pass

@st.cache_resource
def scrape_date(day,month,year):
    #driver_path = '/Users/danielguerrero/chromedriver.exe'
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu') 

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

    # Navigate to a webpage
    driver.get(f'https://www.betexplorer.com/next/football/?year={year}&month={month}&day={day}')

    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="onetrust-accept-btn-handler"]'))).click()
    except Exception as e:
        pass
    
    try:
        timezone = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "js-timezone")))
        timezone.click()

        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.ID, "onetrust-button-group")))

        zone =  WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick,'-5')]")))
        driver.execute_script("arguments[0].click();", zone)
    except:
        pass  

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # Close the webdriver
    driver.quit()



    table = soup.find('table', attrs={'class':"table-main js-nrbanner-t"})
    rows = table.find_all('tr')
    tournament= None

    data = []

    for _,row in enumerate(rows):
        try:
            new_tournament = row.find('a',class_='table-main__tournament').text
            tournament = new_tournament
        except:
            pass

        match_elements = row.find_all('span')
        try:
            time_ = match_elements[0].text
            home = match_elements[1].text
            away = match_elements[2].text
            match = ' - '.join([home,away])
            url = 'https://www.betexplorer.com'+row.find('a')['href']
        
            odds_element = row.find_all("td",class_="table-main__odds")
            odds  = [x.find("a").text if x.find("a").text else x.find("a")['data-odd'] for x in odds_element]
            
            raw_data=[tournament,time_,home,away,url,odds[0],odds[1],odds[2]]

            if 'data-live-cell' not in match_elements[0].attrs:
                data.append(raw_data)
        except:
            continue

    matches = pd.DataFrame(data,columns=['Tournament','Time','Home','Away','Url','1','x','2'])
    matches["Date"] = f'{day}/{month}/{year} ' + matches['Time'] 
    matches['Match'] = matches['Home'] + ' - ' + matches['Away']
    return matches


@st.cache_resource
def add_row(Date_, Time_, Tournament, Url_, Match_, Bet, Bookie, Odd, Stake, Result_, EV, Probability, Market):
    # Establish a connection to the database
    connection = oracledb.connect(user=st.secrets["username"], password=st.secrets["password"], dsn=st.secrets["connect_string"])

    # Create a cursor object
    cursor = connection.cursor()

    # Define the match and market values to check if they already exist
    match_value = Match_
    market_value = Market
    # Check if the combination of match and market already exists
    cursor.execute("""
        SELECT 1 FROM betlog
        WHERE Match_ = :match_value AND Market = :market_value
    """, {'match_value': match_value, 'market_value': market_value})

    if not cursor.fetchone():
        # Insert a new row if the combination doesn't exist
        cursor.execute("""
            INSERT INTO betlog (Date_, Time_, Tournament, Url_, Match_, Bet, Bookie, Odd, Stake, EV, Probability,Outcome, Market)
            VALUES (:Date_, :Time_, :Tournament, :Url_, :Match_, :Bet, :Bookie, :Odd, :Stake,  :EV, :Probability,:Result_, :Market)
        """, {'Date_': Date_, 'Time_': Time_, 'Tournament': Tournament, 'Url_': Url_, 'Match_': Match_, 'Bet': Bet, 'Bookie': Bookie, 'Odd': Odd, 'Stake': Stake, 'Result_': Result_,  'EV': EV, 'Probability': Probability, 'Market': Market})
        connection.commit()
    else:
        pass

    # Close the cursor and the database connection
    cursor.close()
    connection.close()


@st.cache_resource
def update_outcome(tournament, match, market, outcome):
    # Establish a connection to the database
    conn = oracledb.connect(user=st.secrets["username"], password=st.secrets["password"], dsn=st.secrets["connect_string"])
    cursor = conn.cursor()

    query = """
        UPDATE betlog
        SET Outcome = :outcme
        WHERE Tournament = :dt AND Match_ = :mtch AND Market = :mrkt
    """
    cursor.execute(query, outcme=outcome, dt=tournament, mtch=match, mrkt=market)
    conn.commit()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()


def show_table():
    conn = oracledb.connect(user=st.secrets["username"], password=st.secrets["password"], dsn=st.secrets["connect_string"])
    sql = "SELECT * FROM BETLOG"
    df = pd.read_sql(sql,conn)
    conn.close()

    return(df)

    
@st.cache_resource
def create_bets(matches):
    freeze_support()
    with Pool() as pool:
        result = pool.starmap(scrape_odds, [(row,) for _,row in matches[['Date','Time','Tournament','Url','Match']].iterrows()])
        # Apply the expected_value function to the results
        expected_values = []
        expected_values_1x2 = pool.starmap(expected_value,[(x,"1x2") for x in result])
        expected_values_bts = pool.starmap(expected_value,[(x,"bts") for x in result])

        expected_values.extend(expected_values_1x2)
        expected_values.extend(expected_values_bts)
        bets = pd.DataFrame([x for x in expected_values if x],columns=['Date','Time','Tournament','Url','Match','Bet','Bookie','Odd','Stake','Ev','Probability','Outcome','Market'])
    return bets

def find_outcome(url,market,bet):

        try:
            response = requests.get(url)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            score = soup.find(id="js-score")
            score_text = score.text if score else None
            home = score_text.split(':')[0]
            away = score_text.split(':')[1]
            if home=='-' and away=='-':
                outcome=None
            else:
                if market =='1x2':
                    if home>away:
                        outcome='Home'
                    elif away>home:
                        outcome='Away'
                    elif away==home:
                        outcome='Draw'
                    else:
                        outcome=None
                elif market=='bts':
                    if (float(home)>0) and (float(away)>0):
                        outcome='btts-yes'
                    elif (float(home)==0) | (float(away)==0):
                        outcome='btts-no'
                    else:
                        outcome=None
                elif market=='OU':
                    over_under = bet.split('-')[0]
                    bet_goals = float(bet.split('-')[1])
                    total_goals = float(home) + float(away)
                    if ((over_under=='O') and (total_goals>bet_goals)) | ((over_under=='U') and (total_goals<bet_goals)):
                        outcome =bet 
                    else:
                        outcome= 'Incorrect'
        except Exception as e:
            outcome=None
        
        return outcome