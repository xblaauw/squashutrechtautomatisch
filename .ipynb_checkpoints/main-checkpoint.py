username = 'xblaauw'
password = 'Tying-Breach-Hazing8'


from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import datetime as dt
import pandas as pd
from time import sleep


# pick a date based on what day it is today
today = dt.date.today()
desired_date = today
desired_time = dt.time(18, 45)

# Set up the browser driver
driver_options = Options()
driver_options.add_argument("--headless")
driver = webdriver.Firefox(options=driver_options)

# Navigate to the login page
url = 'https://squtrecht.baanreserveren.nl/?goto='
driver.get(url)

# Log in to the website
driver.find_element(by=By.NAME, value="username").send_keys(username)
driver.find_element(by=By.NAME, value='password').send_keys(password)
driver.find_element(by=By.CSS_SELECTOR, value='button').click()

# The next page is the reservation page, now we extract the data:
date_str = desired_date.strftime('%Y-%m-%d')
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
availability = pd.Series(
    [True for _ in range(len(timeslots))],
    index=pd.MultiIndex.from_arrays((timeslots, lanes)), 
    name='available'
).to_frame()
availability['table_index'] = range(len(availability))
availability = availability.rename_axis(['timeslots', 'lanes'])

# select which lane and time if there are any:
availability_wide = availability['available'].unstack('lanes')
availability_wide = availability_wide.drop('76', axis=1)
print(availability_wide.to_string())

def parse_availability_times(times):
    return times.to_series().apply(lambda x: pd.to_datetime(x[:5]).time())
    
start_times = parse_availability_times(availability_wide.index)
available_at_desired_time = availability_wide.loc[start_times == desired_time].squeeze().dropna()

try:
    # select the back lanes first if multiple are available
    chosen_lane = available_at_desired_time.sort_index(ascending=False).head(1).index[0]

    table_index = availability.xs(chosen_lane, level='lanes')
    table_index = table_index.loc[parse_availability_times(table_index.index)==desired_time, 'table_index']
    
    print(
        '\ndesired_date: ', desired_date, 
        '\ndesired_time: ', desired_time, 
        '\nchosen_lane: ', chosen_lane, 
        '\ntable_index: ', table_index.squeeze()
    )

    # click the selected item in the table
    table[table_index.squeeze()].click()

    # we land with the cursor in the "Speler 2" veld
    sleep(3)
    driver.find_element(by=By.CLASS_NAME, value='ms-search').send_keys('Jaron Heising')
    sleep(3)
    driver.find_element(by=By.ID, value='__make_submit').click()
    sleep(3)
    driver.find_element(by=By.ID, value='__make_submit2').click()
    
    print('SUCCESS!')
except Exception as e:
    driver.quit()
    raise e


