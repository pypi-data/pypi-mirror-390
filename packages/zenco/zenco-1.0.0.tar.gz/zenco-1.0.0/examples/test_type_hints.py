def calculate_sum(a, b):
    """Calculate the sum of two numbers."""
    return a + b


def greet_user(name, age):
    """Greet a user with their name and age."""
    message = f"Hello {name}, you are {age} years old!"
    return message


def process_data(items, multiplier=2):
    """Process a list of items by multiplying each by a factor."""
    result = []
    for item in items:
        result.append(item * multiplier)
    return result


def find_max(numbers):
    """Find the maximum number in a list."""
    if not numbers:
        return None
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val


def create_user_dict(username, email, is_active=True):
    """Create a dictionary representing a user."""
    return {
        "username": username,
        "email": email,
        "is_active": is_active
    }
