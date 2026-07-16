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
    def treating_uppercase(df: pd.DataFrame):
        df.columns = [c.upper() if isinstance(c,str) else c for c in df.columns]
        return df

    @staticmethod
    def normalizing_gender(df: pd.DataFrame):
        if "GENDER_ID" in df.columns:
            df["GENDER_ID"] = df["GENDER_ID"].astype("string").str.replace("M", "male").str.replace("f", "Female").str.lower()
            df["GENDER_ID"] = df["GENDER_ID"].astype("string").str.replace("femaleale ", "female")
        return df
    
    @staticmethod
    def normalizing_age(df: pd.DataFrame):
        if "AGE" in df.columns:
            # age has 2 main problems: float numbers and can have the NaN value 
            df["AGE"] = df["AGE"].fillna(0)
            df["AGE"] = [int(c) if isinstance(c, float) else c for c in df["AGE"]]
        return df
    @staticmethod
    def treating_bmi(df: pd.DataFrame):
        df["BMI"] = df["BMI"].astype("string").str.replace("UNKNOWN","0")
        df["BMI"] = df["BMI"].astype("float").__round__(2)
        return df
    @staticmethod 
    def treating_IS_SMOKER(df: pd.DataFrame):
        df["IS_SMOKER"] = df["IS_SMOKER"].astype("string").str.upper()
        df["IS_SMOKER"] = df["IS_SMOKER"].astype("string").str.strip()
        df["IS_SMOKER"] = df["IS_SMOKER"].astype("string").str.replace("Y","YES")
        df["IS_SMOKER"] = df["IS_SMOKER"].astype("string").str.replace("N","NO")
        return df
    @staticmethod
    def treating_region_name(df:pd.DataFrame):
        df["REGION_NAME"] = df["REGION_NAME"].astype("string").str.strip()
        return df 
    @staticmethod
    def treating_total_charges(df:pd.DataFrame):
        df["TOTAL_CHARGES"] = df["TOTAL_CHARGES"].astype("string").str.strip()
        df["TOTAL_CHARGES"] = df["TOTAL_CHARGES"].astype("string").str.replace("$ ","")
        df["TOTAL_CHARGES"] = df["TOTAL_CHARGES"].astype("float").__round__(2)
        df["TOTAL_CHARGES"] = df["TOTAL_CHARGES"].fillna(0)
        return df
    






df = treatments.reading_file()
df = treatments.treating_spaces(df)
df = treatments.treating_uppercase(df)
df = treatments.normalizing_gender(df)
df = treatments.normalizing_age(df)
df = treatments.treating_bmi(df)
df = treatments.treating_IS_SMOKER(df)
df = treatments.treating_region_name(df)
df = treatments.treating_total_charges(df)
print(df)





