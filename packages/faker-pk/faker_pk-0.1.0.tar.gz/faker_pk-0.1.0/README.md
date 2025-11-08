# faker-pk

A simple Python library to generate fake **Pakistani** names, CNICs, phone numbers, and addresses for testing or demo purposes.

---

## 🧩 Installation

```bash
pip install faker-pk
```

---

## Usage   
```
from faker_pk import FakerPK

fake = FakerPK()

print(fake.male_name())       # "Bilal Khan"
print(fake.female_name())     # "Ayesha Malik"
print(fake.cnic())            # "37405-7654321-9"
print(fake.phone_number())    # "+923001234567"
print(fake.city())            # "Lahore"
print(fake.province())        # "Punjab"
print(fake.full_address())    # "House No. 45, Street No. 6, Karachi, Sindh, 75000"
print(fake.company_name())    # "Tech Solutions"

# Generate multiple
print(fake.male_name(5))
# ['Ali Khan', 'Usman Raza', 'Zain Qureshi', ...]
```