# -*- coding: utf8 -*-
from pyuseragents import random as random_useragent
from requests import Session
from msvcrt import getch
from os import system
from ctypes import windll
from urllib3 import disable_warnings
from loguru import logger
from sys import stderr, exit
from concurrent.futures import ThreadPoolExecutor
from random import randint
from json import loads
from eth_account.messages import encode_defunct
from web3.auto import w3
from eth_account import Account

class Wrong_Response(BaseException):
	pass

class Wrong_PrivateKey(BaseException):
	pass

disable_warnings()
def clear(): return system('cls')
logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <white>{message}</white>")
windll.kernel32.SetConsoleTitleW('AlturaNFT Auto Reger | by NAZAVOD')
print('Telegram channel - https://t.me/n4z4v0d\n')

def random_tor_proxy():
	proxy_auth = str(randint(1, 0x7fffffff)) + ':' + str(randint(1, 0x7fffffff))
	proxies = {'http': 'socks5://{}@localhost:9150'.format(proxy_auth), 'https': 'socks5://{}@localhost:9150'.format(proxy_auth)}
	return(proxies)

def take_proxies(length):
	proxies = []

	while len(proxies) < length:
		with open(proxy_folder, 'r') as file:
			for row in file:
				proxies.append(row.strip())

	return(proxies[:length])

def mainth(email, wallet_data, proxy):
	try:
		private_key = [current_wallet for current_wallet in wallet_data.split(':') if len(current_wallet) == 66 and current_wallet[:2] == '0x' or len(current_wallet) == 64]

		if len(private_key) == 1: private_key = private_key[0]
		else: raise Wrong_PrivateKey('')

		if private_key[:2] != '0x': private_key = f'0x{private_key}'

		try:
			address = Account.from_key(str(private_key)).address
		except:
			raise Wrong_PrivateKey('')

	except Wrong_PrivateKey():
		logger.error(f'{email} | Wrong private key: {wallet_data}')

		with open('unregistered.txt', 'a') as file:
			file.write(f'{email}:{wallet_data}:{proxy}\n')

		return

	for _ in range(5):
		try:
			session = Session()
			session.headers.update({'user-agent': random_useragent(), 'accept': 'application/json, text/plain, */*', 'accept-language': 'ru,en;q=0.9,vi;q=0.8,es;q=0.7', 'content-type': 'application/x-www-form-urlencoded', 'origin': 'https://www.alturanft.com', 'referer': 'https://www.alturanft.com/waiting-list'})
			
			if use_proxy == 'y':
				if proxy_source == 2:
					session.proxies.update({'http': f'{proxy_type}://{proxy}', 'https': f'{proxy_type}://{proxy}'})

				else:
					session.proxies.update(random_tor_proxy())

			r = session.post('https://www.alturanft.com/api/mailing-list', data = f'email={email}')

			if not r.ok:
				raise Wrong_Response('')

			nonce = loads(r.text)['user']['nonce']
			sign = w3.eth.account.sign_message(encode_defunct(text=f'I am signing my one-time nonce: {nonce}'), private_key = private_key).signature.hex()

			r = session.post('https://www.alturanft.com/api/mailing-list/add-address', data = f'address={address}&email={email}&signature={sign}')

			if not r.ok:
				raise Wrong_Response('')

		except Wrong_Response as error:
			logger.error(f'{email} | Wrong response: {str(error)}, response code: {str(r.status_code)}, response: {str(r.text)}')

		except Wrong_PrivateKey():
			logger.error(f'{email} | Wrong private key: {wallet_data}')

			with open('unregistered.txt', 'a') as file:
				file.write(f'{email}:{wallet_data}:{proxy}\n')

			return

		except Exception as error:
			logger.error(f'{email} | Unexpected error : {str(error)}')

		else:
			with open('registered.txt', 'a') as file:
				file.write(f'{email}:{wallet_data}:{proxy}\n')

			logger.success(f'{email} | Successfully registered')

			return

	with open('unregistered.txt', 'a') as file:
		file.write(f'{email}:{wallet_data}:{proxy}\n')

if __name__ == '__main__':
	threads = int(input('Threads: '))
	emails_directory = input('Drop .txt with emails: ')
	wallets_datas_directory = input('Drop .txt with private keys (only private key or split any words with :): ')
	use_proxy = input('Use Proxies? (y/N): ').lower()

	with open(emails_directory, 'r') as file:
		emails_list = [row.strip() for row in file]
		proxies = [None for _ in range(len(emails_list))]

	with open(wallets_datas_directory, 'r') as file:
		wallets_datas = [row.strip() for row in file]

	if use_proxy == 'y':
		proxy_source = int(input('How take proxies? (1 - tor proxies; 2 - from file): '))

		if proxy_source == 2:
			proxy_type = str(input('Enter proxy type (http; https; socks4; socks5): '))
			proxy_folder = str(input('Drag and drop file with proxies (ip:port; user:pass@ip:port): '))

			proxies = take_proxies(len(emails_list))

	clear()

	with ThreadPoolExecutor(max_workers = threads) as executor:
		executor.map(mainth, emails_list, wallets_datas, proxies)

	logger.success('Работа успешно завершена!')
	print('\nPress Any Key To Exit..')
	getch()
	exit()
