#include <algorithm>
#include <iostream>
#include <iterator>
 
template <typename RandomAccessIterator>
void bubble_sort(RandomAccessIterator begin, RandomAccessIterator end) {
  bool swapped = true;
  while (begin != end-- && swapped) {
    swapped = false;
    for (auto i = begin; i != end; ++i) {
      if (*(i + 1) < *i) {
        std::iter_swap(i, i + 1);
        swapped = true;
      }
    }
  }
}
 
int main() {
	int a[] = {4, 65, 2, -31, 0, 99, 2, 83, 782, 1};

	std::cout << "Before sorting:\n[";
  	copy(std::begin(a), std::end(a), std::ostream_iterator<int>(std::cout, " "));
  	std::cout << "]" << std::endl;

  	bubble_sort(std::begin(a), std::end(a));

  	std::cout << "After sorting:\n[";
  	copy(std::begin(a), std::end(a), std::ostream_iterator<int>(std::cout, " "));
  	std::cout << "]" << std::endl;  	
}
