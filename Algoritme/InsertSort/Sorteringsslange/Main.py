from Insertionsort import *;

def main():
    # Placeholder for "signal from RPi 'start sorting'".
    # Simulated as user input for now.

    test_vector = []

    while True:
        chip_value = scan_jeton()

        if chip_value == -1:
            break

        test_vector.append(chip_value)

    print("Sorting...")
    insertion_sort(test_vector)

    print("Sorted values:")
    for element in test_vector:
        print(element)

    hash_map_convert(test_vector)


if __name__ == "__main__":
    main()