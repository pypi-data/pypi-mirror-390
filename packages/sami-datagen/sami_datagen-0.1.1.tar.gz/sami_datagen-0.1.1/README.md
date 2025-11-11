# DataGen - Synthetic Data Generation Library

A Python library for generating realistic synthetic datasets for testing, analytics, and machine learning experiments. DataGen provides modular, reproducible, and easy-to-use data generators for various domains.

## Features

**Four Specialized Generators:**
- **Profile Data** - User profiles with names, emails, addresses, and geographic coordinates
- **Salary Data** - Job titles, levels, compensation, and bonuses
- **Region Data** - Global regions with countries, timezones, and managers
- **Car Data** - Vehicle information with make, model, year, and pricing

**Key Capabilities:**
- **Reproducible** - Deterministic output with seed control
- **Flexible** - Multiple output formats (DataFrame, dict, CSV, JSON)
- **Localized** - Kenya-focused data with local context
- **Well-documented** - Comprehensive docstrings and examples
- **Type-safe** - Full type hints for better IDE support
- **Containerized** - Docker support for easy development

## Installation

### From PyPI (Recommended)

```bash
pip install sami-datagen
```

### From Source

```bash
git clone https://github.com/25thOliver/Datagen.git
cd Datagen
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Using Docker

DataGen includes Docker support for containerized development and deployment.

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/25thOliver/Datagen.git
cd Datagen

# Build and run with Docker Compose
docker-compose up -d

# Access the container
docker-compose exec datagen bash

# Inside the container, use datagen
python -c "from datagen import generate_profiles; print(generate_profiles(n=10))"
        or
python -m datagen.generators.profle
```

### Using Dockerfile Directly

```bash
# Build the Docker image
docker build -t datagen:latest .

# Run the container
docker run -it --rm \
  -v $(pwd):/app \
  -v datagen-cache:/root/.cache \
  datagen:latest

# Inside the container
python -c "from datagen import generate_profiles; print(generate_profiles(n=10))"
```

### Docker Configuration

**Dockerfile features**

- Base image: `python:3.11-slim`
- Includes git for version control
- Installs all dependencies from `requirements.txt`
- Install datagen in development mode
- Optimized layer caching for faster builds
- Optimized layer caching for faster builds
- Unbuffered Python output for real-time logs

**docker-compose.yml Features:**

- Servive name: `datagen`
- Container name: `datagen-dev`
- Volume mounting for live coding changes
- Cache volume for pip packages
- Interactive terminal support(stdin_open, tty)
- Working directory: `/app`

### Docker Use Cases

**1. Development Environment**
```bash
# Start development container
docker-compose up -d

# Run tests
docker-compose exec datagen pytest tests/

# Generate data
docker-compose exec datagen python -c "
from datagen import generate_profiles, save_data
df = generate_profiles(n=1000)
save_data(df, 'output/profiles.csv')
"

# Stop container
docker-compose down
```
**2. CI/CD Pipeline**

# Example GitHub Actions workflow
- name: Build Docker image
  run: docker build -t datagen:test .

- name: Run tests in container
  run: docker run --rm datagen:test pytest tests/ 

**3. Production Deployment**

```bash
# Build production image
docker build -t datagen:v0.1.0 .

# Run as a service
docker run -d \
  --name datagen-service \
  -v /path/to/output:/app/output \
  datagen:v0.1.0 \
  python -c "from datagen import generate_profiles, save_data; save_data(generate_profiles(10000), 'output/profiles.csv')"
```

**4. Batch Data Generation**

```bash
# Generate multiple datasets in parallel
docker run --rm -v $(pwd)/output:/app/output datagen:latest \
  bash -c "
    python -c 'from datagen import *; save_data(generate_profiles(5000), \"output/profiles.csv\")' &
    python -c 'from datagen import *; save_data(generate_salaries(5000), \"output/salaries.csv\")' &
    python -c 'from datagen import *; save_data(generate_regions(5000), \"output/regions.csv\")' &
    python -c 'from datagen import *; save_data(generate_cars(1000), \"output/cars.csv\")' &
    wait
  "
```

### Docker Best Practices

**- Volume Mounting**: Mount your output directory to persist generated data
**- Cache Volume**: Use named volumes for pip cache to speed up rebuilds
**- Resource Limits**: Set memory/CPU limits for production deployments
**- Multi-stage Builds**: For production, consider multi-stage builds to reduce image size
**- Security**: Run as non-root user in production environments

## Quick Start

### Basic Usage

```python
from datagen import generate_profiles, generate_salaries, generate_regions, generate_cars

# Generate 100 user profiles
profiles = generate_profiles(n=100, seed=42)
print(profiles.head())

# Generate 50 salary records
salaries = generate_salaries(n=50, seed=42, currency="KES")
print(salaries.head())

# Generate all global regions
regions = generate_regions(seed=42)
print(regions.head())

# Generate 25 car records
cars = generate_cars(n=25, seed=42)
print(cars.head())
```

