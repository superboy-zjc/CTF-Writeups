#!/usr/bin/env python3
import requests
import time
import logging
import json
import asyncio
import aiohttp
from websockets.asyncio.client import connect
from requests.adapters import HTTPAdapter
import jwt 
import subprocess
import threading
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SOLVER")

# Replace with the actual URL of the server
endpoint = "dojo.challs.pwnoh.io"
session = requests.Session()
jwt_token = None
adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
session.mount('http://', adapter)
session.mount('https://', adapter)


player_health = 100
boss_health = 1000
plundered_total = 0

proxy_num = 0

proxy_lists = [
    "147.28.155.23:10001", "66.65.181.6:8080", "46.47.197.210:3128", "54.38.181.125:80", "141.147.9.254:80", "51.75.206.209:80",
    "34.81.160.132:80", "41.74.91.244:80", "196.223.129.21:80", "197.255.125.12:80", "78.28.152.111:80",
    "35.209.198.222:80", "34.81.72.31:80", "78.28.152.113:80", "137.184.100.135:80", "197.243.20.178:80",
    "203.57.51.53:80", "66.29.154.105:3128", "211.104.20.205:8080", "209.97.150.167:3128", "139.59.1.14:8080",
    "54.83.185.141:3128", "20.24.43.214:80", "66.29.154.103:3128", "20.206.106.192:8123", "20.111.54.16:8123",
    "20.210.113.32:8123", "188.166.56.246:80", "73.117.183.115:80", "43.133.59.220:3128", "43.153.207.93:3128",
    "38.54.95.19:8081", "92.60.190.79:3128", "102.130.125.86:80", "35.220.254.137:8080", "8.213.195.191:8095",
    "43.153.237.252:3128", "129.226.193.16:3128", "4.158.61.222:8080", "128.199.202.122:8080", "188.166.197.129:3128",
    "85.210.84.189:8080", "4.158.55.159:8080", "104.248.98.31:3128", "51.222.161.115:80", "4.158.175.186:8080",
    "185.240.49.141:8888", "20.26.97.150:8080", "85.210.203.188:8080", "35.198.189.129:8080", "40.76.69.94:8080",
    "37.46.135.225:3128", "79.101.37.78:3128", "67.43.227.226:30373", "133.18.234.13:80", "139.162.78.109:8080",
    "47.90.205.231:33333", "43.134.32.184:3128", "64.92.82.59:8080", "194.182.178.90:3128", "103.190.179.27:80",
    "43.134.1.40:3128", "43.134.33.254:3128", "114.129.2.82:8081", "72.10.160.91:8167", "223.135.156.183:8080",
    "188.40.59.208:3128", "47.88.31.196:8080", "31.44.7.32:8080", "159.65.245.255:80", "195.114.209.50:80",
    "85.214.195.118:80", "173.255.119.18:80", "81.200.149.178:80", "43.134.229.98:3128", "62.210.15.199:80",
    "142.44.210.174:80", "79.174.12.190:80", "5.75.130.49:80", "147.182.180.242:80", "149.202.91.219:80",
    "51.89.134.68:80", "193.34.144.169:80", "178.128.199.145:80", "13.80.134.180:80", "143.42.66.91:80",
    "162.223.116.54:80", "67.43.227.228:23737", "192.73.244.36:80", "213.16.31.0:80", "173.212.200.73:3128",
    "64.227.38.36:81", "93.127.163.52:80", "83.68.136.236:80", "103.127.1.130:80", "68.185.57.66:80",
    "50.172.75.114:80", "102.134.98.222:8081", "185.228.234.84:80", "123.30.154.171:7777", "51.89.255.67:80",
    "127.0.0.7:80", "103.26.108.254:84", "165.16.55.19:44444", "188.165.49.152:80", "38.45.246.210:999",
    "77.235.31.24:8080", "101.255.116.125:8080", "103.153.247.70:8080", "185.184.217.250:8099", "186.148.182.86:999",
    "45.123.142.46:8181", "103.130.130.179:8080", "45.231.220.78:999", "43.134.121.40:3128", "47.242.47.64:8888",
    "154.205.152.96:3128", "20.84.109.185:80", "117.54.114.96:80", "47.251.73.54:3128", "143.42.191.48:80",
    "217.112.80.252:80", "202.61.204.51:80", "85.210.121.11:8080", "51.89.134.69:80", "65.108.195.47:8080",
    "13.37.73.214:80", "85.92.108.55:8888", "43.255.113.232:8085", "23.137.248.197:80", "47.237.107.41:3128",
    "103.56.157.39:8080", "85.210.84.11:8080", "185.142.66.110:8080", "67.43.227.227:11023", "138.68.60.8:8080",
    "8.219.97.248:80", "63.143.57.119:80", "47.88.85.102:3389", "20.26.249.29:8080", "47.56.110.204:8989",
    "43.134.68.153:3128", "175.139.233.78:80", "158.255.77.169:80", "93.177.67.178:80", "41.204.53.17:80",
    "65.108.207.6:80", "41.169.69.91:3128", "41.204.53.30:80", "119.9.77.49:8080", "194.182.163.117:3128",
    "183.100.14.134:8000", "154.0.12.163:80", "37.27.6.46:80", "160.86.242.23:8080", "198.49.68.80:80",
    "47.250.156.92:80", "51.89.14.70:80", "82.102.10.253:80", "154.64.226.138:80", "85.215.64.49:80",
    "208.104.211.63:80", "50.217.226.41:80", "45.234.60.209:999", "198.44.255.3:80", "50.217.226.44:80",
    "50.231.104.58:80", "50.174.7.156:80", "50.207.199.81:80", "42.114.11.69:8080", "180.242.150.236:8080",
    "45.123.142.17:8181", "103.177.9.104:8080", "103.247.21.225:2024"
]

