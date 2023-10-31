CREATE TABLE services (
    id_service INT,
    id_market INT,
    cdi INT,
    voltage_level INT
);

CREATE TABLE tariffs (
    id_market INT,
    cdi INT,
    voltage_level INT,
    G FLOAT,
    T FLOAT,
    D FLOAT,
    R FLOAT,
    C FLOAT,
    P FLOAT,
    CU FLOAT
);

CREATE TABLE xm_data_hourly_per_agent (
    value FLOAT,
    record_timestamp TIMESTAMP
);

CREATE TABLE records (
    id_record INT PRIMARY KEY,
    id_service INT,
    record_timestamp TIMESTAMP
);


CREATE TABLE consumption (
    id_record INT,
    value FLOAT
);


CREATE TABLE injection (
    id_record INT,
    value FLOAT
);
