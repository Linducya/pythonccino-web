import bcrypt
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
PEPPER_SECRET = os.getenv("PEPPER_SECRET")

def generate_password_hash(password: str) -> str:
  if not PEPPER_SECRET:
    raise ValueError("PEPPER_SECRET is missing from environment variables")
  
  # Combine password with pepper
  peppered_password = password + PEPPER_SECRET

  # Generate a salt
  salt = bcrypt.gensalt()

  # Hash the peppered password
  hashed_password = bcrypt.hashpw(peppered_password.encode('utf-8'), salt)
  return hashed_password.decode('utf-8')

if __name__ == "__main__":
  password = input("Enter a password to hash: ")
  hashed_password = generate_password_hash(password)
  print(f"Hashed password: {hashed_password}")