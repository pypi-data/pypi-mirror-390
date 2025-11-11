from typing import Optional, Union, List, Dict
import pandas as pd
from faker import Faker
import random
from datagen.utils.io import save_data 

def generate_profiles(
        n: int = 100,
        seed: Optional[int] = None,
        locale: str = "en_KE",
        output_format: str = "dataframe"
) -> Union[pd.DataFrame, List[Dict], str]:
    """
    Generate synthetic user profile data localized to Kenya.

    Each profile includes realistic Kenyan names, addresses, coordinates, and contact details.

    Args:
        n (int): Number of profiles to generate.
        seed (Optional[int]): Random seed for reproducibility.
        locale (str): Locale for Faker (default 'en_KE').
        output_format (str): Output format ('dataframe', 'dict', 'csv', 'json').

    Returns:
        Union[pd.DataFrame, List[Dict], str]: Generated data in the requested format.
    """

    # Validate inputs
    if n < 1:
        raise ValueError("Number of profiles (n) must be at least 1.")

    valid_formats = ['dataframe', 'dict', 'csv', 'json']
    if output_format not in valid_formats:
        raise ValueError(f"output_format must be one of {valid_formats}")

    # Initialize Faker for Kenya with reproducibility
    fake = Faker(locale)
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)

    # Kenyan city list for realism
    kenyan_cities = [
        "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret",
        "Thika", "Machakos", "Nyeri", "Garissa", "Naivasha"
    ]

    def generate_kenyan_phone():
        """
        Generate a realistic Kenyan phone number in the  format +254xxxxxxxxx

        Kenya mobile prefixes: 7xx or 1xx(Safaricom, Airtel or Telkom)
        Fromat: +254 7xx xxx xxx or +254 1xx xxx xxx
        """

        # Commonn Kenyan mobile prefixes
        prefixes = [
            '700', '701', '702', '703', '704', '705', '706', '707', '708', '709',  # Safaricom
            '710', '711', '712', '713', '714', '715', '716', '717', '718', '719',  # Safaricom
            '720', '721', '722', '723', '724', '725', '726', '727', '728', '729',  # Safaricom
            '740', '741', '742', '743', '745', '746', '748',  # Airtel
            '750', '751', '752', '753', '754', '755', '756', '757', '758', '759',  # Airtel
            '110', '111', '112', '113', '114', '115',  # Telkom
        ]

        prefix = random.choice(prefixes) 
        # Generate the remaining 6 digits
        remaining_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        return f"+254{prefix}{remaining_digits}"

    profiles = []
    genders = ['Male', 'Female', 'Non-binary']

    for _ in range(n):
        gender = random.choice(genders)

        # Gendered first names
        if gender == 'Male':
            first_name = fake.first_name_male()
        elif gender == 'Female':
            first_name = fake.first_name_female()
        else:
            first_name = fake.first_name()

        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}"

        # Generate contact info
        username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
        email = f"{username}@{fake.free_email_domain()}"

        # Birth date and age
        dob = fake.date_of_birth(minimum_age=18, maximum_age=80)
        from datetime import date
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        # Location and address (Kenya-scoped)
        city = random.choice(kenyan_cities)
        state = "Kenya"
        postal_code = fake.postcode()
        street_address = fake.street_address()
        country = "Kenya"

        # Geo realism — bounding box for Kenya
        latitude = round(random.uniform(-4.7, 5.0), 6)
        longitude = round(random.uniform(34.0, 41.9), 6)

        # Compile profile record
        profile = {
            'profile_id': fake.uuid4(),
            'first_name': first_name,
            'last_name': last_name,
            'full_name': full_name,
            'email': email,
            'username': username,
            'gender': gender,
            'date_of_birth': dob.strftime('%Y-%m-%d'),
            'age': age,
            'phone': generate_kenyan_phone(),
            'street_address': street_address,
            'city': city,
            'state': state,
            'postal_code': postal_code,
            'country': country,
            'latitude': latitude,
            'longitude': longitude,
            'created_at': fake.date_time_between(start_date='-2y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
        }

        profiles.append(profile)

    # Convert to desired output format
    if output_format == 'dict':
        return profiles

    df = pd.DataFrame(profiles)

    if output_format == 'dataframe':
        return df
    elif output_format == 'csv':
        return df.to_csv(index=False)
    elif output_format == 'json':
        return df.to_json(orient='records', indent=2)


if __name__ == "__main__":
    print("Generating 10 Kenya-localized sample profiles...")
    profiles = generate_profiles(n=10, seed=42, locale="en_KE")
    print(profiles.head())
    print(f"\nGenerated {len(profiles)} profiles")
    print(f"Columns: {list(profiles.columns)}")

    save_data(profiles, "./output/profiles.csv", file_format="csv")
