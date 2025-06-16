import sqlite3

def insert_scooters(cursor):
    scooters = [
        ('Xiaomi', 'M365', 'SN123456', 25, 7800, 95.5, '80-100%', 'Downtown', 0, 120.5, '2024-06-01'),
        ('Segway', 'Ninebot', 'SN654321', 30, 10000, 88.0, '70-90%', 'Uptown', 0, 200.0, '2024-05-20')
    ]
    cursor.executemany("""
        INSERT INTO scooters (
            brand, model, serial_number, top_speed, battery_capacity, soc,
            target_range_soc, location, out_of_service, mileage, last_maintenance
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, scooters)

if __name__ == "__main__":
    conn = sqlite3.connect('src/data/urban_mobility.db')
    cur = conn.cursor()
    insert_scooters(cur)
    conn.commit()
    conn.close()