### Saving Data

```python
from datagen import generate_profiles, save_data

# Generate and save to CSV
profiles = generate_profiles(n=1000, seed=42)
save_data(profiles, "profiles.csv", file_format="csv")

# Save to JSON
save_data(profiles, "profiles.json", file_format="json")

# Save to Excel
save_data(profiles, "profiles.xlsx", file_format="excel")

# Save to Parquet
save_data(profiles, "profiles.parquet", file_format="parquet")
```

## Detailed Usage

### 1. Profile Generator

Generate realistic user profiles with Kenyan localization.

```python
from datagen import generate_profiles

# Generate profiles with default settings
profiles = generate_profiles(
    n=100,                    # Number of profiles
    seed=42,                  # Random seed for reproducibility
    locale="en_KE",          # Locale (Kenya)
    output_format="dataframe" # Output format
)

# Output formats: 'dataframe', 'dict', 'csv', 'json'
profiles_dict = generate_profiles(n=10, output_format="dict")
profiles_csv = generate_profiles(n=10, output_format="csv")
```

**Generated Fields:**
- `profile_id` - Unique identifier (UUID)
- `first_name`, `last_name`, `full_name` - Name fields
- `email`, `username` - Contact information
- `gender` - Male, Female, or Non-binary
- `date_of_birth`, `age` - Age information
- `phone` - Phone number
- `street_address`, `city`, `state`, `postal_code`, `country` - Address
- `latitude`, `longitude` - Geographic coordinates (Kenya bounds)
- `created_at` - Account creation timestamp

### 2. Salary Generator

Generate salary data across multiple departments and experience levels.

```python
from datagen import generate_salaries

# Generate salary records
salaries = generate_salaries(
    n=100,
    seed=42,
    locale="en_KE",
    currency="KES",           # KES or USD
    output_format="dataframe"
)

# Analyze salary distribution
print(salaries.groupby('department')['total_compensation'].mean())
print(salaries.groupby('level')['base_salary'].describe())
```

**Generated Fields:**
- `salary_id`, `employee_id` - Identifiers
- `job_title` - Specific role (60+ titles across 8 departments)
- `department` - Engineering, Product, Data, Marketing, Sales, Operations, Finance, HR
- `level` - Junior, Mid, Senior, Lead, Principal, Manager, Senior Manager, Director, VP, C-Level
- `years_experience` - Years of experience aligned with level
- `base_salary` - Base annual salary
- `bonus` - Annual bonus amount
- `bonus_percentage` - Bonus as percentage of base
- `total_compensation` - Base + bonus
- `currency` - KES or USD
- `effective_date` - Salary effective date

**Supported Departments:**
- Engineering (18 roles)
- Product (9 roles)
- Data (10 roles)
- Marketing (9 roles)
- Sales (9 roles)
- Operations (7 roles)
- Finance (9 roles)
- HR (9 roles)

### 3. Region Generator

Generate global region data with timezone and country information.

```python
from datagen import generate_regions

# Generate all regions (default)
regions = generate_regions(seed=42, include_all=True)

# Generate random subset
regions = generate_regions(n=3, seed=42, include_all=False)
```

**Generated Fields:**
- `region_id` - Unique identifier
- `region_name` - North America, South America, Europe, Middle East, Africa, Asia Pacific
- `region_code` - NA, SA, EU, ME, AF, APAC
- `countries` - Comma-separated list of countries
- `country_count` - Number of countries in region
- `primary_timezone` - Main timezone
- `all_timezones` - All timezones in region
- `hq_city`, `hq_country` - Regional headquarters
- `regional_manager` - Manager name
- `manager_email` - Manager email
- `established_date` - Region establishment date

### 4. Car Generator

Generate vehicle data focused on the Kenyan automotive market.

```python
from datagen import generate_cars

# Generate car inventory
cars = generate_cars(
    n=100,
    seed=42,
    output_format="dataframe"
)

# Analyze pricing by make
print(cars.groupby('make')['price_kes'].mean())
```

**Generated Fields:**
- `car_id` - Unique identifier
- `make` - Toyota, Nissan, Mazda, Subaru, Mitsubishi, VW, BMW, Mercedes-Benz, Isuzu
- `model` - Specific model (Corolla, Probox, Note, Demio, Forester, etc.)
- `year` - Manufacturing year (2008-2025)
- `color` - Vehicle color
- `transmission_type` - Manual or Automatic
- `fuel_type` - Petrol or Diesel
- `assembled_in` - Country of assembly
- `dealer_city` - Nairobi, Mombasa, Kisumu, Eldoret, Nakuru
- `price_kes` - Price in Kenyan Shillings (with depreciation modeling)

## Advanced Features

### Reproducibility

All generators support deterministic output through seed control:

```python
# Same seed = same output
df1 = generate_profiles(n=100, seed=42)
df2 = generate_profiles(n=100, seed=42)
assert df1.equals(df2)  # True
```

