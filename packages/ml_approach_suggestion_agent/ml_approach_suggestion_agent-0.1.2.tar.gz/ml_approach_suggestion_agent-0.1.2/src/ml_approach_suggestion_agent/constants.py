METHODOLOGY_SELECTION_SYSTEM_PROMPT = """You are an ML methodology advisor. Analyze the problem and select ONE methodology: binary_classification, time_series_forecasting, or not_applicable.

**Simple Decision Rules:**

1. **Binary Classification** - Choose when:
   - Use case asks "predict whether", "will X happen", "classify if"
   - Answer is YES/NO, TRUE/FALSE, or 1/0
   - Example: "predict if machine fails", "detect fraud", "identify churn"

2. **Time Series Forecasting** - Choose when:
   - Use case asks to "forecast", "predict future value", "estimate next"
   - Answer is a NUMERICAL value in the FUTURE
   - Example: "forecast next month sales", "predict tomorrow's temperature"

3. **Not Applicable** - Choose when:
   - No prediction needed
   - Just data analysis, reporting, or calculations
   - Not enough information
**Required Output:**
1. Select the single best ML methodology from: binary_classification, time_series_forecasting, or not_applicable
2. Provide a clear justification explaining:
   - What you understand the business goal to be
   - What type of prediction is needed (binary outcome, numerical forecast, or none)
   - Whether temporal patterns are critical for this prediction
   - Why the selected methodology is the best fit

**Important:**
- Having timestamps doesn't mean it's time series forecasting
- Check WHAT is being predicted: binary outcome OR future number
- The dataset may contain 1-4 tables - analyze all provided tables together"""



METHODOLOGY_SELECTION_USER_PROMPT = """**Business Context:**
Domain: {domain_name}
{domain_description}

**Use Case:**
{use_case_description}

**Data Overview:**
Columns: {column_descriptions}

Dataset Characteristics:
{column_insights}

"""


def format_approach_prompt(
    domain_name: str,
    domain_description: str,
    use_case: str,
    column_descriptions: str,
    column_insights: str
) -> tuple[str, str]:
    """
    Format the methodology selection prompts for the LLM.
    
    Args:
        domain_name: The domain of the data (e.g., "Healthcare", "Finance")
        domain_description: Detailed description of the domain context
        use_case: Description of what the user wants to achieve
        column_descriptions: Description of the columns in the dataset
        column_insights: Statistical insights about the columns (data types, 
                        unique counts, distributions, etc.)
    
    Returns:
        tuple[str, str]: The formatted system prompt and user prompt
    
    Example:
        system_prompt, user_prompt = format_approach_prompt(
            domain_name="E-commerce",
            domain_description="Online retail platform with customer transactions",
            use_case="Predict if a customer will make a purchase",
            column_descriptions="user_id, page_views, cart_additions, timestamp",
            column_insights="4 columns, 10000 rows, mixed types"
        )
    """
    user_prompt = METHODOLOGY_SELECTION_USER_PROMPT.format(
        domain_name=domain_name,
        domain_description=domain_description,
        use_case_description=use_case,
        column_descriptions=column_descriptions,
        column_insights=column_insights
    )
    
    return METHODOLOGY_SELECTION_SYSTEM_PROMPT, user_prompt