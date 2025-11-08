# Revealed Comparative Advantage Calculator

[![PyPI - Version](https://img.shields.io/pypi/v/rca-batch-calc?color=green)](https://pypi.org/project/rca-batch-calc/)
[![DOI](https://zenodo.org/badge/978591723.svg)](https://doi.org/10.5281/zenodo.15578976)

This is the repository associated with the manuscript _Competitiveness analysis to identify marginal suppliers in consequential LCA: A seaweed case_. 

The repository is designed as a Python library to help users calculate Revealed Comparative Advantage (RCA) using BACI trade data.

## 📖 Background Knowledge 

### BACI Dataset
The [BACI](https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37) (from CEPII) dataset offers detailed information on bilateral trade flows for 200 countries, broken down by product (covering 5,000 products). The data spans various time periods, ranging from 2 to 28 years, depending on the specific dataset. Each year's data is stored in a separate `CSV` file. Each file contains six columns: _t = year_, _i = exporter_, _j = importer_, _k = product_, _v = value_, and _q = quantity_, and comprises over one million rows of data. 

This library can calculate RCA for both _quantity_ (metric tons) and _value_ (thousand USD).

### Revealed Comparative Advantage (RCA)
In international economics, the RCA is a metric that evaluating the relative advantage or disadvantage of a certain country in a certain class of goods or services as evidenced by trade flows. It is based on the Ricardian comparative advantage concept. [WIKI](https://en.wikipedia.org/wiki/Revealed_comparative_advantage)  

### Formula
$RCA^i_j = \left( \frac{X^i_j}{X^i_n} \middle/ \frac{X^w_j}{X^w_n} \right)$ 
Where:
- $X^i_j$: Export value of commodity i from a country to country j.
- $X^i_n$: Total export value of commodity i from all exporting countries to country j.
- $X^w_j$: Total export value of all commodities from a country to country j.
- $X^w_n$: Total export value of all commodities from all exporting to country j.
- $RCA^i_j$: Comparative advantage of commodity i of a country in country j.
  
Reference:  
[Competitiveness of Indonesian Non-Human Consumption Seaweed in the China Market.pdf](https://github.com/user-attachments/files/17606696/Competitiveness.of.Indonesian.Non-Human.Consumption.Seaweed.in.the.China.Market.pdf)  

## ✨ Features
(applicable to all BACI dataset versions)
1. Get the data for specific products from the BACI dataset.
2. Calculate RCA in batches.
3. Convert country codes into country names.

## 👩‍💻 Quick Start 
### Requirements
- This project was developed using **Python 3.12.9**.

### Option 1. Install via pip
1. Open your local terminal.  
(For windows, search for "Terminal/Prompt/PowerShell"; for macOS, search for "Terminal")

2. Install the library.
   ```
   pip install rca_batch_calc
   ```
3. Follow the instructions in [Example](https://github.com/Annedrew/Revealed-Comparative-Advantage-Calculator/blob/main/example_notebook.ipynb) to use the library. 

### Option 2. Clone and run from GitHub
1. Open your local terminal.  
(For windows, search for "Terminal/Prompt/PowerShell"; for macOS, search for "Terminal")
2. Clone this repository into your local computer
```
git clone https://github.com/Annedrew/Revealed-Comparative-Advantage-Calculator.git
```
3. Navigate into the project folder:
```
cd Revealed-Comparative-Advantage-Calculator
```
4. Install dependencies:
```
pip install pandas
```
5. Follow the instructions in [Example](https://github.com/Annedrew/Revealed-Comparative-Advantage-Calculator/blob/main/example_notebook.ipynb) to use the library. 

## 💬 Contact
If you encounter any issues or would like to contribute to the library, please contact: 
  - Ning An (ningan@plan.aau.dk)
  - Ravalnath Shikhare (ravshi@plan.aau.dk)
  - Massimo Pizzol (massimo@plan.aau.dk)

## Funding
Ravalnath Shikhare’s contribution is funded by the FunSea Project (Horizon Europe BlueBio Partnership, grant number 3157-00016B). Ning An’s contribution is funded by the ALIGNED project (Horizon Europe, grant number 101059430). Massimo Pizzol’s contribution is funded by both FunSea and ALIGNED.

## Acknowledgements
The work was partially supported by DeiC National HPC (g.a. DeiC-AAU-L1-402401).

## Conflict of Interest statement
The authors declare no conflict of interest.
