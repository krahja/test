import os
import json
from config import *
from data import cash
from datetime import datetime


def check_am():
    data_dir = os.curdir + '/data/'
    with open(data_dir+'wallet.txt', 'r') as file:
        l_wall = json.load(file)
    s_wall = get_status()['return']['funds']
    flag = 0
    sum_loc_coin = 0
    for i in l_wall[coin]:
        sum_loc_coin += i[0]
    if round(s_wall[coin], 2) != round(sum_loc_coin, 2):
        flag = 1
    return flag


def check_free_cash():
    usd = get_status()['return']['funds']['usd']
    if usd > cash/2:
        return round(usd-cash/2)
    else:
        return 0


def main(av_pr):
    print('   ___   ')
    data_dir = os.curdir + '/data/'
    with open(data_dir+'wallet.txt', 'r') as file:
        l_wall = json.load(file)
    with open(data_dir+'deal.txt', 'r') as file:
        for line in file:
            deal.append(line.strip())
    for i in l_wall[coin]:
        ord_bid = get_depth(pair)[pair]['bids'][0]
        if ord_bid[0] < i[1] * 0.994 and ord_bid[0] >= i[1] * 0.986:
            print('stoploss покупка', i[1], 'при текущей', round(ord_bid[0], 2))
            # trade('sell',zec_pr*0.99,0.05,'zec_usd')
        elif ord_bid[0] >= i[1]*0.994 and ord_bid[0] <= i[1]*1.012:
            print('flat покупка', i[1], 'при текущей', round(ord_bid[0], 2))
        elif ord_bid[0] < i[1]*0.986:
            pass
            # print('you\'re investor')
        else:
            profit = round(ord_bid[0]*0.998*i[0] - i[0]*i[1],2)
            print('profit', profit)

            if ord_bid[1] > i[0]:
                trade('sell', ord_bid[0], i[0], pair)
                if get_my_orders()['success'] == 0:
                    l_wall[coin].remove([i[0], i[1]])
                    print('продажа прошла')
                    deal_line = 'zec_usd '+str(i[0])+' '+str(i[1])+' '+str(ord_bid[0])+' '+str(profit)
                    print(deal_line)
                    deal.append(deal_line)
                    print(deal)
                    with open(data_dir + 'deal.txt', 'w') as file:
                        for i in deal:
                            file.write(i + '\n')
                else:
                    print('продажа встала ордером')

        time.sleep(1)
    deal.clear()

    ord_ask = get_depth(pair)[pair]['asks'][0]
    if ord_ask[0] < av_pr-2 or ord_ask[0] < 232:
        if ord_ask[1] > am and check_free_cash() > 20:
            trade('buy', ord_ask[0], am, pair)
            print('заявка на покупку сделана')
            time.sleep(1)
            if get_my_orders()['success'] == 0:
                l_wall[coin].append([am*0.998, ord_ask[0]])
                print('покупка прошла')
            else:
                print('покупка встала ордером')

    with open(data_dir + 'wallet.txt', 'w') as file:
        json.dump(l_wall, file, ensure_ascii=False)


# last one hour
func_length = 60
pair = 'zec_usd'
coin = 'zec'

func_price = []
deal = []
count = 1

am = 0.012

if __name__ == '__main__':
    while True:
        try:
            depth = get_depth(pair)
            coin_pr = round(0.5*(depth[pair]['bids'][0][0]+depth[pair]['asks'][0][0]), 2)
            func_price.append(coin_pr)

            if len(func_price) >= func_length:
                func_price.remove(func_price[0])

            av_pr = 0
            for i in func_price:
                av_pr += i
            av_pr = round(av_pr/len(func_price), 2)
            print('avpr=',av_pr, end=' ')

            #main(av_pr)

            #print(func_price)

            if count % 5 == 0 and count >= 5:
                av_pr_5 = 0
                for i in range(-5,0):
                    av_pr_5 += func_price[i]
                av_pr_5 = round(av_pr_5/5, 2)
                print('5m=', av_pr_5)
            else:
                print()

            time.sleep(60)
            count += 1
            #print('average price for', count, 'min', round(av_pr, 2))
            
        except:
            print('неизвестная ошибка',end='')
            time.sleep(1)
            print('.',end='')
            time.sleep(1)
            print('.',end='')
            time.sleep(1)
            print('.')
            time.sleep(1)
