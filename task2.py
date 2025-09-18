#!/usr/bin/env python3

BASE = 2 ** 15  # M = 2^15
MAX_DIGITS = 50  # N = 50


def create_bignum(value=0):
    digits = []
    sign = 1

    if isinstance(value, int):
        if value < 0:
            sign = -1
            value = abs(value)

        if value == 0:
            digits = [0]
        else:
            while value > 0 and len(digits) < MAX_DIGITS:
                digits.append(value % BASE)
                value //= BASE

    elif isinstance(value, list):
        digits = value[:MAX_DIGITS]
        digits = normalize(digits)
    else:
        raise TypeError("Значение должно быть целым числом")
    return (sign, digits)


def normalize(digits):
    while len(digits) > 1 and digits[-1] == 0:
        digits.pop()

    if not digits:
        return [0]

    return digits


def to_string(bignum):
    sign, digits = bignum
    result = 0
    i = 0
    for digit in digits:
        result += digit * (BASE ** i)
        i += 1
    if sign < 0:
        result = -result
    return str(result)


def add(a, b):
    if isinstance(a, int):
        a = create_bignum(a)
    if isinstance(b, int):
        b = create_bignum(b)

    a_sign, a_digits = a
    b_sign, b_digits = b
    if a_sign != b_sign:
        if a_sign < 0:
            return subtract(b, (1, a_digits))
        else:
            return subtract(a, (1, b_digits))
    result_digits = []
    carry = 0
    for i in range(max(len(a_digits), len(b_digits))):
        digit1 = a_digits[i] if i < len(a_digits) else 0
        digit2 = b_digits[i] if i < len(b_digits) else 0
        curr_sum = digit1 + digit2 + carry
        carry = curr_sum // BASE
        result_digits.append(curr_sum % BASE)
    if carry > 0 and len(result_digits) < MAX_DIGITS:
        result_digits.append(carry)
    return (a_sign, result_digits)


def abs_compare(a_digits, b_digits):
    if len(a_digits) != len(b_digits):
        return 1 if len(a_digits) > len(b_digits) else -1
    for i in range(len(a_digits) - 1, -1, -1):
        if a_digits[i] != b_digits[i]:
            return 1 if a_digits[i] > b_digits[i] else -1
    return 0


def subtract(a, b):
    if isinstance(a, int):
        a = create_bignum(a)
    if isinstance(b, int):
        b = create_bignum(b)

    a_sign, a_digits = a
    b_sign, b_digits = b

    if a_sign != b_sign:
        if a_sign < 0:
            result = add((1, a_digits), (1, b_digits))
            return (-a_sign, result[1])
        else:
            return add(a, (1, b_digits))

    cmp_result = abs_compare(a_digits, b_digits)
    if cmp_result < 0:
        return_sign = -a_sign
        a_digits, b_digits = b_digits, a_digits
    else:
        return_sign = a_sign
    result_digits = []
    borrow = 0
    for i in range(max(len(a_digits), len(b_digits))):
        digit1 = a_digits[i] if i < len(a_digits) else 0
        digit2 = b_digits[i] if i < len(b_digits) else 0

        diff = digit1 - digit2 - borrow
        if diff < 0:
            diff += BASE
            borrow = 1
        else:
            borrow = 0

        result_digits.append(diff)

    result_digits = normalize(result_digits)
    return (return_sign, result_digits)


def multiply(a, b):
    if isinstance(a, int):
        a = create_bignum(a)
    if isinstance(b, int):
        b = create_bignum(b)

    a_sign, a_digits = a
    b_sign, b_digits = b

    result_sign = a_sign * b_sign

    result = (1, [0])
    for i, digit2 in enumerate(b_digits):
        if i >= MAX_DIGITS:
            break

        carry = 0
        temp = []
        for j, digit1 in enumerate(a_digits):
            if i + j >= MAX_DIGITS:
                break

            prod = digit1 * digit2 + carry
            carry = prod // BASE
            temp.append(prod % BASE)
        if carry > 0 and i + len(a_digits) < MAX_DIGITS:
            temp.append(carry)

        temp = [0] * i + temp
        result = add(result, (1, temp))

    return (result_sign, normalize(result[1]))