# valid_proxies = []

# proxy_lists = [
#   'http://147.28.155.23:10001',
#   'http://4.158.61.222:8080',
#   'http://43.134.68.153:3128',
#   'http://35.220.254.137:8080',
#   'http://43.153.237.252:3128',
#   'http://64.92.82.59:8080'
# ]

proxy_lists = ['http://147.28.155.23:10001', 'http://43.153.207.93:3128', 'http://43.134.32.184:3128', 'http://129.226.193.16:3128', 'http://104.248.98.31:3128', 'http://185.240.49.141:8888', 'http://43.134.229.98:3128', 'http://43.134.33.254:3128', 'http://64.92.82.59:8080', 'http://147.28.155.23:10001', 'http://188.166.197.129:3128', 'http://43.134.68.153:3128', 'http://43.133.59.220:3128', 'http://35.198.189.129:8080', 'http://185.240.49.141:8888', 'http://64.92.82.59:8080', 'http://104.248.98.31:3128', 'http://129.226.193.16:3128', 'http://43.134.32.184:3128', 'http://188.166.197.129:3128', 'http://43.134.33.254:3128', 'http://43.134.229.98:3128', 'http://85.210.84.11:8080', 'http://47.88.31.196:8080', 'http://43.134.121.40:3128', 'http://85.210.203.188:8080', 'http://43.134.68.153:3128', 'http://4.158.61.222:8080', 'http://147.28.155.23:10001', 'http://35.198.189.129:8080', 'http://185.240.49.141:8888', 'http://64.92.82.59:8080', 'http://104.248.98.31:3128', 'http://85.210.121.11:8080', 'http://4.158.175.186:8080', 'http://20.26.97.150:8080', 'http://43.134.33.254:3128', 'http://43.134.32.184:3128', 'http://85.210.121.11:8080', 'http://147.28.155.23:10001', 'http://43.134.68.153:3128', 'http://85.210.121.11:8080', 'http://85.210.203.188:8080', 'http://20.26.97.150:8080', 'http://4.158.175.186:8080', 'http://185.240.49.141:8888', 'http://104.248.98.31:3128', 'http://188.166.197.129:3128', 'http://35.198.189.129:8080', 'http://47.88.31.196:8080', 'http://85.210.84.189:8080', 'http://64.92.82.59:8080', 'http://4.158.61.222:8080', 'http://43.134.33.254:3128', 'http://43.134.229.98:3128', 'http://43.134.32.184:3128', 'http://8.219.97.248:80', 'http://147.28.155.23:10001']

