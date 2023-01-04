import config
import socket
import time
import random
import datetime
from datetime import date
from gpiozero import CPUTemperature
import requests
import json
import ISS_Info
import os
from bs4 import BeautifulSoup
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

def chat(sock, msg):
    if(type(msg) == str):
        sock.send(("PRIVMSG {} :{}\r\n".format(config.CHAN, msg)).encode("UTF-8"))
    elif(type(msg) == list):
        for m in msg:
            sock.send(("PRIVMSG {} :{}\r\n".format(config.CHAN, m)).encode("UTF-8"))
    time.sleep(1 / config.RATE)

def report_in(msg):
    return "Reporting *hic* in! [" + u'\U0001F40D' + "] https://cr0s.is/cr0bot.php"

def check_time(msg):
    curr_time = time.strftime("%H:%M:%S", time.localtime())
    return curr_time

def temp(msg):
    cpu = CPUTemperature()
    return "Temp: " + str(round(cpu.temperature, 1)) + "°C"

def check_date(msg):
    today = date.today()
    d2 = today.strftime("%B %d, %Y")
    return d2 

def moon(msg):
    url = 'https://www.timeanddate.com/moon/phases/'
    response = requests.get(url, headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    percent = soup.select_one('#cur-moon-percent')
    percent_value = float(percent.text.replace('%', ''))  # Remove the % symbol
    percent_value = round(percent_value)
    if percent_value < 5:
       return u'\U0001F311' 
    elif percent_value < 35:
       return u'\U0001F312'
    elif percent_value < 65:
        return u'\U0001F313'
    elif percent_value < 95:
        return u'\U0001F314'
    else:
        return u'\U0001F315'

def random_choice(msg):
    u = msg["user"]
    m = msg["message"]
    try:
        # Split the string into a list of words
        words = m.split()
        # Get the part of the list that contains the words before the | character
        first_option = words[1]
        # Get the part of the list that contains the words after the | character
        second_option = words[3]
        chosen_string = random.choice([first_option, second_option])
        return chosen_string
    except Exception as e:
        print(str(e))
        return "Not enough parameters: !random word | word"


def jumble(msg):
    word = str("GINGER")
    word = list(word)  # Convert the word to a list of characters
    random.shuffle(word)  # Shuffle the list of characters
    return ''.join(word)  # Join the list of characters back into a string and return it

def ISS(msg):
    location = ISS_Info.iss_current_loc()
    latitude = location['iss_position']['latitude']
    longitude = location['iss_position']['longitude']
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
    response = requests.get(url)
    data = response.json()
    try:
        return "Flying over: " + (data["address"]["country"])
    except Exception as e:
        url = f"https://geocode.xyz/{latitude},{longitude}?json=1"
        response = requests.get(url)
        data = response.json()
        try:
            return "Flying over: " + (data["suggestion"]["subregion"])
        except Exception as e:
            return "Ocean info not found. Pos: " + str(latitude) + "," + str(longitude)
            print(str(e))

def lenny(msg):
    return (f"( ?° ?? ?°)")

def dogs(msg):
    url = "https://dog.ceo/api/breeds/image/random"
    response = requests.get(url)
    data = response.json()
    try:
        return data["message"]
    except Exception as e:
        return str(e)

def fox(msg):
    url = "https://randomfox.ca/floof/"
    response = requests.get(url)
    data = response.json()
    try:
        return data["image"]
    except Exception as e:
        return str(e)

def duck(msg):
    url = "https://random-d.uk/api/random"
    response = requests.get(url)
    data = response.json()
    try:
        return data["url"]
    except Exception as e:
        return str(e)

def bankhol(msg):
    response = requests.get('https://www.gov.uk/bank-holidays.json')
    data = response.json()
    now = datetime.datetime.now()
    next_holiday = None
    for holiday in data['england-and-wales']['events']:
        holiday_date = datetime.datetime.strptime(holiday['date'], '%Y-%m-%d')
        if holiday_date > now:
            next_holiday = holiday
            break
    if next_holiday:
        return (f'The next bank holiday is {next_holiday["title"]} on {next_holiday["date"]} {next_holiday["notes"]}')
    else:
        return 'There are no more bank holidays this year.'

def read_json_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def write_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def get_stats(msg):
    data = read_json_file('dice_rolls.json')
    total_rolls = data['total_rolls']
    lowest_score = data['lowest_score']
    lowest_score_user = data['lowest_score_user']
    best_scores = data['best_scores']
    message = f"Total rolls: {total_rolls} Best roll: {lowest_score_user} with {lowest_score}\n"
    return message

def roll_dice(msg):
    u=msg["user"]
    m=msg["message"]
    dice=[] # Initialize an empty list to store the dice rolls
    for i in range(7):
        roll=random.randint(1, 6)
        if roll==1:
            dice.append("\x0313,15" + str(roll))
        else:
            dice.append("\x0301,15" + str(roll)) 
        dice_str=" ".join(dice)
        int_dice=[int(x[6:]) for x in dice] 
        if i==6:
            newrecord=False
            sum_dice=sum(int_dice)
            dice_str="\x0301,15-".join(dice)
            
            # Read data from JSON file
            data = read_json_file('dice_rolls.json')

            # Increment total number of rolls
            data['total_rolls'] += 1

            # Update lowest score and user with lowest score
            if sum_dice < data['lowest_score']:
                data['lowest_score'] = sum_dice
                data['lowest_score_user'] = u
                newrecord=True
            # Update best score for current user
            if u not in data['best_scores'] or sum_dice < data['best_scores'][u]:
                data['best_scores'][u] = sum_dice

            # Write updated data to JSON file
            write_json_file('dice_rolls.json', data)
            dice_list = [dice_str + "\x03 " + u + "\x03 rolled: \x0307" + str(sum_dice)]
            if not newrecord:
                return dice_list
            else:
                dice_list.append("omg " + u + " broke the record!!")
                return dice_list
