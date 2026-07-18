import pandas as pd
from pathlib import Path

# Set the path to the file you'd like to load

current_dir =Path(__file__).parent.resolve()
file_path = current_dir / "pacientes.csv"
df = pd.read_csv(file_path)
print(df.head())

