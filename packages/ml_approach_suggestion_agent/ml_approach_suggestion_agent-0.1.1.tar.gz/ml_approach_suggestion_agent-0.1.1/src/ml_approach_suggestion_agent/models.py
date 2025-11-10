from pydantic import BaseModel, Field
from typing import Literal

class MethodologyRecommendation(BaseModel):
    selected_methodology: Literal[ "binary_classification", "time_series_forecasting", "not_applicable"] = Field(..., description="The most appropriate ML approach for this problem")
    
    justification: str = Field( ..., description="Clear explanation connecting the business goal and data characteristics to the chosen methodology")
