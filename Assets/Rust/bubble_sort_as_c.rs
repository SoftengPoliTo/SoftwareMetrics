// bubble_sort_function
fn bubble_sort(a: &mut [isize; 10], n: usize) {
    let mut t: isize;
    let mut j: usize = n;
    let mut s: usize = 1;

    while s > 0 {
        s = 0;
        let mut i: usize = 1;

        while i < j {
            if a[i] < a[i - 1] {
                t = a[i];
                a[i] = a[i - 1];
                a[i - 1] = t;
                s = 1;
            }
            i += 1;
        }
        j -= 1;
    }
}

fn main() {
    let mut numbers: [isize; 10] = [4, 65, 2, -31, 0, 99, 2, 83, 782, 1];
    let n: usize = 10;
    let mut i: usize = 0;

    print!("Before sorting:\n\n");
    while i < n {
        print!("{} ", numbers[i]);
        i += 1;
    }

    bubble_sort(&mut numbers, n);

    print!("\n\nAfter sorting:\n\n");
    i = 0;
    while i < n {
        print!("{} ", numbers[i]);
        i += 1;
    }
}
