def calculate_balance(transactions, group_id=None):
    debt_dict = {}

    # First we calculate who owns and who is owned by the respective amount

    debt_dict = {}
    for t in transactions:
        if group_id == t[2]:
            continue
        transaction = t[0]
        person = t[1]
        paid = t[3]
        consumed = t[4]
        if person not in debt_dict.keys():
            debt_dict[person] = 0
        debt_dict[person] += paid
        debt_dict[person] -= consumed

    print(debt_dict)
    own_list = []
    owned_list = []

    total_sum = 0
    for person in debt_dict.keys():
        total_sum += debt_dict[person]
        if debt_dict[person] > 0:
            owned_list.append([person, debt_dict[person]])
        elif debt_dict[person] < 0:
            own_list.append([person, -debt_dict[person]])

    if int(total_sum) != 0:
        print("total_sum not equal to zero")

    nmax_transactions = len(owned_list) + len(own_list)
    owned_list = sorted(owned_list, reverse=True, key=lambda a: a[1])
    own_list = sorted(own_list, reverse=True, key=lambda a: a[1])

    settle_transactions = []
    while nmax_transactions > 0:
        if len(owned_list) == 0 or len(own_list) == 0:
            break

        print(f"Lookign at {own_list[0]} transfering to {owned_list[0]}")
        if own_list[0][1] > owned_list[0][1]:
            settle_transactions.append({'payer': own_list[0][0],
                                        'receiver': owned_list[0][0],
                                        'amount': owned_list[0][1]})

            own_list[0][1] -= owned_list[0][1]
            owned_list.pop(0)
        elif own_list[0][1] < owned_list[0][1]:
            settle_transactions.append({'payer': own_list[0][0],
                                        'receiver': owned_list[0][0],
                                        'amount': own_list[0][1]})

            owned_list[0][1] -= own_list[0][1]
            own_list.pop(0)
        else:
            settle_transactions.append({'payer': own_list[0][0],
                                        'receiver': owned_list[0][0],
                                        'amount': own_list[0][1]})
            own_list.pop(0)
            owned_list.pop(0)

        owned_list = sorted(owned_list, reverse=True, key=lambda a: a[1])
        own_list = sorted(own_list, reverse=True, key=lambda a: a[1])

        nmax_transactions -= 1

    print(settle_transactions)
    return settle_transactions
