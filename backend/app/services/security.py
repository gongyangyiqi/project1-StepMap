import bcrypt


def hash_password(password: str) -> str:
    truncated = password[:72]
    hashed = bcrypt.hashpw(truncated.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated = plain_password[:72]
    return bcrypt.checkpw(
        truncated.encode("utf-8"), hashed_password.encode("utf-8")
    )

