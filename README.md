# valorem-client-python

Python client for VALOREM project 

**Warning: This package should be used exclusively for tests / debug purposes.**

## Install:

    > docker-compose build

## IOTA Wallet CLI:

**Important: You can create multiple wallets using the CLI. 
However all of them will share the same password, declared as 
`STRONG_WALLET_KEY` in .env file**.


### Check available commands:

    > docker-compose run --rm app python wallet.py --help

### Create new wallet (and alias):

To create a new wallet, use the `create-wallet` command. This will create a 
new wallet DB file and create a new account (with alias equal to your email)

    > docker-compose run --rm app python create-wallet --email bob@bob.com

Optionally, if you want to store your mnemonic in txt file (debug purposes) 
you can do so by including `store_mnemonic` argument:

    > docker-compose run --rm app python create-wallet --email bob@bob.com --store_mnemonic=1


### Request funds from IOTA faucet:

    > docker-compose run --rm app python request-funds --email bob@bob.com


### Check wallet balance:

    > docker-compose run --rm app python get-balance --email bob@bob.com



### Get wallet address:

    > docker-compose run --rm app python get-address --email bob@bob.com


### Send tokens:

    > docker-compose run --rm app python wallet.py send-tokens --email=bob@bob.com --amount=10000000 --to_address=atoi1qqnycf64hr45tvpxcxgmtvnsxh50eq0l8huuqcgeuftqt7kfdgkgyg3utxw


## VALOREM Client CLI:

### Check available commands:

    > docker-compose run --rm app python valorem.py --help
