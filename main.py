import pandas as pd


class DataService:
    def __init__(self):
        self.consumption = pd.read_csv('dataframes/consumption.csv')
        self.records = pd.read_csv('dataframes/records.csv')
        self.injection = pd.read_csv('dataframes/injection.csv')
        self.services = pd.read_csv('dataframes/services.csv')
        self.tariffs = pd.read_csv('dataframes/tariffs.csv')
        self.xm_data_hourly_per_agent = pd.read_csv('dataframes/xm_data_hourly_per_agent.csv')


class EnergyCalculator:

    @staticmethod
    def calculate_energy_bill(data, id_service):
        EE2 = 0
        service_data = data.services[data.services['id_service'] == id_service]
        voltage_level_var = service_data['voltage_level'].values[0]

        consumption = data.consumption[
            data.consumption['id_record'].isin(data.records[data.records['id_service'] == id_service]['id_record'])]

        if voltage_level_var in [2, 3]:
            cu_tariff = data.tariffs[data.tariffs['voltage_level'].isin([2, 3])]['CU'].values[0]
        else:
            cu_tariff = data.tariffs[
                (data.tariffs['id_market'] == service_data['id_market'].values[0]) &
                (data.tariffs['cdi'] == service_data['cdi'].values[0]) &
                (data.tariffs['voltage_level'] == voltage_level_var)
                ]['CU'].values[0]

        total_consumption = consumption['value'].sum()
        EA = total_consumption * cu_tariff
        injection = data.injection[
            data.injection['id_record'].isin(data.records[data.records['id_service'] == id_service]['id_record'])]
        total_injection = injection['value'].sum()

        if total_injection <= total_consumption:
            EE1 = total_injection * (-cu_tariff)
        else:
            EE1 = total_consumption * (-cu_tariff)

        if total_injection <= total_consumption:
            EE2 = 0
        else:
            consumption_difference = consumption['value'].sub(injection['value'], fill_value=0)
            relevant_hours = data.xm_data_hourly_per_agent[
                data.xm_data_hourly_per_agent['record_timestamp'].isin(
                    data.records[data.records['id_service'] == id_service]['record_timestamp']
                )]

            if not relevant_hours.empty:
                consumption_difference = (consumption_difference[consumption_difference > 0] - total_injection).sum()
                EE2 = (consumption_difference * relevant_hours['value']).sum()

        c_tariff = data.tariffs[
            (data.tariffs['id_market'] == service_data['id_market'].values[0]) &
            (data.tariffs['voltage_level'] == voltage_level_var)
            ]['C'].values[0]

        EC = total_injection * c_tariff
        results = pd.DataFrame({'id_service': id_service, 'EA': [EA], 'EE1': [EE1], 'EE2': [EE2], 'EC': [EC]})

        return results

    @staticmethod
    def print_results(result_dataframe):
        print(result_dataframe)

    def calculate_energy_bills_for_all_services(self, data):
        service_ids = data.services['id_service'].unique()
        results = []

        for service_id in service_ids:
            result_dataframe = self.calculate_energy_bill(data, service_id)
            if result_dataframe is not None:
                results.append(result_dataframe)

        return pd.concat(results)


if __name__ == '__main__':
    data = DataService()
    calculator = EnergyCalculator()
    results_dataframe = calculator.calculate_energy_bills_for_all_services(data)
    calculator.print_results(results_dataframe.sort_values(by='id_service'))

