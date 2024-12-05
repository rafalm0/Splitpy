def calculate_balance(transactions, group_id=None):
    debt_dict = {}

    # First we calculate who owns and who is owned by the respective amount

    transaction_dict = {}
    for t in transactions:
        if group_id == t[3]:
            continue
        transaction = t[0]
        t_id = transaction.id
        price = transaction.price
        person = t[1]
        debt_dict[person] = 0
        if t_id not in transaction_dict.keys():
            transaction_dict[t_id] = {"price": price, "payer": [], "non_payer": []}
        if t[2]:
            transaction_dict[t_id]['payer'].append(person)
        else:
            transaction_dict[t_id]['non_payer'].append(person)

    print(transaction_dict)
    for t in transaction_dict.values():
        qtd_part = len(t['payer']) + len(t['non_payer'])
        qtd_payers = len(t['payer'])
        price_person = t['price'] / qtd_part
        price_payers = t['price'] / qtd_payers

        for p in t['payer']:
            debt_dict[p] += (price_payers - price_person)
        for p in t['non_payer']:
            debt_dict[p] -= price_person

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

    settle_transactions = {}  # dict of transactions to settle everything
    transaction_id = 0
    while nmax_transactions > 0:
        if len(owned_list) == 0 or len(own_list) == 0:
            break

        if own_list[0][1] > owned_list[0][1]:
            settle_transactions[transaction_id] = {'payer': own_list[0][0],
                                                   'receiver': owned_list[0][0],
                                                   'amount': owned_list[0][1]}

            own_list[0][0] -= owned_list[0][1]
            owned_list.pop(0)
        elif own_list[0][1] < owned_list[0][1]:
            settle_transactions[transaction_id] = {'payer': own_list[0][0],
                                                   'receiver': owned_list[0][0],
                                                   'amount': own_list[0][1]}

            owned_list[0][0] -= own_list[0][1]
            own_list.pop(0)
        else:
            settle_transactions[transaction_id] = {'payer': own_list[0][0],
                                                   'receiver': owned_list[0][0],
                                                   'amount': own_list[0][1]}
            own_list.pop(0)
            owned_list.pop(0)

        owned_list = sorted(owned_list, reverse=True, key=lambda a: a[1])
        own_list = sorted(own_list, reverse=True, key=lambda a: a[1])

        nmax_transactions -= 1

    print(settle_transactions)
    return settle_transactions
