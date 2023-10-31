from connection import connect_to_database


def calculate_energy_bill():
    connection = connect_to_database()
    connection.close()


if __name__ == '__main__':
    calculate_energy_bill()

