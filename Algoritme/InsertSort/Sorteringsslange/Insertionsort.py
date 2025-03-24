from collections import Counter
from typing import List, TypeVar

T = TypeVar('T')

# Sorteringsvektorer
sorting_vector: List[T] = []
temp_sort: List[int] = []

# HashMap til tælling
hash_map = {
    1: 0,
    5: 0,
    10: 0,
    20: 0,
}

# Insertion sort-funktion
def insertion_sorting(sorting_vector: List[T]) -> None:
    global temp_sort  # Bruges til at gemme det sorterede resultat
    for position in range(1, len(sorting_vector)):
        temp = sorting_vector[position]

        j = position
        while j > 0 and temp < sorting_vector[j - 1]:
            sorting_vector[j] = sorting_vector[j - 1]
            j -= 1

        sorting_vector[j] = temp
    temp_sort = sorting_vector.copy()  # Gem resultatet i temp_sort
    for element in temp_sort:
        print(element)


# Konverter funktion til at opdatere hash_map
def hash_map_convert(map_list: List[int]) -> None:
    temp_map = hash_map.copy()

    for num in map_list:
        if num in temp_map:
            temp_map[num] += 1

    print("Printer map:")
    for key, value in temp_map.items():
        print(f"{key} {value}")

# Simuleret scanning af jetonværdi
def scan_jeton() -> int:
    try:
        value = int(input("Indtast chipValue (eller -1 for at stoppe): "))
        return value
    except ValueError:
        print("Ugyldig indtastning, prøv igen.")
        return scan_jeton()

