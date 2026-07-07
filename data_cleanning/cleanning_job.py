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
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].astype("string").str.strip()
                # df[col] = df[col].str.replace(";", ",", regex=False)
        return df
    
    @staticmethod
    def normalizing_gender(df: pd.DataFrame):
        if "gender_ID" in df.columns:
            df["gender_ID"].astype("string").str == "M"
            df["gender_ID"] = df["gender_ID"].astype("string").str.replace("M", "male").str.replace("f", "Female").str.lower()
    
        return df




df = treatments.reading_file()
result = treatments.treating_spaces(df)
result_v2 = treatments.normalizing_gender(result)
print(result_v2)


