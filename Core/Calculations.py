def Decimal_to_treasury(price):
    """Converts a float price to 32nds price."""
    if float(price) > 0:
        integral = int(price.partition(".")[0])
        price = float(price)
        decimal_part = str((price-integral)*32)
        if ".5" in decimal_part:
            decimal_part = decimal_part.partition(".")[0]
            if float(decimal_part) < 10:
                return "{}-0{}+".format(integral, decimal_part)
            else:
                return "{}-{}+".format(integral, decimal_part)

        else:
            decimal_part = decimal_part.partition(".")[0]
            if float(decimal_part) < 10:
                return "{}-0{}".format(integral, decimal_part)
            else:
                return "{}-{}".format(integral, decimal_part)


def Treasury_to_decimal(price):
    """Converts a 32nds price to a decimal price."""

    integral = int(price.partition("-")[0])
    decimal_part = price.partition("-")[2]
    if "+" in price:
        decimal_part = float(decimal_part.replace("+", "")) + 0.5
        decimal_part = decimal_part/32
        converted_value = integral + decimal_part
        return round(converted_value, 6)
    else:
        decimal_part = float(decimal_part)/32
        converted_value = integral + decimal_part
        return round(converted_value, 6)


def Convertprice(user_input):
    """Converts the price based on the user_input"""

    try:
        return Decimal_to_treasury(user_input)
    except ValueError:
        pass
    try:
        return Treasury_to_decimal(user_input)
    except ValueError:
        return "Value Error.\nExamples 108.50 or 108-16"
