import psycopg2

CONNECTION = "postgres://admin:admin@localhost:5432/testdb"


def main():

    sensors = [('a','floor'),('a', 'ceiling'), ('b','floor'), ('b', 'ceiling')]

    conn = psycogp2.connect(CONNECTION)
    #insert_data(conn)
    cur = conn.cursor()


    #query_create_sensors_table = "CREATE TABLE sensors (id SERIAL PRIMARY KEY, type VARCHAR(50), location VARCHAR(50));"

    query_create_sensordata_table = """CREATE TABLE sensor_data (
                                        time TIMESTAMPTZ NOT NULL,
                                        sensor_id INTEGER,
                                        temperature DOUBLE PRECISION,
                                        cpu DOUBLE PRECISION,
                                        FOREIGN KEY (sensor_id) REFERENCES sensors (id)
                                    );"""

    query_create_sensordata_hypertable = "SELECT create_hypertable('sensor_data', 'time');"


    cur.execute(query_create_sensordata_table)   
    cur.execute(query_create_sensordata_hypertable)

    SQL = "INSERT INTO sensors (type, location) VALUES (%s, %s);"
    for sensor in sensors:
        try:
            data = (sensor[0], sensor[1])
            cur.execute(SQL, data)

        except (Exception, psycopg2.Error) as error:
            print(error.pgerror)
    conn.commit()
    cur.close()
    


