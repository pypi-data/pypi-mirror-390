"""
Synthetic salary data generator for the `datagen` library.

This module generates realistic synthetic salary data for various job titles,
levels (e.g., Junior, Mid, Senior), and compensation bands. It produces reproducible
outputs when a random seed is provided and supports multiple output formats.

Example:
    >>> from datagen.generators.salary import generate_salaries
    >>> df = generate_salaries(n=50, seed=123)
    >>> print(df.head())

Typical fields:
    salary_id
    employee_id
    job_title
    department
    level
    years_experience
    base_salary
    bonus
    bonus_percentage
    total_compensation
    currency
    effective_date
"""

from typing import Optional, Union, List, Dict
import pandas as pd
from faker import Faker
import random
from datagen.utils.io import save_data

"""
Generate synthetic salary records with deterministic reproducibility.

    The function creates salary data across different roles and experience levels.
    Salary bands are loosely modeled on real-world distributions, ensuring realistic
    but anonymized compensation data.

    Args:
        n (int): Number of salary records to generate. Must be >= 1.
        seed (Optional[int]): Random seed for reproducibility.
        locale (str): Faker locale to control region/language (default: 'en_US').
        output_format (str): Output format — one of ['dataframe', 'dict', 'csv', 'json'].

    Returns:
        Union[pd.DataFrame, List[Dict], str]: The generated salary dataset in the
        requested format.

    Raises:
        ValueError: If `n < 1` or if `output_format` is invalid.

    Example:
        >>> df = generate_salaries(n=10, seed=42)
        >>> df.columns
        ['salary_id', 'employee_id', 'job_title', 'level', 'years_experience', 'department', 'base_salary',
         'bonus', 'bonus_percenyage', 'total_compensation', 'currency', 'effective_date']
"""


# Job titles by department
JOB_TITLES = {
    'Engineering': [
        'Software Engineer', 'Senior Software Engineer', 'Staff Software Engineer',
        'Principal Engineer', 'Engineering Manager', 'Senior Engineering Manager',
        'Director of Engineering', 'VP of Engineering', 'CTO',
        'DevOps Engineer', 'Site Reliability Engineer', 'Security Engineer',
        'Frontend Engineer', 'Backend Engineer', 'Full Stack Engineer',
        'Mobile Engineer', 'QA Engineer', 'Data Engineer'
    ],
    'Product': [
        'Product Manager', 'Senior Product Manager', 'Principal Product Manager',
        'Director of Product', 'VP of Product', 'Chief Product Officer',
        'Product Designer', 'UX Researcher', 'Product Analyst'
    ],
    'Data': [
        'Data Analyst', 'Senior Data Analyst', 'Data Scientist',
        'Senior Data Scientist', 'Staff Data Scientist', 'ML Engineer',
        'Data Engineering Manager', 'Director of Data Science',
        'VP of Data', 'Chief Data Officer'
    ],
    'Marketing': [
        'Marketing Manager', 'Senior Marketing Manager', 'Director of Marketing',
        'VP of Marketing', 'CMO', 'Content Marketing Manager',
        'Growth Marketing Manager', 'Brand Manager', 'Marketing Analyst'
    ],
    'Sales': [
        'Sales Representative', 'Account Executive', 'Senior Account Executive',
        'Sales Manager', 'Senior Sales Manager', 'Director of Sales',
        'VP of Sales', 'Chief Revenue Officer', 'Business Development Manager'
    ],
    'Operations': [
        'Operations Manager', 'Senior Operations Manager', 'Director of Operations',
        'VP of Operations', 'COO', 'Program Manager', 'Project Manager'
    ],
    'Finance': [
        'Financial Analyst', 'Senior Financial Analyst', 'Finance Manager',
        'Senior Finance Manager', 'Director of Finance', 'VP of Finance',
        'CFO', 'Controller', 'Accountant'
    ],
    'HR': [
        'HR Manager', 'Senior HR Manager', 'Director of HR', 'VP of HR',
        'Chief People Officer', 'Recruiter', 'Senior Recruiter',
        'Talent Acquisition Manager', 'HR Business Partner'
    ]
}

# Employee levels with typical salary ranges (USD)
LEVEL_RANGES_USD = {
    'Junior': {'base': (50000, 70000), 'bonus_pct': (0, 10)},
    'Mid': {'base': (70000, 100000), 'bonus_pct': (5, 15)},
    'Senior': {'base': (100000, 150000), 'bonus_pct': (10, 20)},
    'Lead': {'base': (130000, 180000), 'bonus_pct': (15, 25)},
    'Principal': {'base': (160000, 220000), 'bonus_pct': (20, 30)},
    'Manager': {'base': (120000, 170000), 'bonus_pct': (15, 25)},
    'Senior Manager': {'base': (150000, 200000), 'bonus_pct': (20, 30)},
    'Director': {'base': (180000, 250000), 'bonus_pct': (25, 35)},
    'VP': {'base': (220000, 350000), 'bonus_pct': (30, 50)},
    'C-Level': {'base': (300000, 500000), 'bonus_pct': (40, 80)}
}

