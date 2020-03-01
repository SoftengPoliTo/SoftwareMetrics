fn bubble_sort(values: &mut[i32]) {
    let mut n = values.len();
    let mut swapped = true;
 
    while swapped {
        swapped = false;
 
        for i in 1..n {
            if values[i - 1] > values[i] {
                values.swap(i - 1, i);
                swapped = true;
            }
        }
 
        n = n - 1;
    }
}
 
fn main() {
    let mut numbers = [4, 65, 2, -31, 0, 99, 2, 83, 782, 1];
    println!("Before: {:?}", numbers);
 
    bubble_sort(&mut numbers);
    println!("After: {:?}", numbers);
}
