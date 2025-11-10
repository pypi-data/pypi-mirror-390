# Xurpas Data Quality Report

## How to Use
- Load the data to be analyzed (so far only csv files supported)
- Import the DataReport class
- Save the report to html File

## DataReport
Creates and saves to file the data report.

**Args**
>**file**:&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;The path of the file you want to analyze. If empty, df parameter must exist.  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; Only supports .csv, .xlsx, .parquet, and .orc file formats.  
>**df**:&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Pandas DataFrame object of data to be analyzed, If using df, file must be empty.  
>**report_name**: &emsp;&emsp;Name of the report. Defaults to 'Data Report'.  
>**file_path**:&emsp;&emsp;&emsp;&emsp;&nbsp;Path/ directory of where the report is to be saved.  
>**data_types**:&emsp;&emsp;&emsp; A dict containing the column names and column type to specify column data type.
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; Data Types currently allowed "Categorical, Numerical, Date, Text".  
>**minimal**:&emsp;&emsp;&emsp;&emsp;&nbsp;Default is **True**. A boolean to check if you want minimal mode as your data report.  
>**sample_mode**:&emsp;&emsp;&nbsp;The mode of sampling. Choose between 'auto', 'manual', or 'none'. Default is 'auto'. If 'manual', you must provide a sample_size parameter. If 'none', no sampling is done to the data.  
>**sample_size**:&emsp;&emsp;&nbsp;The fraction of the data to be sampled. Only used when sample_mode is 'manual'.  
>**auto_sample_dataset_length**:&emsp;&emsp;&nbsp;The length of the dataset to be sampled. Only used when sample_mode is 'auto'. If empty, defaults to 100000.  
>**config_file**:&emsp;&emsp;&nbsp;Optional. The path of the configuration file. If empty, default values will be used.

**Returns**
>HTML File of data quality Report

#### Sample Usage using pandas DataFrame
```python
import pandas as pd
from xurpas_data_quality import DataReport

df = pd.read_csv("manhour_utilization_summary.csv")
report = DataReport(df=df,
                    report_name="Manhour Utilization Summary", 
                    file_path="test_reports/test.html")
report.to_file()
```

#### Sample Usage using filepath
```python
from xurpas_data_quality import DataReport
report = DataReport(file="manhour_utilization_summary.csv",
                    report_name="Manhour Utilization Summary", 
                    file_path="test_reports/test.html")
report.to_file()
```


#### Sample Usage with a config file
```python
from xurpas_data_quality import DataReport
report = DataReport(file="manhour_utilization_summary.csv",
                    report_name="Manhour Utilization Summary", 
                    file_path="test_reports/test.html",
                    config_file ="./path_to_config_file/config.yaml")
report.to_file()
```
