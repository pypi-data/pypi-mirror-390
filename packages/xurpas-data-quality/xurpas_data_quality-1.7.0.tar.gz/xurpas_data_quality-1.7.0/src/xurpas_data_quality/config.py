from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import List

class Colors(BaseModel):
    base_colors: List[str] = ['#17A2B8', "#28A745", "#0D6EFD", "#DC3545", "#FFC107"]

class Sampling(BaseModel):
    get_sampling: bool = True
    auto: bool = True
    size: float = 0.1
    auto_length: int = 100000

class Visualizations(BaseModel):
    correlation: bool = True
    missing: bool = True
    interactions: bool = True

class Settings(BaseSettings):
    colors: Colors = Colors()
    report_name: str = "Data Quality Report"
    minimal: bool = True
    file_path:str= "report.html"
    sampling: Sampling = Sampling()
    visualizations: Visualizations = Visualizations()