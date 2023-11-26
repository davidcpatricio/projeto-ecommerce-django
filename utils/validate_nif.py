def validate_nif(sent_nif):
    if not sent_nif or \
            len(sent_nif) != 9 or \
            sent_nif == sent_nif[0] * len(sent_nif):
        return False

    validationSets = {
      'one': ['1', '2', '3', '5', '6', '8'],
      'two': [
          '45', '70', '71', '72', '74', '75', '77', '78', '79',
          '90', '91', '98', '99'
        ]
    }
    if sent_nif[0] not in validationSets['one'] and \
            sent_nif[:2] not in validationSets['two']:
        return False

    first_eight_digits = sent_nif[:-1]
    reversed_counter = 9
    total = 0

    for digit in first_eight_digits:
        total += int(digit) * reversed_counter
        reversed_counter -= 1

    remainder = total % 11

    if remainder <= 1:
        control_digit = '0'
    else:
        control_digit = str(11 - remainder)

    if control_digit != sent_nif[-1]:
        return False

    new_nif = first_eight_digits + control_digit

    return new_nif == sent_nif
