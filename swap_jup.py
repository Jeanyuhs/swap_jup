import os
import csv
import requests
import time
from solders.pubkey import Pubkey # type: ignore
from solders.keypair import Keypair # type: ignore
from solana.transaction import Transaction
from solders.system_program import transfer as spl_transfer # type: ignore
from solders.account import Account # type: ignore
from solana.rpc.api import Client

# Read private key from dontshare.py
import dontshare as d

# KEY FROM THE FILE DONTSHARE
KEY = Keypair.from_base58_string(d.key)

# Establish a connection to a Solana node
rpc_url = "https://api.devnet.solana.com"
connection = Client(rpc_url)

# Function to sell the token back to SOL
async def sellToken(tokenAddress):
    inputMint = tokenAddress
    outputMint = 'So11111111111111111111111111111111111111112'  # SOL mint address
    quoteUrl = f'https://quote-api.jup.ag/v6/quote?inputMint={inputMint}&outputMint={outputMint}&amount=1000000000&slippageBps=1'
    print("Quote URL:", quoteUrl)
    quote = requests.get(quoteUrl).json()
    if 'swapTransaction' in quote:
        swapTx = bytes.fromhex(quote['swapTransaction'])
        instructions = [
            spl_transfer(
                KEY.public_key(),  # Use public key for the source account
                Pubkey(inputMint),
                Pubkey(outputMint),
                1000000000,  # 1 SOL
            ),
        ]
        transaction = Transaction().add(*instructions)
        transaction.sign(KEY)
        txId = await connection.send_transaction(transaction, KEY)
        print(f"Token sold: {tokenAddress}")
    else:
        print("Error in quote response:", quote)

async def main():
    # Read token address from token_address.txt
    with open('token_address.txt', 'r') as file:
        tokenAddress = file.readline().strip()

    # Amount to swap in token decimals
    amount = 0.01
    inputMint = 'So11111111111111111111111111111111111111112'  # Use the SOL mint address
    outputMint = tokenAddress  # Use the mint address of the new token
    slippageBps = 1

    # Query the Jupiter API for the quote
    quoteUrl = f'https://quote-api.jup.ag/v6/quote?inputMint={inputMint}&outputMint={outputMint}&amount={amount}&slippageBps={slippageBps}'
    response = requests.get(quoteUrl)
    quote = response.json()

    # Extract the output amount from the quote response
    outAmount = quote.get('outAmount')

    print(f"Output amount: {outAmount}")

    # Wait for 10 seconds
    time.sleep(10)

    # Call the async function to sell the token back to SOL
    await sellToken(tokenAddress)

# Run the async main function
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
