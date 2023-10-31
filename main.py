import psycopg2

from connection import connect_to_database


class calculate_energy_bill:
    def __init__(self):
        self.connection = None

    def connect_to_database(self):
        self.connection = connect_to_database()

    def disconnect_from_database(self):
        if self.connection:
            self.connection.close()

    def calculate_energy_bill(self):
        try:
            cur = self.connection.cursor()

            cur.execute("""
                SELECT SUM(c.value)
                FROM consumption c
                JOIN records r ON c.id_record = r.id_record
                JOIN services s ON r.id_service = s.id_service
                WHERE s.voltage_level IN (2, 3) 
            """)
            total_consumption = cur.fetchone()[0]

            cur.execute("""
                SELECT SUM(i.value)
                FROM injection i
                JOIN records r ON i.id_record = r.id_record
                JOIN services s ON r.id_service = s.id_service
                WHERE s.voltage_level IN (2, 3) 
            """)
            total_injection = cur.fetchone()[0]

            cur.execute("SELECT CU, C FROM tariffs WHERE voltage_level IN (2, 3) AND cdi IS NULL")
            cu_tariffs, c_tariffs = cur.fetchone()

            EA = total_consumption * cu_tariffs
            EC = total_injection * c_tariffs

            if total_injection <= total_consumption:
                EE1 = total_injection * (-cu_tariffs)
                EE2 = 0
            else:
                EE1 = total_consumption * (-cu_tariffs)

                if total_injection > total_consumption:
                    cur.execute("""
                        SELECT SUM((i.value - %s) * b.value)
                        FROM injection i
                        JOIN xm_data_hourly_per_agent b ON i.record_timestamp = b.record_timestamp
                        JOIN records r ON i.id_record = r.id_record
                        JOIN services s ON r.id_service = s.id_service
                        WHERE i.value > %s AND s.voltage_level IN (2, 3)
                    """, (total_consumption, total_consumption))
                    EE2_tariff = cur.fetchone()[0]
                    EE2 = EE2_tariff
                else:
                    EE2 = 0

            return {
                "Energía Activa (EA)": EA,
                "Excedentes de Energía Tipo 1 (EE1)": EE1,
                "Excedentes de Energía Tipo 2 (EE2)": EE2,
                "Comercialización de Excedentes de Energía (EC)": EC
            }

        except (psycopg2.Error, Exception) as error:
            print("Error:", error)
            return None


if __name__ == '__main__':
    bill = calculate_energy_bill()
    bill.connect_to_database()
    result = bill.calculate_energy_bill()
    bill.disconnect_from_database()

    if result is not None:
        for type, value in result.items():
            print(f"{type}: {value}")

