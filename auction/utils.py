import json
from web3 import Web3
import redis
from datetime import *
from .models import *
from django.contrib import messages
import hashlib
from django.contrib.auth.models import User
from users.models import Profile

client = redis.Redis(host="127.0.0.1", port="6379", decode_responses=True)


def sendTransaction(message):
    w3 = Web3(
        Web3.HTTPProvider(
            "https://goerli.infura.io/v3/0bd7f96ab76b4ab697009051a025312f"
        )
    )
    address = "0x26F6f5233681ea691709Bf366BBc23d3526f5d1E"
    privateKey = "0x27943b007c14ef3ba1c7609b1ffe097b84f90c48fa4ec65ea4b61f63d9ecadb9"
    nonce = w3.eth.getTransactionCount(address)
    gasPrice = w3.eth.gasPrice
    value = w3.toWei(0, "ether")
    signedTx = w3.eth.account.sign_transaction(
        dict(
            nonce=nonce,
            gasPrice=gasPrice,
            gas=100000,
            to="0x0000000000000000000000000000000000000000",
            value=value,
            data=message.encode("utf-8"),
        ),
        privateKey,
    )
    tx = w3.eth.sendRawTransaction(signedTx.rawTransaction)
    txId = w3.toHex(tx)
    return txId


def send_on_chain(auct):
    json_info = {
        f"Auction_{auct.id}": {
            "Auction id": auct.id,
            "Object": auct.object,
            "Description": auct.description,
            "Open date(UTC)": str(auct.open_date),
            "Close date(UTC)": str(auct.close_date),
            "Open price": auct.open_price,
            "Close price": auct.close_price,
            "Details all bets": detail_bets(auct.id),
            "Total bets": auct.total_bet,
            "Winner": auct.winner,
        }
    }
    json_file = json.dumps(json_info)
    hash_json = hashlib.sha256(json_file.encode("utf-8")).hexdigest()
    tx = sendTransaction(hash_json)
    auct.json_details_file = str(json_file)
    auct.tx = tx
    auct.save()
    print(tx)
    return tx


def add_data_redis(auction_id, price, date, user):
    client.rpush(f"Auction_{auction_id}", f"{price}")
    client.rpush(f"Data_in_{auction_id}", f"{date}")
    client.rpush(f"User_in_{auction_id}", f"{user}")


def last_bet(auction_id):
    last_price = client.lindex(
        f"Auction_{auction_id}",
        -1,
    )
    return last_price


def last_user(auction_id):
    list_user = client.lindex(f"User_in_{auction_id}", -1)
    return list_user


def last_date(auction_id):
    list_date = client.lindex(f"Data_in_{auction_id}", -1)
    return list_date


def len_bets(auction_id):
    tot = client.llen(f"Auction_{auction_id}")
    return tot


def detail_bets(id):
    list_bet = client.lrange(f"Auction_{id}", 0, -1)
    list_data = client.lrange(f"Data_in_{id}", 0, -1)
    list_user = client.lrange(f"User_in_{id}", 0, -1)
    details = []
    count = len_bets(id)
    i = 0
    while i != count:
        details.append([f"{list_user[i]} - {list_data[i]} - $ {list_bet[i]}"])
        i += 1
    return details


def check_data(close_data):
    now_t = datetime.utcnow()
    now = datetime.strftime(now_t, "%Y-%m-%d %H:%M")
    end_data = datetime.strftime(close_data, "%Y-%m-%d %H:%M")
    if now >= end_data:
        return False
    else:
        return True


def check_winner(request, id_auction):
    auction = Auction.objects.get(id=id_auction)
    auction.total_bet = len_bets(id_auction)
    auction.close_price = last_bet(id_auction)
    auction.winner = last_user(id_auction)
    auction.save()
    prof_user = Profile.objects.get(username=auction.winner)
    prof_user.wins += 1
    prof_user.wallet -= int(auction.close_price)
    tx = send_on_chain(auction)
    if prof_user.wallet < 0:
        prof_user.active = False
        prof_user.save()
    prof_user.save()
    messages.success(
        request,
        f"The winner is {auction.winner} with the last bet at $ {auction.close_price}",
    )
    messages.info(request, f"The transaction is {tx}")
    return tx


def check_profile(request):
    user = request.user
    prof_user = Profile.objects.get(user=user)
    if prof_user is False:
        messages.error(request, f"Attention! please pay {prof_user.wallet} $")
        return True
