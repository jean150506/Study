# main precisa acessar os dados dentro do repo
import pandas as pd

class Config:
    PATH = r"C:\Users\Jean\Desktop\Scripts\medical_cost_relation\medical_cost_relation\Study\insurance.csv"

class Raw:
    def data_reading(self, path):
        self.df = pd.read_csv(path, sep=",")
        return self.df

class DataQuality:
    def number_columns(self, df):
        # Usar o df recebido como parâmetro
        self.count_columns = df.shape[1]
        self.number_data = df.shape[0]
        self.null_values = df.isnull().sum()
        return self.count_columns, self.number_data, self.null_values

def main():
    print(Config.PATH)
    raw_obj = Raw()
    df = raw_obj.data_reading(Config.PATH)
    print(df.head())
    
    quality = DataQuality()
    quality.number_columns(df)

if __name__ == "__main__":
    main()