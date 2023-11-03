CREATE OR REPLACE FUNCTION calculate_energy_bill(
    IN service_id INT,
    OUT EA FLOAT,
    OUT EE1 FLOAT,
    OUT EE2 FLOAT,
    OUT EC FLOAT
) AS $$
DECLARE
    total_consumption FLOAT;
    total_injection FLOAT;
    cu_tariffs FLOAT;
    c_tariffs FLOAT;
    EE2_tariff FLOAT;
	voltage_level_var INT;
BEGIN
    SELECT voltage_level INTO voltage_level_var FROM services WHERE id_service = service_id;

	SELECT SUM(c.value)
    INTO total_consumption
    FROM consumption c
    JOIN records r ON c.id_record = r.id_record
    WHERE r.id_service = service_id;

    SELECT SUM(i.value)
    INTO total_injection
    FROM injection i
    JOIN records r ON i.id_record = r.id_record
    WHERE r.id_service = service_id;

	IF voltage_level_var = 2 OR voltage_level_var = 3 THEN
		SELECT CU INTO cu_tariffs
		FROM tariffs
		WHERE id_market = (SELECT id_market FROM services WHERE id_service = service_id)
		AND voltage_level IN (2, 3);
	ELSE
		SELECT CU INTO cu_tariffs
        FROM tariffs
        WHERE id_market = (SELECT id_market FROM services WHERE id_service = service_id)
        AND cdi = (SELECT cdi FROM services WHERE id_service = service_id)
        AND voltage_level = voltage_level_var;
	END IF;
	EA := total_consumption * cu_tariffs;

    IF total_injection <= total_consumption THEN
        -- Tarifa CU negativa
        EE1 := total_injection * (-cu_tariffs);
	END IF;
    IF total_injection > total_consumption THEN
        -- Tarifa CU negativa
        EE1 := total_consumption * (-cu_tariffs);
    END IF;

	IF total_injection <= total_consumption THEN
        EE2 := 0; -- EE2 es igual a cero si la inyección es menor o igual al consumo
    ELSE
		SELECT SUM((c.value - i.value) * b.value)
		INTO EE2_tariff
		FROM consumption c
		JOIN injection i ON c.id_record = i.id_record
		JOIN records r ON c.id_record = r.id_record
		JOIN xm_data_hourly_per_agent b ON r.record_timestamp = b.record_timestamp
		WHERE r.id_service = service_id;

        EE2 := EE2_tariff;
    END IF;

 	SELECT C INTO c_tariffs
    FROM tariffs
    WHERE id_market = (SELECT id_market FROM services WHERE id_service = service_id)
    AND voltage_level = voltage_level_var;
	RAISE NOTICE 'total_injection: %, c_tariffs: %', total_injection, c_tariffs;
	EC := total_injection * c_tariffs;

    RETURN;
END;
$$ LANGUAGE plpgsql;

SELECT s.id_service, (calculate_energy_bill(s.id_service)).* FROM services s ORDER BY s.id_service;