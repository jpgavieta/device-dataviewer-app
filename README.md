
# Device Dataviewer

A portable Python dashboard to upload and view data, sourced from one or more devices. 
Expandable ETL pipeline to allow for the later additions in data sources (i.e. Atmotube, Raspberry Pi Sensors [PonyoPi], FitBit, Whatsapp, etc.) and its accompanying parser.

---

## What's in here?

```
dataDashboard/
├── app.py                      # `panel serve app.py` to run dashboard GUI
├── environment.yml
├── src/
|   ├── __init__.py
|   ├── etl.py                  # Extract (uploads data), Transform (applies parser), Load CSV (returns dfs)
|   ├── utils.py                # Incl. shared auto-detectors (i.e. JSON-blobs, UTC, lat/lon), map builder (gis_df)
|   ├── parsers/                # Builds specific-to-device dfs
|   |   ├── atmotube.py
|   |   └── ponyopi.py
|   └── plots/                  # Builds generic plots 
|       ├── map.py              
|       ├── timeline.py         
|       ├── heatmap.py          
├── notebooks/
|   ├── sample_data/            # Raw csv only for testing any code, before implementation into the dashboard pipeline
|   ├── scratchpad_utils.ipynb  
|   ├── scratchpad_etl.ipynb  
|   └── scratchpad_plots.ipynb  
└── docs/                       # Documentation for every data source (device)
    ├── Atmotube_datasheet.md
    └── etc.
```


---

## How to use dashboard?

1. Create and activate conda env

Inside VSCode, Ctrl + Shift + ` to automatically open the terminal with this repo as the current directory

```bash
conda env create -f environment.yml
conda activate multidevice_dashboard 
```
Note: Works with either _mamba_ or _conda_ installer. If Linux user, _mamba_ is recommended. 


2. Run dashboard GUI with panel

```
panel serve app.py 
```

3. Choose device and variables to visualize

    Upload CSV (reads as bytes)
        ↓
    Select Device (applies parser)
        ↓
    Select Variables (filters columns)
        ↓ 
    *Optional: Clean Data (removes missing rows)

---

## How to use notebooks? 

Use to test-run any code chunks (functions) before implementing into the actual pipeline.
Uncomment the `.gitignore` to pretends notebook/ doesn't exist. 

ALWAYS create and activate conda env (`multidevice_dashboard`) before running any code.

### Writing new code

1. Upload any test data as raw CSV under `notebooks/sample_data`
2. Add a new notebook under `notebooks/`
3. Select Python interpreter for the notebook
    - Ctrl + Shift + P → type `Python: Select Interpreter` → `multidevice_dashboard`
4. Write and run code chunks using real data from `notebooks/sample_data`

Notes: Don't forget to `Clear Outputs` and `Restart` to clear the cache.

### Adding new parser

1. Add `src/parsers/yourdevice.py` with a `parse(df)` function
2. Import parser module and add to registry list in `src/etl.py`
3. Add its datasheet to `docs/`

Note: Uncomment the `.gitignore` to pretend the notebook doesn't exist. 

