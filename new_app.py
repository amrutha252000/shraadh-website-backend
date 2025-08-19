# This script requires the 'pancanga' library.
# You can install it by running: pip install pancanga

from pancanga import anka, calendar, masa, paksa, tithi
from datetime import date

def find_lunar_date_in_current_year(input_year, input_month, input_day):
    """
    Converts a Gregorian date to its Indian lunar calendar equivalent,
    finds that lunar date in the current year, and converts it back
    to a Gregorian date.

    Args:
        input_year (int): The year of the original date.
        input_month (int): The month of the original date.
        input_day (int): The day of the original date.

    Returns:
        A tuple containing:
        - The original Gregorian date as a string.
        - The corresponding Indian lunar date as a string.
        - The Gregorian date of the equivalent lunar date in the current year as a string.
        Returns (None, None, None) if the date is invalid.
    """
    try:
        # Create a Gregorian date object for the input date
        original_gregorian_date = calendar.GregorianDate(year=input_year, month=input_month, day=input_day)

        # Convert the Gregorian date to the Indian lunar calendar date
        original_indian_date = calendar.IndianDate.from_gregorian(original_gregorian_date)

        # Get the current year
        current_year = date.today().year

        # Get the components of the lunar date
        lunar_month = original_indian_date.masa
        lunar_paksha = original_indian_date.paksa
        lunar_tithi = original_indian_date.tithi

        # Create the same lunar date for the current year
        # Note: Some lunar dates might not occur every year.
        # The library will find the next occurrence if it's not in the current year.
        current_year_indian_date = calendar.IndianDate(
            year=current_year,
            masa=lunar_month,
            paksa=lunar_paksha,
            tithi=lunar_tithi
        )

        # Convert the new Indian lunar date back to a Gregorian date
        current_year_gregorian_date = current_year_indian_date.to_gregorian()

        # Format the dates for display
        original_gregorian_str = original_gregorian_date.strftime('%Y-%m-%d')
        original_indian_str = f"{lunar_tithi.name.capitalize()} tithi, {lunar_paksha.name.capitalize()} paksha, {lunar_month.name.capitalize()} masa"
        current_year_gregorian_str = current_year_gregorian_date.strftime('%Y-%m-%d')

        return original_gregorian_str, original_indian_str, current_year_gregorian_str

    except (ValueError, calendar.DateError) as e:
        print(f"Error: {e}. Please enter a valid date.")
        return None, None, None

if __name__ == "__main__":
    print("--- Indian Lunar Calendar Date Converter ---")
    print("Given a date, this script finds the corresponding lunar date in the current year.")

    try:
        # Get user input for the date
        year_input = int(input("Enter the year (e.g., 1995): "))
        month_input = int(input("Enter the month (1-12): "))
        day_input = int(input("Enter the day (1-31): "))

        print("\nCalculating...")

        # Perform the conversion
        original_date, lunar_date, new_date = find_lunar_date_in_current_year(year_input, month_input, day_input)

        if original_date:
            print("\n--- Results ---")
            print(f"Original Gregorian Date: {original_date}")
            print(f"Corresponding Lunar Date:  {lunar_date}")
            print(f"This lunar date occurs on the following Gregorian date this year: {new_date}")
            print("-----------------")

    except ValueError:
        print("\nInvalid input. Please enter numbers for the date components.")