LEVEL_RANGES_KES = {
    'Junior': {'base': (600000, 1200000), 'bonus_pct': (0, 5)},
    'Mid': {'base': (1200000, 2400000), 'bonus_pct': (3, 10)},
    'Senior': {'base': (2400000, 4000000), 'bonus_pct': (5, 15)},
    'Lead': {'base': (4000000, 5500000), 'bonus_pct': (10, 20)},
    'Principal': {'base': (5500000, 7500000), 'bonus_pct': (10, 25)},
    'Manager': {'base': (3000000, 5000000), 'bonus_pct': (10, 20)},
    'Senior Manager': {'base': (5000000, 7000000), 'bonus_pct': (15, 25)},
    'Director': {'base': (7000000, 10000000), 'bonus_pct': (20, 30)},
    'VP': {'base': (10000000, 15000000), 'bonus_pct': (25, 40)},
    'C-Level': {'base': (15000000, 30000000), 'bonus_pct': (30, 60)}
}

# Determine employee salary based on job title
def determine_level(job_title: str) -> str:
    title_lower = job_title.lower()

    if any(x in title_lower for x in ['cto', 'cfo', 'coo', 'cmo', 'cpo', 'cdo', 'cro', 'chief']):
        return 'C-Level'
    elif 'vp' in title_lower or 'vice president' in title_lower:
        return 'VP'
    elif 'director' in title_lower:
        return 'Director'
    elif 'senior manager' in title_lower:
        return 'Senior Manager'
    elif 'manager' in title_lower:
        return 'Manager'
    elif 'principal' in title_lower:
        return 'Principal'
    elif 'lead' in title_lower or 'staff' in title_lower:
        return 'Lead'
    elif 'senior' in title_lower or 'sr' in title_lower:
        return 'Senior'
    elif 'junior' in title_lower or 'jr' in title_lower:
        return 'Junior'
    else:
        return 'Mid'
    
# Salary Generator    
def generate_salaries(
        n: int=100,
        seed: Optional[int] = None,
        locale: str = "en_KE",
        currency: str = "KES",
        output_format: str = "dataframe"
) -> Union[pd.DataFrame, List[Dict], str]:
        
    # Validate inputs
        if n < 1:
            raise ValueError("Number of salary records (n) must be atleast 1")
        
        valid_formats = ['dataframe', 'dict', 'csv', 'json']
        if output_format not in valid_formats:
            raise ValueError(f"output_format must be one of {valid_formats}")
        
        # Pick correct ranges
        LEVEL_RANGES =LEVEL_RANGES_KES if currency == "KES" else LEVEL_RANGES_USD
        
        # Initialize Faker with seed for reproducibility
        fake = Faker(locale)
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

        salaries = []

        for _ in range(n):
            # Select random department and job title
            department = random.choice(list(JOB_TITLES.keys()))
            job_title = random.choice(JOB_TITLES[department])

            # Determine level based on job title
            level = determine_level(job_title)

            # Get salary range for this level
            salary_range = LEVEL_RANGES[level]
            base_min, base_max = salary_range['base']
            bonus_min, bonus_max = salary_range['bonus_pct']

            # Generate base salary
            base_salary = random.randint(base_min, base_max)
            # Round to nearest 1000
            base_salary = round(base_salary / 1000) * 1000

            # Generate bonus
            bonus_pct = random.uniform(bonus_min, bonus_max)
            bonus = int(base_salary * (bonus_pct / 100))
            # Round to nearest 100
            bonus = round(bonus / 100) * 100

            # Calculate total compensation
            total_comp = base_salary + bonus

            # Generate years of experience based on level
            exp_ranges = {
                'Junior': (0, 3),
                'Mid': (2, 6),
                'Senior': (5, 10),
                'Lead': (7, 12),
                'Principal': (10, 20),
                'Manager': (5, 10),
                'Senior Manager': (8, 15),
                'Director': (10, 20),
                'VP': (15, 25),
                'C-Level': (20, 35)
            }
            exp_min, exp_max = exp_ranges[level]
            years_exp = random.randint(exp_min, exp_max)

            # Create salary record
            salary_record = {
                'salary_id': fake.uuid4(),
                'employee_id': fake.uuid4(),
                'job_title': job_title,
                'department': department,
                'level': level,
                'years_experience': years_exp,
                'base_salary': base_salary,
                'bonus': bonus,
                'bonus_percentage': round(bonus_pct, 2),
                'total_compensation': total_comp,
                'currency': currency,
                'effective_date': fake.date_between(start_date='-2y', end_date='today').strftime('%Y-%m-%d')
            }

            salaries.append(salary_record)
        
        # Convert to requested format
        if output_format == 'dict':
            return salaries
        
        df = pd.DataFrame(salaries)
        
        if output_format == 'dataframe':
            return df
        elif output_format == 'csv':
            return df.to_csv(index=False)
        elif output_format == 'json':
            return df.to_json(orient='records', indent=2)
        

if __name__ == "__main__":
    print("Generating 10 Kenya-localized salary records...")
    salaries = generate_salaries(n=10, seed=42, locale="en_KE", currency="KES")
    print(salaries)
    save_data(salaries, "./output/salaries.csv", file_format="csv")