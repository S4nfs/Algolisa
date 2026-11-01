// Rust is a modern programming language. Graydon Hoare created Rust in 2006 while working at Mozilla, which officially sponsored the project in 2009. 
// Dev-note: I almost lost comparing it with Golang, Zig , & C for more than 6 months along with procastinating other projects but eventually came up to decide to learn rust. What make this language special is that Rust is "safe by default" and that is the best thing which is making it fast so that you can build up low level stuff like kernels, drivers and even OS. It has a very steep learning curve and that eventually built up the curiosty to challenge myself up for this language. It has simple things harder and after 60% its eventually simple.

// Run the file using `cargo run` or `rustc 01_HelloWorld.rs && ./01_HelloWorld` because Rust is compiled language and needs to be compiled before running while cargo handles compilation and running in one command.


fn main(){


    //🦀 A Lovely Hello to the world of RUST =====================================
    print!("A Lovely, ");               // no next line with print!()
    println!("Hello World!");           // println!() is a macro, A macro is like a function, but with an exclamation mark (!) after it.
    
    
    //🦀 Variables let & const - Variable are immutable even with let also they are blocked scope like the let in Javascript
    let x: i32 = 5; 
    
    assert_eq!(x, 5);
    
    let mut x: i32 = 6;                 //mut keyword makes the variable mutable
    x = x+10;
    println!("{}", x);

    let result = 5;
    println!("The variables x and Y are equal to {}", result);

    {
        let x : i32 = 6;                // this x value is blocked scope 
        assert_eq!(x , 6);
    }
    
    const NAME: &str = "Sagar Verma";     //non-mutable, type is required
    println!("Name: {}", NAME);

    //🦀 Data Types ===============================================================
    let my_num: i32 = 7;                // integer
    let my_num2: u32 = 42;              // integer but u32 store between 0 - positive numbers only
    let my_double: f64 = 6.99;          // float
    let my_letter: char = 'S';          // character
    let my_bool: bool = true;           // boolean
    let my_text: &str = "4nfs";         // string
    
    println!(" Number is {}", my_num);
    println!(" Positive Number is {}", my_num2);
    println!(" Decimal is {}", my_double);
    println!(" Character is {}", my_letter);
    println!(" Boolean is {}", my_bool);
    println!(" Text is {}", my_text);
    
    let _unused_variable = 37;           //use _underscore to best declare unused variables



    let _cc: i32 = 58;
    let _cc = 84;
    println!("{}", _cc);



    //🦀 Operators 

    //🦀 Destructuring ========================================================
    // let (x, y);
    





    println!("Chapter End!");

}