def send_request_with_proxy_nowait(url):
  # rotate proxy
  global proxy_num
  id = (proxy_num) % len(proxy_lists)
  # proxy = f"http://{proxy_lists[id]}"
  proxy = proxy_lists[id]
  proxy_num += 1
  try:
    r = session.get(url, proxies={"https": proxy, "http": proxy})
    if r.status_code == 200:
      response = r.json()
      if response["status"] == "success":
        plundered_total = response["total"]
        logger.info(f"Plundered {response['amount']} emeralds. Total plundered: {plundered_total} with proxy {proxy}")
        # valid_proxies.append(proxy)
        # print(f"Valid proxies: {valid_proxies}")
      else:
        pass
    return r
  except Exception as e:
    # logger.error(f"Failed to send request with proxy {proxy}: {e}")
    return None
  

def new_game():
  url = f"https://{endpoint}/api/new"
  
  r = session.get(url, allow_redirects=False)

  if r.status_code == 307 and 'Set-Cookie' in r.headers:
    set_cookie_header = r.headers['Set-Cookie']
    logger.info(f"Set-Cookie header: {set_cookie_header}")

    global jwt_token
    jwt_token = set_cookie_header.split(';')[0].split('=')[1]
    
    session.cookies.set('jwt', jwt_token, path='/')
    logger.info(f"JWT token set in session: {jwt_token}")

  else:
    logger.warning(f"Failed to start a new game. Status: {r.status_code}")
    return None

def attack(wait):
  global plundered_total
  url = f"https://{endpoint}/api/attack"
  if wait:
    r = session.get(url)
    if r.status_code == 200:
      response = r.json()
      if response["status"] == "success":
        logger.info(f"Successfully attacked the boss for {response['amount']} damage.")
      else:
        pass
  else:
    thread = threading.Thread(target=send_request_with_proxy_nowait, args=(url,))
    thread.start()

def dodge():
  url = f"https://{endpoint}/api/dodge"
  r = session.get(url)
  if r.status_code == 200:
    response = r.json()
    if response["status"] == "success":
      logger.info("Successfully dodged the boss's attack.")
    else:
      logger.warning(f"Dodge failed: {response['message']}")
      pass

def plunder(wait):
  global plundered_total
  url = f"http://{endpoint}/api/plunder"
  if wait:
    r = session.get(url)
    if r.status_code == 200:
      response = r.json()
      if response["status"] == "success":
        plundered_total = response["total"]
        logger.info(f"Plundered {response['amount']} emeralds. Total plundered: {plundered_total}")
      else:
        pass
  else:
    thread = threading.Thread(target=send_request_with_proxy_nowait, args=(url,))
    thread.start()

def on_message(ws, message):
  global player_health, boss_health, plundered_total
  logger.info(f"Received message: {message}")
  response = json.loads(message)

  if response["action"] == "sync":
    player_health = response["playerHealth"]
    boss_health = response["bossHealth"]
    logger.info(f"Health sync: Player {player_health}, Boss {boss_health}")

  elif response["action"] == "boss_attack":
    logger.info(f"Boss attacked for {response['amount']} damage.")
    player_health -= response["amount"]
  
  elif response["action"] == "dodged":
    logger.info(f"Successfully dodged {response['amount']} damage.")

  elif response["action"] == "lose":
    logger.error(f"Game lost. Reason: {response['reason']}")
    ws.close()

  elif response["action"] == "win":
    logger.info("Congratulations, you won!")
    ws.close()

  elif response["action"] == "flag":
    logger.info(f"Flag received: {response['flag']}")
    ws.close()

def on_error(ws, error):
  logger.error(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_reason):
  logger.info(f"WebSocket closed. Status: {close_status_code}, Reason: {close_reason}")

def on_open(ws):
  logger.info("WebSocket connection established.")

