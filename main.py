import configparser
import requests
import sys
import time
from time import sleep
from solana.publickey import PubKey
from solana.rpc.websocket_api import connect
from solana.rpc.commitment import Finalized
from solana.rpc.api import Client
import subprocess
from utils.discord_notifier import send_message, composeEmbed
from utils.security import checkPoolSize, checkLiquidityLockPercentage, checkPresentRisks, checkMintAuthority, checkFreezeAuthority, checkTopHolders

checkPoolSizeFlag = False
mintAuthority = False
freezeAuthority = False
topHoldersPercentage = 0
rugPullAPIJsonData = ""

def getRugAPIJsonData(token_address):
    while(True):
        try:
            print(" [*] Gettings token metadata")
            r = requests.get(f'https://api.rugcheck.xyz/v1/tokens/{token_address}/report')
            if(r.text is not None):
                print(" [*] Metadata obtained")
                print("")
            return r.json()
        except:
            print(" [*] Failed to parse json, sleeping for 5 seconds and trying again")
            sleep(5)

def get_pool_infos(token_address, pool_number):
    print(" [*] ENGAGING WITH SECURITY SIZE")
    print(" [*] CHECKING POOL SIZE")
    global checkPoolSizeFlag
    checkPoolSizeFlag = checkPoolSize(pool_number, minimum_pool_size, maximum_pool_size)
    if (checkPoolSizeFlag == True):
        global rugPullAPIJsonData   
        rugPullAPIJsonData = getRugAPIJsonData(token_address)
        print(" [*] CHECKING LOCKED LIQUIDITY PERCENTAGE")
        lockedPercentage = checkLiquidityLockPercentage(rugPullAPIJsonData)
        if(lockedPercentage > int(minimum_locked_percentage)):
            print(" [*] Locked liquidity check passed!")
            print(" [*] CHECKING MINT AUTHORITY")
            mintAuthority = checkMintAuthority(rugPullAPIJsonData)
            if(mintAuthority):
                print(" [*] Mint Authority check passed!")
                print(" [*] CHECKING FREEZE AUTHORITY")
                freezeAuthority = checkFreezeAuthority(rugPullAPIJsonData)
                if(freezeAuthority):
                    print(" [*] Freeze Authority check passed!")
                    print(" [*] CHECKING TOP HOLDERS PERCENTAGE")
                    topHoldersPercentage = checkTopHolders(rugPullAPIJsonData)
                    if(topHoldersPercentage <= int(max_holder_percentage)):
                        print(" [*] Top Holders Percentage check passed!")
                        print(" [*] RISK ANALYSIS")
                        if(checkPresentRisks(rugPullAPIJsonData, max_risk_count) == False):
                            print(" [*] Risk check passed!")
                            embed = composeEmbed(rugPullAPIJsonData, token_address, pool_number, mintAuthority, freezeAuthority, topHoldersPercentage, True)
                            send_message('', embed)
                            subprocess.Popen(['python3', 'utils/trade.py', token_address])
                        else:
                            print(" [-] Risk check failed")
                    else:
                        print("TOP HOLDERS CHECK FAILED")
                else:
                    print("FREEZE AUTHORITY CHECK FAILED")
            else:
                print("MINT AUTHORITY CHECK FAILED")
        else:
            print(" [*] Locked liquidity percentage low! {lockedPercentage}% ")
    else:
        print(" [*] POOL LOWER THAN THE MINIMUM")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(" [*] Data was not passed from NodeJS to Python")
        sys.exit(1)

    token_address = sys.argv[1]
    pool_size_str = sys.argv[2]

    if not token_address:
        print("Error: Token address is not provided.")
        sys.exit(1)

    try:
        pool_size_float = float(pool_size_str)
        pool_size = int(pool_size_float)
    except ValueError:
        print("Error: Invalid pool size. Please provide a valid number.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read('./config.ini')
    minimum_pool_size = config['config']['minimum_pool_size']
    maximum_pool_size = config['config']['maximum_pool_size']
    minimum_locked_percentage = config['config']['locked_percentage']
    max_holder_percentage = config['config']['max_holder_percentage']
    max_risk_count = config['config']['max_risk_count']
    main_url = config['solanaConfig']['main_url']
    ws_url = config['solanaConfig']['ws_url']
    raydium_lp_v4 = config['solanaConfig']['raydium_lp_v4']
    log_instruction = config['solanaConfig']['log_instruction']

    client = Client(main_url)
    raydium_lp_v4 = PublicKey.from_string(raydium_lp_v4)

    ascii = 'xdd'
    print(ascii)
    print()
