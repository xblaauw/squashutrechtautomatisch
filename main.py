username = 'xblaauw'
password = 'Tying-Breach-Hazing8'


from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime as dt
import pandas as pd
from time import sleep


# pick a date based on what day it is today
today = dt.date.today()
next_thursday = today+dt.timedelta(days=1) + dt.timedelta( (3-(today+dt.timedelta(days=1)).weekday()) % 7 )
next_tuesday = today+dt.timedelta(days=1) + dt.timedelta( (1-(today+dt.timedelta(days=1)).weekday()) % 7 )
if today.weekday == 1:
    date = next_tuesday
else:
    date = next_thursday

desired_time = dt.time(19)

# Set up the browser driver
driver = webdriver.Firefox()

# Navigate to the login page
url = 'https://squtrecht.baanreserveren.nl/?goto='
driver.get(url)

# Log in to the website
driver.find_element(by=By.NAME, value="username").send_keys(username)
driver.find_element(by=By.NAME, value='password').send_keys(password)
driver.find_element(by=By.CSS_SELECTOR, value='button').click()

# The next page is the reservation page, now we extract the data:
date_str = date.strftime('%Y-%m-%d')
date_url = f'https://squtrecht.baanreserveren.nl/reservations/public/{date_str}/sport/113'
driver.get(date_url)

# get info
table = driver.find_elements(by=By.CLASS_NAME, value='free')

timeslots = []
lanes = []
for free_timeslot in table:
    timeslots.append(free_timeslot.text)
    lanes.append(free_timeslot.get_property('slot'))

# manipulate info, get index of lane at desired time if available in table variable
availability = pd.Series([True for _ in range(len(timeslots))],index=pd.MultiIndex.from_arrays((timeslots, lanes)), name='available').to_frame()
availability['table_index'] = range(len(availability))
availability = availability.rename_axis(['timeslots', 'lanes'])

# select which lane and time if there are any:
availability_wide = availability['available'].unstack('lanes')
available_at_desired_time = availability_wide.loc[availability_wide.index == '19:00 - 19:45'].squeeze().dropna()

if len(available_at_desired_time) != 0:
    # select the back lanes first if multiple are available
    available_at_desired_time = available_at_desired_time.sort_index(ascending=False).head(1)

    chosen_lane = available_at_desired_time.index[0]
    chosen_time = available_at_desired_time.name

    table_index = availability.loc[pd.IndexSlice[chosen_time, chosen_lane], 'table_index']

    # click the selected item in the table
    table[table_index].click()

    # we land with the cursor in the "Speler 2" veld
    sleep(3)
    driver.find_element(by=By.CLASS_NAME, value='ms-search').send_keys('Jaron Heising')
    sleep(3)
    driver.find_element(by=By.ID, value='__make_submit').click()
    sleep(3)
    driver.find_element(by=By.ID, value='__make_submit2').click()

driver.quit()