def divide(a, b):
    precision = 20
    if isinstance(a, int):
        a = create_bignum(a)
    if isinstance(b, int):
        b = create_bignum(b)

    if is_zero(b):
        raise ZeroDivisionError("Делить на 0 нельзя")
    a_sign, a_digits = a
    b_sign, b_digits = b
    result_sign = a_sign * b_sign
    cmp = abs_compare(a_digits, b_digits)
    if cmp < 0:
        return (1, [0])
    norm_factor = BASE // (b_digits[-1] + 1)
    a_norm = multiply(a, (1, [norm_factor]))[1]
    b_norm = multiply(b, (1, [norm_factor]))[1]
    quotient_digits = []
    remainder = a_norm[:len(b_norm) - 1] or [0]
    for i in range(len(b_norm) - 1, len(a_norm)):
        remainder.append(a_norm[i])
        remainder = normalize(remainder)
        if len(remainder) < len(b_norm):
            q_digit = 0
        else:
            top = remainder[-1] * BASE + remainder[-2] if len(remainder) > 1 else remainder[-1]
            q_digit = min(top // b_norm[-1], BASE - 1)
            while True:
                product = multiply((1, b_norm), q_digit)[1]
                if abs_compare(product, remainder) <= 0:
                    break
                q_digit -= 1
        quotient_digits.append(q_digit)
        product = multiply((1, b_norm), q_digit)[1]
        remainder = subtract((1, remainder), (1, product))[1]
    return (result_sign, normalize(quotient_digits))


def is_zero(bignum):
    sign, digits = bignum
    return len(digits) == 1 and digits[0] == 0
    
def show_base_m(bignum):
    sign, digits = bignum
    if len(digits) == 1 and digits[0] == 0:
        return "0"
    result = "(" + ", ".join(str(d) for d in digits) + ")"
    if sign < 0:
        result = "-" + result
    return result


def get_valid_integer(prompt):
    """Get a valid integer from user input with error handling."""
    while True:
        try:
            value = input(prompt)
            return int(value)
        except ValueError:
            print("Ошибка! Пожалуйста, введите целое число.")


def interactive():
    print("=== Калькулятор больших чисел ===")
    print(f"База системы счисления (M) = 2^15 = {BASE}")
    print(f"Максимальное количество разрядов (N) = {MAX_DIGITS}")
    print()
    
    try:
        num1 = get_valid_integer("Введите первое число: ")
        
        num2 = get_valid_integer("Введите второе число: ")
        
        a = create_bignum(num1)
        b = create_bignum(num2)
        
        print(f"\nВведенные числа:")
        print(f"a = {to_string(a)} (десятичная система), a = {show_base_m(a)} (система с основанием М=2^15)")
        print(f"b = {to_string(b)} (десятичная система), b = {show_base_m(b)} (система с основанием М=2^15)")
        
        sum_result = add(a, b)
        print(f"\nСложение:")
        print(f"a + b = {to_string(sum_result)} (десятичная система)")
        print(f"a + b = {show_base_m(sum_result)} (система с основанием М=2^15)")
        
        diff_result = subtract(a, b)
        print(f"\nВычитание:")
        print(f"a - b = {to_string(diff_result)} (десятичная система)")
        print(f"a - b = {show_base_m(diff_result)} (система с основанием М=2^15)")
        
        prod_result = multiply(a, b)
        print(f"\nУмножение:")
        print(f"a * b = {to_string(prod_result)} (десятичная система)")
        print(f"a * b = {show_base_m(prod_result)} (система с основанием М=2^15)")
        
        try:
            quotient_result = divide(a, b)
            print(f"\nДеление:")
            print(f"a / b = {to_string(quotient_result)} (десятичная система)")
            print(f"a / b = {show_base_m(quotient_result)} (система с основанием М=2^15)")
        except ZeroDivisionError:
            print(f"\nДеление: Ошибка - деление на ноль невозможно")
        
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
    
    print("\nПрограмма завершена.")


if __name__ == "__main__":
    interactive()
