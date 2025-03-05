import bcrypt

def generate_password_hash(password: str) -> str:
  # Generate a salt
  salt = bcrypt.gensalt()
  # Generate a hashed password
  hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
  return hashed_password.decode('utf-8')

if __name__ == "__main__":
  password = input("Enter a password to hash: ")
  hashed_password = generate_password_hash(password)
  print(f"Hashed password: {hashed_password}")