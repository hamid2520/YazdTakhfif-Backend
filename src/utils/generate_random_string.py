import random
import string


def generate_random_code(digits=None):
    if not digits:
        digits = 8

    all_characters = string.ascii_uppercase + string.ascii_lowercase + string.digits

    random_code = ''.join(random.choice(all_characters) for _ in range(digits))

    return random_code