### Custom Output Formats

```python
# Get as list of dictionaries
data = generate_profiles(n=10, output_format="dict")

# Get as CSV string
csv_string = generate_profiles(n=10, output_format="csv")

# Get as JSON string
json_string = generate_profiles(n=10, output_format="json")

# Get as pandas DataFrame (default)
df = generate_profiles(n=10, output_format="dataframe")
```

### Batch Generation

```python
# Generate large datasets efficiently
large_profiles = generate_profiles(n=10000, seed=42)
large_salaries = generate_salaries(n=10000, seed=42)

# Save to file
save_data(large_profiles, "large_profiles.parquet", file_format="parquet")
```

## CLI Usage

DataGen includes a command-line interface for quick data generation:

```bash
# Generate profiles
datagen profiles --count 100 --output profiles.csv

# Generate salaries
datagen salaries --count 50 --currency KES --output salaries.json

# Generate regions
datagen regions --output regions.csv

# Generate cars
datagen cars --count 25 --output cars.json

# With seed for reproducibility
datagen profiles --count 100 --seed 42 --output profiles.csv
```

## API Reference

### `generate_profiles(n, seed, locale, output_format)`

Generate synthetic user profile data.

**Parameters:**
- `n` (int): Number of profiles to generate. Default: 100
- `seed` (Optional[int]): Random seed for reproducibility. Default: None
- `locale` (str): Faker locale. Default: "en_KE"
- `output_format` (str): Output format. Options: 'dataframe', 'dict', 'csv', 'json'. Default: "dataframe"

**Returns:** Union[pd.DataFrame, List[Dict], str]

### `generate_salaries(n, seed, locale, currency, output_format)`

Generate synthetic salary data.

**Parameters:**
- `n` (int): Number of salary records. Default: 100
- `seed` (Optional[int]): Random seed. Default: None
- `locale` (str): Faker locale. Default: "en_KE"
- `currency` (str): Currency code. Options: 'KES', 'USD'. Default: "KES"
- `output_format` (str): Output format. Default: "dataframe"

**Returns:** Union[pd.DataFrame, List[Dict], str]

### `generate_regions(n, seed, include_all, output_format)`

Generate global region data.

**Parameters:**
- `n` (Optional[int]): Number of regions (ignored if include_all=True). Default: None
- `seed` (Optional[int]): Random seed. Default: None
- `include_all` (bool): Generate all predefined regions. Default: True
- `output_format` (str): Output format. Default: "dataframe"

**Returns:** Union[pd.DataFrame, List[Dict], str]

### `generate_cars(n, seed, output_format)`

Generate synthetic car data.

**Parameters:**
- `n` (int): Number of car records. Default: 100
- `seed` (Optional[int]): Random seed. Default: None
- `output_format` (str): Output format. Default: "dataframe"

**Returns:** Union[pd.DataFrame, List[Dict], str]

### `save_data(data, filename, file_format)`

Save data to file.

**Parameters:**
- `data` (Union[pd.DataFrame, List[Dict]]): Data to save
- `filename` (str): Output file path
- `file_format` (Optional[str]): File format. Options: 'csv', 'json', 'excel', 'parquet'. Auto-detected from filename if None.

## Examples

See the `examples/` directory for Jupyter notebooks demonstrating:
- Profile generation and analysis
- Salary distribution analysis
- Regional data mapping
- Car inventory management

## Requirements

- Python >= 3.8
- faker >= 18.0.0
- pandas >= 2.0.0
- numpy >= 1.24.0

## Development

### Setup Development Environment

```bash
git clone https://github.com/25thOliver/Datagen.git
cd Datagen
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
pytest --cov=datagen tests/
```

### Code Formatting

```bash
black datagen/
flake8 datagen/
mypy datagen/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- Code follows PEP 8 style guidelines
- All tests pass
- New features include tests
- Documentation is updated

## Author

**Sami**
- Email: os679736@gmail.com
- GitHub: [@25thOliver](https://github.com/25thOliver)

## Changelog

### Version 0.1.0 (Initial Release)
- Profile generator with Kenya localization
- Salary generator with 8 departments and 10 levels
- Region generator with 6 global regions
- Car generator with Kenya market focus
- Multiple output format support
- Reproducible generation with seed control
- CLI interface for quick generation
- Comprehensive documentation

## Support

If you encounter any issues or have questions:
- Open an issue on [GitHub](https://github.com/25thOliver/Datagen/issues)
- Email: os679736@gmail.com

## Roadmap

Future enhancements planned:
- [ ] Additional generators (transactions, events, logs)
- [ ] More locales and regions
- [ ] Data relationship support (foreign keys)
- [ ] Performance optimizations for large datasets
- [ ] Web UI for interactive generation
- [ ] More export formats (SQL, Avro)
- [ ] Data quality validation tools
- [ ] Kubernetes deployment examples
- [ ] Cloud deployment guides (AWS, GCP, Azure)

---