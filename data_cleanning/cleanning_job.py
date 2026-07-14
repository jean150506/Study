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
    # def treating_spaces(df):
    #     for col in df.columns:
    #         print(col)
    #         df = df.rename(columns={col:col.strip() for col in df.columns})
    #         # if df[col].dtype == "object":
    #         # df[col] = df[col].astype("string").str.strip()
    #         #     # df[col] = df[col].str.replace(";", ",", regex=False)
        # return df
    
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

        # if "AGE" in df.columns:
        #     print("column dtype:", df["AGE"].dtype)
        #     types = df["AGE"].apply(lambda x: type(x).__name__)
        #     for t in types:
        #         print(t)                       # imprime um tipo por linha
        #     print("counts:\n", types.value_counts())
        #     df["AGE_numeric"] = pd.to_numeric(df["AGE"], errors="coerce")
        # return df
        
        #     df["AGE"] = df["AGE"].astype("string").str.replace("NaN","18")

        # return df




df = treatments.reading_file()
result = treatments.treating_spaces(df)
print(result)
# result_v2 = treatments.normalizing_gender(result)
# print(result_v2.columns)
# age_treatment = treatments.normalizing_age(result_v2)
# print(age_treatment)


