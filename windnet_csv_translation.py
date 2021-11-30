from csv import reader

if __name__ == '__main__':
    with open('data/wind_net_csv.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        header = False
        for wind_net_data in csv_reader:
            if not header:
                header = True
                continue
            print(wind_net_data)
            break