#pragma once

#include <iostream>
#include <vector>
#include <unordered_map>

template <typename T>
std::vector<T> sortingVector;

std::vector<int> tempSort;

std::unordered_map<int, int> hashMap{
	{1, 0},
	{2, 0},
	{5, 0},
	{10, 0},
	{25, 0},
};

template <typename T>
void insertionSorting(std::vector<T>& sortingVector)
{
	for (int position = 1; position < sortingVector.size(); position++) // Vi starter i index 1, element i index 0 vil ikke kunne sammenlignes med noget i starten
	{
		T temp = std::move(sortingVector[position]);

		int j;
		for (j = position; j > 0 && temp < sortingVector[j - 1]; j--)
		{
			sortingVector[j] = std::move(sortingVector[j - 1]);
		}

		sortingVector[j] = std::move(temp);
	}
	tempSort = sortingVector;
}

void hashMapConvert(std::vector<int> map)
{
	std::unordered_map<int, int> tempMap = hashMap;
	
	for (int i = 0; i < map.size(); i++)
	{
		for(auto &pair :tempMap)
		if (pair.first == map[i])
		{
			pair.second += 1;
		}
	}
	std::cout << "printer map: " << std::endl;
	for (const auto& pair : tempMap)
	{
		std::cout << pair.first << " " << pair.second << std::endl;
	}
}

// Denne metode er lavet for modul test. 
int scanJeton() 
{
	int value;
	std::cout << "Indtast chipValue (eller -1 for at stoppe): ";
	std::cin >> value; // dette skal simulere dataet, som sendes fra scanning processen
	return value;
}