async def websocket_connect():
  global jwt_token, endpoint
  url = f"wss://{endpoint}/api/ws"
  # url = "wss://enr8jgrufur3.x.pipedream.net/"
  logger.info(f"Connecting to WebSocket at {url}")

  if jwt_token:
    logger.info(f"Using JWT token in WebSocket connection: {jwt_token}")

    # Construct the Cookie header with the JWT token
    headers = {
        "Cookie": f"jwt={jwt_token}",
    }

    async with connect(url, additional_headers=headers) as websocket:
      try:
        logger.info("WebSocket connection established")

        async for message in websocket:
          if isinstance(message, str):
            on_message(websocket, message)
            
      except Exception as e:
          logger.error(f"WebSocket error: {e}")
          on_error(websocket, e)
  else:
      logger.error("No JWT token found in session.")


def get_predicted_sequence():
  global jwt_token
  if jwt_token is None:
      logger.error("JWT token not set. Cannot retrieve gameId.")
      return None

  try:
      decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
      game_id = decoded_token.get('game_id')
      if game_id is None:
          logger.error("game_id not found in JWT token.")
          return None
  except Exception as e:
      logger.error(f"Failed to decode JWT token: {e}")
      return None

  logger.info(f"Extracted game_id: {game_id}")

  try:
      result = subprocess.run(['go', 'run', 'poc.go', str(game_id)], capture_output=True, text=True)
      if result.returncode != 0:
          logger.error(f"Failed to run Go program. Error: {result.stderr}")
          return None
      else:
          logger.info("Go program executed successfully.")
          output = result.stdout.strip()
          predicted_sequence = [int(x) for x in output.strip('[]').split()]
          logger.info(f"Predicted sequence: {predicted_sequence}")
          return predicted_sequence
  except Exception as e:
      logger.error(f"Error while running Go program: {e}")
      return None
  

def strategy(predicted_sequence):
    # The action plan array to keep track of what the player should do each second
    # '1' means "plunder and attack", '0' means "dodge"
    action_plan = [1, 1, 1]  # First 3 seconds are always plunder and attack

    for i, v in enumerate(predicted_sequence):
      if v < 20:
          action_plan.append(0)
      elif 20 <= v < 35:
          # Boss signals an attack, followed by a delayed attack. Prepare to dodge
          action_plan.append(1)
          action_plan.append(0) # Dodge the signal attack
      elif 35 <= v < 50:
          action_plan.append(0)  # Dodge the attack
      elif 50 <= v < 65:
          action_plan.append(1)
      else:
          # Otherwise, attack
          action_plan.append(1)

    return action_plan


async def game(action_plan):
  global player_health, boss_health, plundered_total

  # Start time 100ms earlier for early action
  start_time = time.time() - 0.1
  current_action = 'plunder'  # Start with plundering
  current_second = 0  # Track time in seconds

  logger.info(f"Current action plan: {action_plan}")
  while player_health > 0 and boss_health > 0:
      elapsed_time = time.time() - start_time
      elapsed_seconds = int(elapsed_time)

      if elapsed_seconds > current_second:
        current_second = elapsed_seconds
        dodged_this_second = False 

        if current_second < len(action_plan):
          action = action_plan[current_second]
        else:
          action = 1

        if action == 0:
          logger.info(f"Current action: dodge at second {current_second}")
          dodge()
          await asyncio.sleep(0.9) # Wait for 1 second before the next action

        elif action == 1:
          if current_action == 'plunder':
            for i in range(20):
              plunder(wait=False)
            plunder(wait=True)
          elif current_action == 'attack':
            for i in range(20):
              attack(wait=False)
            attack(wait=True)
          # logger.info(f"Current action: {current_action} at second {current_second}")

      if plundered_total >= 800:
          current_action = 'attack'

      await asyncio.sleep(0.01) 


async def start_game():
  global player_health, boss_health, plundered_total

  new_game()
  predicted_sequence = get_predicted_sequence()
  action_plan = strategy(predicted_sequence)
  
  websocket_task = asyncio.create_task(websocket_connect())
  game_task = asyncio.create_task(game(action_plan))

  await asyncio.gather(websocket_task, game_task)
  


if __name__ == "__main__":
   asyncio.run(start_game())