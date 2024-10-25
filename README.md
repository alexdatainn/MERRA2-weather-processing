# MERRA2 Data Processing

This project retrieves and processes meteorological data from MERRA2 netCDF4 files. It calculates air density and wind speed at a specified height and saves the processed data to a CSV file.

## Project Structure

- `merra2_data_processing.py`: Main script for fetching, processing, and saving MERRA2 data.
- `requirements.txt`: Lists all dependencies required to run the script.
- `MERRA2_20yrs/MERRA2_20yrs.txt`: Contains URLs for netCDF4 files.
- `MERRA2_20yrs/netfiles/`: Directory to temporarily save downloaded files.

## Requirements

- Python 3.x
- Packages: `requests`, `numpy`, `pandas`, `netCDF4`

Install the dependencies:

```bash
pip install -r requirements.txt
