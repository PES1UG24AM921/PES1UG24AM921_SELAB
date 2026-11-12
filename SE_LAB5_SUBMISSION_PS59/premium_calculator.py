"""Insurance premium calculator with safe data handling."""

import math
import secrets
import ssl
import tarfile
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

from defusedxml import ElementTree as DET

quotes = {}
HOST = "127.0.0.1"
UNDERWRITER_TOKEN = "uw-" + secrets.token_hex(4)
LOG_FILE = Path(__file__).resolve().with_name("premium_quotes.log")
BASE_RATES = {"health": 5000, "motor": 3000, "life": 8000}


# pylint: disable=too-many-arguments,too-many-positional-arguments
def calculate_premium(
        policy_type,
        age,
        sum_insured,
        smoker,
        claims,
        discounts=None,
):
    """Calculate a premium based on policy attributes and discount list."""
    if policy_type not in BASE_RATES:
        raise ValueError(f"Unsupported policy type: {policy_type}")
    if age < 0 or sum_insured < 0:
        raise ValueError("Age and sum insured cannot be negative.")

    local_discounts = list(discounts or [])
    base = BASE_RATES[policy_type]
    premium = base + (sum_insured * 0.002)

    if age > 45:
        premium *= 1.5
    if smoker in (True, 1, "yes", "Y", "y", "true", "True"):
        premium *= 1.3

    premium += claims * 1000
    for discount in local_discounts:
        premium -= discount
    premium = max(premium, 0)
    local_discounts.append(500)
    return premium


def age_from_dob(dob):
    """Return the age represented by a date of birth string."""
    born = datetime.strptime(dob, "%d-%m-%Y").date()
    today = date.today()
    age = today.year - born.year
    if (today.month, today.day) < (born.month, born.day):
        age -= 1
    return age


def policy_number():
    """Generate a policy number using a cryptographically secure RNG."""
    return "POL-" + str(secrets.randbelow(900000) + 100000)


def save_quote(name, premium):
    """Save a quote in memory and persist it to a local log file."""
    number = policy_number()
    quotes[number] = {"name": name, "premium": premium}
    with open(LOG_FILE, "a", encoding="utf-8") as file_obj:
        file_obj.write(f"{number},{name},{premium:.2f}\n")
    return number


def import_policies(xml_text):
    """Parse XML policy data using a secure XML parser."""
    root = DET.fromstring(xml_text)
    result = []
    for policy in root.findall("policy"):
        policy_type = policy.get("type")
        age = policy.get("age")
        total_sum = policy.get("sum")
        if policy_type is None or age is None or total_sum is None:
            continue
        try:
            result.append((policy_type, int(age), int(total_sum)))
        except ValueError:
            continue
    return result


def fetch_rates(url):
    """Download rate data using a verified HTTPS context when allowed."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS URLs are allowed.")

    context = ssl.create_default_context()
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(  # nosec B310
        request,
        context=context,
        timeout=10,
    ) as response:
        return response.read()


def import_claim_documents(archive_path):
    """Safely extract claim files from a tar archive."""
    target_dir = Path("claims_docs")
    target_dir.mkdir(exist_ok=True)
    with tarfile.open(archive_path, "r:*") as archive:
        archive.extractall(target_dir, filter="data")


def monthly_instalment(premium, months=12):
    """Return a monthly instalment amount."""
    if months == 0:
        return premium
    return math.floor(premium / months)


def is_authorised(token):
    """Validate whether a token matches the expected signing token."""
    return token == UNDERWRITER_TOKEN


def renewal_due(start, years=1):
    """Return the renewal date for a given start date and duration."""
    start_date = datetime.strptime(start, "%Y-%m-%d")
    future = start_date.replace(year=start_date.year + years)
    return future.strftime("%Y-%m-%d")


def print_quotes():
    """Print each stored quote with its index."""
    print("===== Quote Book =====")
    for index, key in enumerate(quotes, start=1):
        print(index, key, quotes[key]["name"], "Rs.", quotes[key]["premium"])


def main():
    """Execute the premium calculator demo for the lab."""
    p1 = calculate_premium("health", 30, 500000, False, 0)
    p2 = calculate_premium("health", 30, 500000, False, 0)
    p3 = calculate_premium("motor", 50, 800000, "no", 0)
    p4 = calculate_premium("life", 25, 100000, False, 0, [3000, 3000, 3000])

    print("Quote 1:", p1)
    print("Quote 2 (same customer details):", p2)
    print("Non-smoker aged 50:", p3)
    print("Life with stacked discounts:", p4)
    print("Age from DOB 31-12-1990:", age_from_dob("31-12-1990"))
    print("Monthly instalment:", monthly_instalment(p3))
    print("Renewal due:", renewal_due("2025-03-15"))
    xml = (
        "<policies><policy type='health' age='40' sum='300000'/>"
        "<policy type='motor' age='abc' sum='1'/></policies>"
    )
    print("Imported:", import_policies(xml))
    print("Saved as:", save_quote("Kiran", p1))
    print("Authorised:", is_authorised(UNDERWRITER_TOKEN))
    print("Server would listen on", HOST)
    print_quotes()


# pylint: disable=invalid-name
calculatePremium = calculate_premium
ageFromDob = age_from_dob
policyNumber = policy_number
saveQuote = save_quote
importPolicies = import_policies
fetchRates = fetch_rates
importClaimDocuments = import_claim_documents
monthlyInstalment = monthly_instalment
isAuthorised = is_authorised
renewalDue = renewal_due
printQuotes = print_quotes
# pylint: enable=invalid-name


if __name__ == "__main__":
    main()
