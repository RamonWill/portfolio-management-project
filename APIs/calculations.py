def Convertprice(user_input):
    """Converts a float value to 32nds or a 32nds to a float value"""

    try:
        if float(user_input)>0 and type(float(user_input)) == type(0.1):
            treausry_input = int(user_input.partition(".")[0])
            user_input = float(user_input)
            tick_display = str((user_input-treausry_input)*32)
            if ".5" in tick_display:
                tick_display = tick_display.partition(".")[0]
                if float(tick_display) < 10:
                    return "{}-0{}+".format(treausry_input,tick_display)
                else:
                    return "{}-{}+".format(treausry_input,tick_display)

            else:
                tick_display = tick_display.partition(".")[0]
                if float(tick_display) < 10:
                    return "{}-0{}".format(treausry_input,tick_display)
                else:
                    return "{}-{}".format(treausry_input,tick_display)


    except ValueError:
        pass

    try:
        if "-" in user_input:
            treausry_input = int(user_input.partition("-")[0])
            tick_display = user_input.partition("-")[2]
            if "+" in user_input:
                tick_display = float(tick_display.replace("+","")) + 0.5
                tick_display = tick_display/32
                converted_value = treausry_input + tick_display
                return round(converted_value,6)
            else:
                tick_display = float(tick_display)/32
                converted_value = treausry_input + tick_display
                return round(converted_value,6)
        else:
            pass
    except ValueError:
        pass
    except TypeError:
        pass
