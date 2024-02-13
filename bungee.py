from web3 import Web3
import csv
import requests
import time

# Connect to the Ethereum node
w3 = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))

# Define the parameters
address = "0x3a23F943181408EAC424116Af7b7790c94Cb97a5"  # Socket: Gateway Address
from_block = 19145502  # Feb-03-2024 04:54:47 AM +UTC
to_block = 19165592  # Feb-06-2024 12:20:59 AM +UTC
topic_transfer = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

filter_params = {
    'fromBlock': hex(from_block),  # Convert to hex string
    'toBlock': hex(to_block),  # Convert to hex string
    'topics': [
        topic_transfer,  # Transfer event signature
        None,  # Don't filter by sender
        '0x000000000000000000000000' + address.lower()[2:]  # Filter by receiver, padding address
    ]
}

# Fetch the logs
logs = w3.eth.get_logs(filter_params)

# Log parsing function
def parse_log(log):
    block = w3.eth.get_block(log['blockNumber'])  # get block
    timestamp = block['timestamp']  # get block timestamp
    return {
        'blockNumber': log['blockNumber'],
        'timestamp': timestamp,
        'transactionHash': log['transactionHash'].hex(),
        'from': '0x' + log['topics'][1].hex()[-40:],
        'to': '0x' + log['topics'][2].hex()[-40:],
        'value': int(log['data'], 16),
        'address': log['address']
    }

# Parse the logs
parsed_logs = [parse_log(log) for log in logs]

# Function to get token name for a given address
def get_token_name(address):
    # ERC-20 Token Name ABI
    abi = [{"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}],
            "payable": False, "stateMutability": "view", "type": "function"}]

    # Load the contract
    contract = w3.eth.contract(address=address, abi=abi)

    # Call the name function
    try:
        token_name = contract.functions.name().call()
        return token_name
    except Exception as e:
        print(f"Error fetching token name for {address}: {e}")
        return "Unknown"  # Return "Unknown" if there's an error fetching the name

# Function to get token decimals for a given address
def get_token_decimals(address):
    # ERC-20 Token Decimals ABI
    abi = [{"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}],
            "payable": False, "stateMutability": "view", "type": "function"}]

    # Load the contract
    contract = w3.eth.contract(address=address, abi=abi)

    # Call the decimals function
    try:
        token_decimals = contract.functions.decimals().call()
        return token_decimals
    except Exception as e:
        print(f"Error fetching decimals for {address}: {e}")
        return None  # Return None if there's an error fetching the decimals

# Function to fetch token price for a given token address
def get_token_price(token_address, timestamp=None):
    max_retries = 10
    retries = 0
    
    while retries < max_retries:
        try:
            url = f"https://coins.llama.fi/prices/historical/{timestamp}/ethereum:{token_address}?searchWidth=4h"
            headers = {'accept': 'application/json'}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                coin_data = data.get('coins', {}).get(f'ethereum:{token_address}')
                if coin_data:
                    print(coin_data)
                    return coin_data.get('price')
                else:
                    print(f"No price data found for token: {token_address}")
                    return None
            else:
                print(f"Failed to fetch token price for {token_address}. Status code: {response.status_code}")
                retries += 1
                time.sleep(0.1)  # Pause for 100 milliseconds before retrying
                continue
        except Exception as e:
            print(f"Error fetching token price for {token_address}: {e}")
            retries += 1
            time.sleep(0.1)  # Pause for 100 milliseconds before retrying
            continue
            
    print(f"Max retries reached for token: {token_address}")
    return None

# Create a dictionary to store token data for each address
token_data = {}

# Get token data for each address
for log in parsed_logs:
    address = log['address']
    timestamp = log['timestamp'] 
    if address not in token_data:
        token_data[address] = {
            'tokenName': get_token_name(address),
            'decimals': get_token_decimals(address),
            'tokenPrice': get_token_price(address,timestamp)
        }
        print(token_data[address])

# Store the parsed logs along with token data in a CSV file
csv_filename = 'Bungee_TX_logs2.csv'
with open(csv_filename, 'w', newline='') as csvfile:
    fieldnames = ['blockNumber', 'timestamp', 'transactionHash', 'from', 'to', 'value', 'address', 'tokenName', 'decimals', 'tokenPrice']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for log in parsed_logs:
        address = log['address']
        log.update(token_data.get(address, {}))  # Add token data to log
        writer.writerow(log)

print(f"ERC-20 transfers have been stored in '{csv_filename}'.")
