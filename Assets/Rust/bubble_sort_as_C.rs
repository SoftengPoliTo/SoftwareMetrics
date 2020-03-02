fn bubble_sort(values: &mut[i32]) {
    let mut n = values.len();
    let mut swapped = true;

    while swapped {
        swapped = false;
        for i in 1..n {
            if values[i] < values[i - 1] {
                values.swap(i - 1, i);
                swapped = true;
            }
        }
        n -= 1;
    }
}

fn main() {
    let mut numbers = [4, 65, 2, -31, 0, 99, 2, 83, 782, 1];
    let n = numbers.len() ;
    print!("Before sorting:\n[");
    for i in 0..n {
        print!("{:?}", numbers[i]);
        if i < n - 1 {
            print!(", ");
        } else {
            print!("]\n");
        }
    }

    bubble_sort(&mut numbers);

    print!("After sorting:\n[");
    for i in 0..n {
        print!("{:?}", numbers[i]);
        if i < n - 1 {
            print!(", ");
        } else {
            print!("]\n");
        }
    }
}
