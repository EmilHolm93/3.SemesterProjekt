#include "InsertionSort.h"

/*
	Sekvensen for algoritmen
	1. Modtag jeton-værdi og append til vektor
	2. Modtag signal (start sortering)
	3. Send sorteret "pakke"
*/

int main()
{
	// signal fra RPi "start sortering". 

	std::vector<int> testVector;

	int chipValue; 

	while (true)
	{
		chipValue = scanJeton();

		if (chipValue == -1)
			break;

		testVector.push_back(chipValue);
	}

	insertionSorting(testVector);
	
	for (const auto& element: testVector)
	{
		std::cout << element << std::endl;
	}

	hashMapConvert(tempSort);

	return 0;
}