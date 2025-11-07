def ekub(a, b):
    if a == 0 or b == 0:
        return ValueError("0 soni uchun aniqlanmaydi!")

    if a < 0 or b < 0:
        return ValueError("Musbat sonlar kiritilishi kerak!")
    a_list = []
    b_list = []

    i = 2
    while i <= a:
        if a % i == 0:
            a_list.append(i)
            a //= i
        else:
            i += 1

    j = 2
    while j <= b:
        if b % j == 0:
            b_list.append(j)
            b //= j
        else:
            j += 1

    # ekub
    ekub = 1

    for prime in set(a_list):
        if prime in b_list:
            count = min(a_list.count(prime), b_list.count(prime))
            for _ in range(count):
                ekub *= prime
    return ekub


def ekuk(a,b):
    if a == 0 or b == 0:
        return ValueError("0 soni uchun aniqlanmaydi!")

    if a < 0 or b < 0:
        return ValueError("Musbat sonlar kiritilishi kerak!")
    
    saved_a = a
    saved_b = b
    a_list = []
    b_list = []

    i = 2
    while i <= a:
        if a % i == 0:
            a_list.append(i)
            a //= i
        else:
            i += 1

    j = 2
    while j <= b:
        if b % j == 0:
            b_list.append(j)
            b //= j
        else:
            j += 1
    
    ekuk = (saved_a * saved_b // ekub(a,b))

    return ekuk

def pow_number(a,n):
    if n < 0:
        return ValueError("n musbat son bo'lishi kerak!")
    result = 1
    for _ in range(n):
        result *= a
    return result
