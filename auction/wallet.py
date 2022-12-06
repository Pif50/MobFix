from web3 import Web3

w3 = Web3(
    Web3.HTTPProvider("https://goerli.infura.io/v3/0bd7f96ab76b4ab697009051a025312f")
)
account = w3.eth.account.create()
privateKey = account.privateKey.hex()
address = account.address

print(f"Your address: {address}\nYour key: {privateKey}")
