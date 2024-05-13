import re


class Verify:
    def password_verifier(password: str):
        # Check if the password has at least 8 characters
        if len(password) < 8:
            return 0

        # Check if the password contains at least one uppercase letter
        if not re.search(r"[A-Z]", password):
            return 0

        # Check if the password contains at least one lowercase letter
        if not re.search(r"[a-z]", password):
            return 0

        # Check if the password contains at least one digit
        if not re.search(r"\d", password):
            return 0

        # Check if the password contains at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return 0

        # If all the conditions are met, the password is valid
        return 1
