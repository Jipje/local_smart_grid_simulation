no_mutation = {
    'soc_lower': 0,
    'soc_upper': 0,
    'charge_price_lower': 0,
    'charge_price_upper': 0,
    'discharge_price_lower': 0,
    'discharge_price_upper': 0
}

aggressive_mutation = {
    'charge_price_lower': -5,
    'charge_price_upper': 0,
    'discharge_price_lower': 0,
    'discharge_price_upper': 5
}

small_mutation = {
    'soc_lower': -2,
    'soc_upper': 2,
    'charge_price_lower': -2,
    'charge_price_upper': 0,
    'discharge_price_lower': 0,
    'discharge_price_upper': 2
}

big_mutation = {
    'soc_lower': -5,
    'soc_upper': 5,
    'charge_price_lower': -5,
    'charge_price_upper': 0,
    'discharge_price_lower': 0,
    'discharge_price_upper': 5
}

random_mutation = {
    'soc_lower': -2,
    'soc_upper': 2,
    'charge_price_lower': -1,
    'charge_price_upper': 1,
    'discharge_price_lower': -1,
    'discharge_price_upper': 1
}
