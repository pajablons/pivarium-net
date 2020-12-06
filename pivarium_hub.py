import netio

station_conn = netio.Connection(0)
station_conn.initiate_connection('192.168.1.166', 10200)

for x in range(0, 25):
    station_conn.write("SENSE {}".format(x % 2 + 1))

for x in range(0, 25):
    print(station_conn.read())
