# import random

# PREFIXES = ["Al", "Pak", "Tech", "Green", "United", "Prime", "Blue", "Smart"]
# SUFFIXES = ["Traders", "Solutions", "Corporation", "Industries", "Enterprises", "Systems"]

# def company_name():
#     """Generate a random Pakistani-style company name."""
#     return f"{random.choice(PREFIXES)} {random.choice(SUFFIXES)}"
   

from faker_pk import FakerPK

fake = FakerPK()

print(fake.male_name())       # "Bilal Khan"
print(fake.female_name())     # "Ayesha Malik"
print(fake.cnic())            # "37405-7654321-9"
print(fake.phone_number())    # "+923001234567"
print(fake.city())            # "Lahore"
print(fake.province())        # "Punjab"
print(fake.full_address())    # "House No. 45, Street No. 6, Karachi, Sindh, 75000"
print(fake.company_name())    # "Te   