CREATE OR REPLACE FUNCTION calculate_energy_bill(OUT EA FLOAT, OUT EE1 FLOAT, OUT EE2 FLOAT, OUT EC FLOAT) AS $$
DECLARE
    total_consumption FLOAT;
    total_injection FLOAT;
    cu_tariffs FLOAT;
    c_tariffs FLOAT;
    EE2_tariff FLOAT;
BEGIN
    SELECT SUM(value) INTO total_consumption
    FROM consumption c
    JOIN records r ON c.id_record = r.id_record
    JOIN services s ON r.id_service = s.id_service
    WHERE s.voltage_level IN (2, 3);

    SELECT SUM(value) INTO total_injection
    FROM injection i
    JOIN records r ON i.id_record = r.id_record
    JOIN services s ON r.id_service = s.id_service
    WHERE s.voltage_level IN (2, 3);

    SELECT CU INTO cu_tariffs FROM tariffs WHERE voltage_level IN (2, 3);
    SELECT C INTO c_tariffs FROM tariffs WHERE voltage_level IN (2, 3);

    EA := total_consumption * cu_tariffs;

    EC := total_injection * c_tariffs;

    IF total_injection <= total_consumption THEN
        EE1 := total_injection * (-cu_tariffs);
        EE2 := 0;
    ELSE
        EE1 := total_consumption * (-cu_tariffs);
        IF total_injection > total_consumption THEN
            SELECT SUM((i.value - total_consumption) * b.value)
            INTO EE2_tariff
            FROM injection i
            JOIN xm_data_hourly_per_agent b ON i.record_timestamp = b.record_timestamp
            JOIN records r ON i.id_record = r.id_record
            JOIN services s ON r.id_service = s.id_service
            WHERE i.value > total_consumption AND s.voltage_level IN (2, 3);
        ELSE
            EE2_tariff := 0;
        END IF;
        EE2 := EE2_tariff;
    END IF;

    RETURN;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM calculate_energy_bill();

