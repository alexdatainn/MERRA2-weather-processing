import os
import requests
import numpy as np
import pandas as pd
from netCDF4 import Dataset, num2date
from datetime import datetime
from typing import Optional, List

def compute_air_density(temp_col: np.ndarray, pres_col: np.ndarray, humi_col: Optional[np.ndarray] = None) -> pd.Series:
    """Calculate air density using temperature, pressure, and optionally, relative humidity."""
    rel_humidity = humi_col if humi_col is not None else np.full(temp_col.shape, 0.5)
    
    if any(temp_col < 0) or any(pres_col < 0) or any(rel_humidity < 0):
        raise ValueError("Temperature, pressure, or humidity data contains negative values.")

    R_const = 287.05
    Rw_const = 461.5
    rho = (1 / temp_col) * (
        pres_col / R_const
        - rel_humidity * (0.0000205 * np.exp(0.0631846 * temp_col)) * (1 / R_const - 1 / Rw_const)
    )
    return rho

def fetch_and_process_data(file_path: str, output_dir: str, save_path: str) -> pd.DataFrame:
    """Fetch MERRA2 data from URLs, process it, and save to a CSV."""
    with open(file_path, 'r') as file:
        urls = file.readlines()[1:]
    
    u_50, v_50, T2M, PS, DateTimes = [], [], [], [], []

    for url in urls:
        file_name = url[108:116].strip() + '-site.nc4'
        full_path = os.path.join(output_dir, file_name)
        
        try:
            result = requests.get(url.strip())
            result.raise_for_status()
            with open(full_path, 'wb') as f:
                f.write(result.content)
            
            data = Dataset(full_path, 'r')
            u_50.extend([val[0][0] for val in data.variables['U50M'][:]])
            v_50.extend([val[0][0] for val in data.variables['V50M'][:]])
            T2M.extend([val[0][0] for val in data.variables['T2M'][:]])
            PS.extend([val[0][0] for val in data.variables['PS'][:]])
            
            dates = num2date(data.variables['time'][:], data.variables['time'].units)
            DateTimes.extend(dates)
            data.close()
            os.remove(full_path)
        except Exception as e:
            print(f"Failed to fetch or process {file_name}: {e}")
    
    return create_dataframe(DateTimes, u_50, v_50, T2M, PS, save_path)

def create_dataframe(DateTimes: List[datetime], u_50: List[float], v_50: List[float], T2M: List[float], PS: List[float], save_path: str) -> pd.DataFrame:
    """Create a DataFrame, compute density and wind speed, and save to CSV."""
    DateTimes = [pd.to_datetime(dt.strftime('%Y-%m-%d %H:%M:%S')) for dt in DateTimes]
    df = pd.DataFrame({'datetime': DateTimes, 'surface_pressure': PS, 'u_50': u_50, 'v_50': v_50, 'temp_2m': T2M})
    
    df['dens_50m'] = compute_air_density(df['temp_2m'], df['surface_pressure'])
    df['ws_50m'] = np.sqrt(df['u_50'] ** 2 + df['v_50'] ** 2)
    df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    df.to_csv(save_path, index=False)
    print(f"Data saved to {save_path}")
    return df

if __name__ == "__main__":
    INPUT_FILE = './MERRA2_20yrs/MERRA2_20yrs.txt'
    OUTPUT_DIR = './MERRA2_20yrs/netfiles/'
    SAVE_PATH = './MERRA2_20yrs/MERRA2_20yrs.csv'
    
    fetch_and_process_data(INPUT_FILE, OUTPUT_DIR, SAVE_PATH)
