# Code for the Analysis of the Environmental Effects on COVID-19 Transmission in Africa

## Overview
This repository contains the code and documentation for my 2024 Applied Data Institute capstone project in the Data and Decisions course. The project focuses on decoding datasets, cleaning, merging and using them for the analysis.
You can find the paper and read it here: [capstone paper](https://drive.google.com/file/d/1h8Cr2Tk65ZsnM_dgIwLgckvx6SvX0pp4/view?usp=sharing)

## Project Structure
- `Datasets/`: Main Datasets used for the application.
- `extract_environmental_data.py`: Script to decode the grib formatted data.
- `preprocess.py`: Script to clean and preprocess the resulting data
- `generate_paper_statistics.py`: Script to run the analysis and generate the key numbers shared in the paper.
- `generate_paper_figures`: Script to generate the figures used in the paper.
- `processed_african_covid_data.csv`: Final merged script that was used for the Analysis.

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/Phinart98/Data-and-Decisions-Capstone.git
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the scripts:

If you only want to reproduce the analysis and figures,
Run the last two files as repeated below:

```bash
python generate_paper_statistics.py
python generate_paper_figures.py
```

If you want reproduce the environmental data extraction and preprocessing, then download the grib dataset from the following link: [Copernicus Enviromental Dataset](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels-monthly-means?tab=overview)

Create a folder called 'environmental-data' in the root folder and place the grib file in it.

Run the following files in the order listed

```bash
python extract_environmental_data.py
python preprocess.py
python generate_paper_statistics.py
python generate_paper_figures.py
```
