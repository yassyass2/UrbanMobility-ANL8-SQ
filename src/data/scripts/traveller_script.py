import sqlite3

def insert_travellers(cursor):
    travellers = [
        ('Thijs', 'van Steenbeek', '07-09-2002', 'M', 'Wijnhaven', '107', '1234AB', 'Rotterdam', 'tvs@gmail.com', '+31-6-12345678', 'NL1234567', '12-06-2025'),
        ('Tivs', 'v S', '07-09-2002', 'M', 'Wijnhaven', '107', '1234AB', 'Rotterdam', 'tivs@gmail.com', '+31-6-12345678', 'NL1234569', '12-06-2025'),
        ('Bob', 'Marley', '01-02-3456', 'F', 'Wijnhaven', '107', '1234BA', 'Rotterdam', 'MarleyBob@gmail.com', '+31-6-12345679', 'NL1234568', '12-06-2025')
    ]

    cursor.executemany("""
                       INSERT INTO travellers (
                       first_name, last_name, birthday, gender, street, house_number, zip_code, city, email, mobile, license_number, registration_date
                       ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, travellers)
    
if __name__ == "__main__":
    conn = sqlite3.connect('data/urban_mobility.db')
    cur = conn.cursor()
    insert_travellers(cur)
    conn.commit()
    conn.close()