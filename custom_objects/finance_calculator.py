class FinanceCalculator:
    @staticmethod
    def treasury_to_decimal(price):
        """
        Converts a treasury priced in 32nds into a decimal. This works for
        treasurys priced up to 3dp i.e. "99-126"
        """
        price_split = price.split("-")
        integer_part = int(price_split[0])
        frac_part = price_split[1]

        frac_part_one = float(frac_part[0:2])
        frac_part_two = float(0)

        if len(frac_part) == 3:
            last_digit = frac_part[-1]
            if last_digit == "+":
                frac_part_two = float(4)
            else:
                frac_part_two = float(last_digit)
        elif len(frac_part) > 3:
            raise ValueError("4 decimal places are not supported")

        return integer_part + (frac_part_one + (frac_part_two / 8)) / 32

    # Convert decimal price to treasury in python
    @staticmethod
    def decimal_to_treasury(price):
        """
        Converts a treasury priced in 32nds into a decimal. This works for
        treasurys priced up to 2dp i.e. "99-12"
        """
        integral = int(price.partition(".")[0])
        price = float(price)
        decimal_part = str((price - integral) * 32)
        conversion = ""
        if ".5" in decimal_part:
            decimal_part = decimal_part.partition(".")[0]
            if float(decimal_part) < 10:
                conversion = f"{integral}-0{decimal_part}+"
            else:
                conversion = f"{integral}-{decimal_part}+"
        else:
            decimal_part = decimal_part.partition(".")[0]
            if float(decimal_part) < 10:
                conversion = f"{integral}-0{decimal_part}"
            else:
                conversion = f"{integral}-{decimal_part}"
        return conversion
