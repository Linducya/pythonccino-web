import asyncio
from app.db import init_db, store_totp_secret, get_totp_secret

async def test_totp_secret():
    await init_db()  # Ensure the database is initialized
    username = "test_user"
    secret = "test_secret"

    # Store the TOTP secret
    await store_totp_secret(username, secret)

    # Retrieve the TOTP secret
    retrieved_secret = await get_totp_secret(username)

    # Assert that the stored and retrieved secrets match
    assert retrieved_secret == secret, f"Expected {secret}, got {retrieved_secret}"
    print("Test passed!")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_totp_secret())