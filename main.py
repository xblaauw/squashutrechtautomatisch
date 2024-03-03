print('STARTIG SCRIPT...')

username = 'xblaauw'
password = 'Tying-Breach-Hazing8'
DEV = False
print('devmode', DEV)

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import datetime as dt
import pandas as pd
from time import sleep
from random import randint
import logging


now = dt.datetime.now()
log_filename = f"logs/{now:%Y%m%d%H%M%S}.log"
log_format   = '%(name)s - %(levelname)s - %(message)s'
log_level    = logging.INFO

logging.basicConfig(filename=log_filename, filemode='w', format=log_format, level=log_level)

console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
console_handler.setFormatter(logging.Formatter(log_format))
logging.getLogger('').addHandler(console_handler)


if not DEV: 
    wait_min = 0
    wait_random_sec = randint(0, wait_min*60)
    logging.info(f'waiting {wait_random_sec} seconds')
    sleep(wait_random_sec)


logging.info('making dates')
today = dt.date.today()
desired_date = today + dt.timedelta(days=7)
desired_time = dt.time(19, 00)

logging.info('setting up driver')
driver_options = Options()
driver_options.binary_location = "/usr/locall/bin/geckodriver"

if not DEV: 
    logging.info('driver_options.add_argument("--headless")')
    driver_options.add_argument("--headless")
driver = webdriver.Firefox(options=driver_options)

logging.info('going to login page')
url = 'https://squtrecht.baanreserveren.nl/?goto='
driver.get(url)

logging.info('finding uname and pw')
driver.find_element(by=By.NAME, value="username").send_keys(username)
driver.find_element(by=By.NAME, value='password').send_keys(password)
driver.find_element(by=By.CSS_SELECTOR, value='button').click()

logging.info('getting table data')
date_str = desired_date.strftime('%Y-%m-%d')
date_url = f'https://squtrecht.baanreserveren.nl/reservations/public/{date_str}/sport/113'
driver.get(date_url)

logging.info('extracting table data')
table = driver.find_elements(by=By.CLASS_NAME, value='free')

timeslots = []
lanes = []
for free_timeslot in table:
    timeslots.append(free_timeslot.text)
    lanes.append(free_timeslot.get_property('slot'))

logging.info('building availability dataframe')
availability = pd.Series(
    [True for _ in range(len(timeslots))],
    index=pd.MultiIndex.from_arrays((timeslots, lanes)), 
    name='available'
).to_frame()
availability['table_index'] = range(len(availability))
availability = availability.rename_axis(['timeslots', 'lanes'])

logging.info('filtering availability dataframe')
availability_wide = availability['available'].unstack('lanes')
availability_wide = availability_wide.drop('76', axis=1)

def parse_availability_times(times):
    return times.to_series().apply(lambda x: pd.to_datetime(x[:5]).time())
   
logging.info('parsing availability')
start_times = parse_availability_times(availability_wide.index)
available_at_desired_time = availability_wide.loc[start_times == desired_time].squeeze().dropna()

logging.info('determining if there is a room at desired time')
available_at_desired_time_print = available_at_desired_time.copy()
available_at_desired_time_print.index = available_at_desired_time_print.index.astype(int) - 121

lane_rank = pd.Series({
    '127': 0,
    '126': 1,
    '128': 2,
    '125': 3,
    '129': 4,
    '124': 5,
    '130': 6,
    '123': 7
}).sort_values()

logging.info('chosing a lane if there is one')
chosen_lane = None
for lane, rank in lane_rank.items():
    if available_at_desired_time.index.isin([lane]).any():
        chosen_lane = lane
        break

if chosen_lane is None:
    logging.info('NO LANES AVAILABLE', 'stopping program...')
    driver.quit()
    exit()

logging.info(f'chosen_lane={int(chosen_lane)-121}')


logging.info('getting corresponding table index')
table_index = availability.xs(chosen_lane, level='lanes')
table_index = table_index.loc[parse_availability_times(table_index.index)==desired_time, 'table_index']

logging.info('clicking table cell')
table[table_index.squeeze()].click()

logging.info(f'waiting 3 seconds')
sleep(3)

logging.info('adding jaron')
driver.find_element(by=By.CLASS_NAME, value='ms-search').send_keys('Jaron Heising')
logging.info(f'waiting 8 seconds')
sleep(8)

logging.info('clicking button 1')
driver.find_element(by=By.ID, value='__make_submit').click()
logging.info(f'waiting 8 seconds')
sleep(8)

if not DEV:
    logging.info('clicking button 1')
    driver.find_element(by=By.ID, value='__make_submit2').click()


logging.info(f'''
{desired_date=}
{desired_time=}
chosen_lane: {int(chosen_lane)-121}
''')

logging.info('all done')