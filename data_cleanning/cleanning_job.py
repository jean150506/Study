import pandas as pd
from pathlib import Path

class treatments:
    @staticmethod
    def reading_file():
        current_dir = Path(__file__).resolve().parent
        file_path = current_dir / "Dados_trash.csv"
        return pd.read_csv(file_path, sep=";")  # se o CSV usa ; como separador

    @staticmethod
    def treating_spaces(df):
        print("antes:", list(df.columns))
        df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
        print("depois:", list(df.columns))
        df.columns = [c.replace(" ","")if isinstance(c,str) else c for c in df.columns]
        return df
    @staticmethod
    def treating_uppercase(df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [c.upper() if isinstance(c,str) else c for c in df.columns]
        return df

   
    
    @staticmethod
    def normalizing_gender(df: pd.DataFrame):
        if "gender_ID" in df.columns:
            df["gender_ID"] = df["gender_ID"].astype("string").str.replace("M", "male").str.replace("f", "Female").str.lower()
            df["gender_ID"] = df["gender_ID"].astype("string").str.replace("femaleale ", "female")
        return df
    
    @staticmethod
    def normalizing_age(df: pd.DataFrame):
        if "AGE" in df.columns:
            print("true")





df = treatments.reading_file()
result = treatments.treating_spaces(df)
treating_uppercase = treatments.treating_uppercase(result)
print(treating_uppercase)




