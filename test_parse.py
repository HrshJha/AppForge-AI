import re

err_msg = "Rate limit reached for model... Please try again in 29.86s. Need more tokens?"
match = re.search(r"try again in ([\d\.]+)s", err_msg)
if match:
    print(float(match.group(1)))
