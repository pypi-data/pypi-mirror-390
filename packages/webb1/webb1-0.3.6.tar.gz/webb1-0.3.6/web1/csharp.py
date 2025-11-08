def csharp():
    return """
💡 1️⃣ Program to Check if a Number is Even or Odd
using System;

class Program
{
    static void Main()
    {
        Console.Write("Enter a number: ");
        int num = Convert.ToInt32(Console.ReadLine());

        if(num % 2 == 0)
            Console.WriteLine("Even Number");
        else
            Console.WriteLine("Odd Number");
    }
}
Concept: % operator gives remainder; if 0 → even, else odd.
________________________________________
💡 2️⃣ User Login (3 Attempts)
using System;

class Program
{
    static void Main()
    {
        string user, pass;
        int attempt = 0;

        while(attempt < 3)
        {
            Console.Write("Enter User ID: ");
            user = Console.ReadLine();
            Console.Write("Enter Password: ");
            pass = Console.ReadLine();

            if(user == "admin" && pass == "1234")
            {
                Console.WriteLine("Login Successful!");
                break;
            }
            else
            {
                attempt++;
                Console.WriteLine("Invalid login! Attempt " + attempt);
            }
        }

        if(attempt == 3)
            Console.WriteLine("User Rejected!");
    }
}
Concept: Loop with condition; after 3 invalid attempts → rejected.
________________________________________
💡 3️⃣ Equation: x = y² + 2y + 1 (for y = -5 to 5)
using System;

class Program
{
    static void Main()
    {
        for(int y = -5; y <= 5; y++)
        {
            int x = (y * y) + (2 * y) + 1;
            Console.WriteLine($"y = {y} , x = {x}");
        }
    }
}
Concept: Loop from -5 to +5 → apply formula → print result.
________________________________________
💡 4️⃣ Both Numbers Even or Odd
using System;

class Program
{
    static void Main()
    {
        Console.Write("Enter first number: ");
        int a = Convert.ToInt32(Console.ReadLine());
        Console.Write("Enter second number: ");
        int b = Convert.ToInt32(Console.ReadLine());

        if(a % 2 == b % 2)
            Console.WriteLine("Both numbers are even or both odd → True");
        else
            Console.WriteLine("Different parity → False");
    }
}
________________________________________
💡 5️⃣ Largest of Three Numbers
using System;

class Program
{
    static void Main()
    {
        Console.Write("Enter three numbers: ");
        int a = Convert.ToInt32(Console.ReadLine());
        int b = Convert.ToInt32(Console.ReadLine());
        int c = Convert.ToInt32(Console.ReadLine());

        if(a > b && a > c)
            Console.WriteLine($"{a} is largest");
        else if(b > c)
            Console.WriteLine($"{b} is largest");
        else
            Console.WriteLine($"{c} is largest");
    }
}
________________________________________
💡 6️⃣ Check Quadrant of Point (x, y)
using System;

class Program
{
    static void Main()
    {
        Console.Write("Enter X coordinate: ");
        int x = Convert.ToInt32(Console.ReadLine());
        Console.Write("Enter Y coordinate: ");
        int y = Convert.ToInt32(Console.ReadLine());

        if(x > 0 && y > 0)
            Console.WriteLine("1st Quadrant");
        else if(x < 0 && y > 0)
            Console.WriteLine("2nd Quadrant");
        else if(x < 0 && y < 0)
            Console.WriteLine("3rd Quadrant");
        else if(x > 0 && y < 0)
            Console.WriteLine("4th Quadrant");
        else
            Console.WriteLine("Origin");
    }
}
________________________________________
💡 7️⃣ Eligibility for Admission
(Maths > 65, Physics > 55, Chemistry > 50 and total > 180)
using System;

class Program
{
    static void Main()
    {
        int math, phy, chem;
        Console.Write("Enter Maths marks: ");
        math = Convert.ToInt32(Console.ReadLine());
        Console.Write("Enter Physics marks: ");
        phy = Convert.ToInt32(Console.ReadLine());
        Console.Write("Enter Chemistry marks: ");
        chem = Convert.ToInt32(Console.ReadLine());

        int total = math + phy + chem;

        if(math > 65 && phy > 55 && chem > 50 && total > 180)
            Console.WriteLine("Eligible for admission");
        else
            Console.WriteLine("Not eligible");
    }
}________________________________________
💡 8️⃣ Program to Calculate Roots of a Quadratic Equation
Formula:
For equation ax² + bx + c = 0,
Roots are → (-b ± √(b² - 4ac)) / 2a
using System;

class Program
{
    static void Main()
    {
        double a = 1, b = -5, c = 6;
        double d = b * b - 4 * a * c;
        double root1, root2;

        if (d > 0)
        {
            root1 = (-b + Math.Sqrt(d)) / (2 * a);
            root2 = (-b - Math.Sqrt(d)) / (2 * a);
            Console.WriteLine($"Roots are real: {root1} , {root2}");
        }
        else if (d == 0)
        {
            root1 = -b / (2 * a);
            Console.WriteLine($"Equal Roots: {root1}");
        }
        else
            Console.WriteLine("Roots are imaginary");
    }
}
🧠 Concept:
Use Math.Sqrt() for square root; check discriminant d.
________________________________________
💡 9️⃣ Menu-Driven Program (Area of Shapes)
using System;

class Program
{
    static void Main()
    {
        int ch;
        double area;
        Console.WriteLine("1.Circle  2.Rectangle  3.Triangle");
        Console.Write("Enter your choice: ");
        ch = Convert.ToInt32(Console.ReadLine());

        switch(ch)
        {
            case 1:
                Console.Write("Enter radius: ");
                double r = Convert.ToDouble(Console.ReadLine());
                area = 3.14 * r * r;
                Console.WriteLine("Area of Circle = " + area);
                break;

            case 2:
                Console.Write("Enter length & breadth: ");
                double l = Convert.ToDouble(Console.ReadLine());
                double b = Convert.ToDouble(Console.ReadLine());
                area = l * b;
                Console.WriteLine("Area of Rectangle = " + area);
                break;

            case 3:
                Console.Write("Enter base & height: ");
                double ba = Convert.ToDouble(Console.ReadLine());
                double h = Convert.ToDouble(Console.ReadLine());
                area = 0.5 * ba * h;
                Console.WriteLine("Area of Triangle = " + area);
                break;
            default:
                Console.WriteLine("Invalid choice");
                break;
        }
    }
}
🧠 Concept:
Use switch for multiple choices; read user input with Console.ReadLine().
________________________________________
💡 🔟 Display n Terms of Odd Natural Numbers and Their Sum
using System;

class Program
{
    static void Main()
    {
        Console.Write("Enter number of terms: ");
        int n = Convert.ToInt32(Console.ReadLine());
        int sum = 0;
        int num = 1;

        for(int i=1; i<=n; i++)
        {
            Console.Write(num + " ");
            sum += num;
            num += 2;
        }
        Console.WriteLine("\nSum = " + sum);
    }
}
🧠 Concept:
Odd numbers = 1, 3, 5, 7, … (difference of 2).
________________________________________
💡 1️⃣1️⃣ Pattern 1
1
12
123
using System;

class Program
{
    static void Main()
    {
        for(int i=1; i<=3; i++)
        {
            for(int j=1; j<=i; j++)
                Console.Write(j);
            Console.WriteLine();
        }
    }
}
🧠 Concept:
Nested loops → inner loop controls numbers printed, outer controls lines.
________________________________________
💡 1️⃣2️⃣ Pattern 2
1
2 3
4 5 6
using System;

class Program
{
    static void Main()
    {
        int num = 1;
        for(int i=1; i<=3; i++)
        {
            for(int j=1; j<=i; j++)
            {
                Console.Write(num + " ");
                num++;
            }
            Console.WriteLine();
        }
    }
}
🧠 Concept:
Increment counter num inside nested loops.
________________________________________
💡 1️⃣3️⃣ Number Triangle with Width
using System;

class Program
{
    static void Main()
    {
        Console.Write("Enter number: ");
        int n = Convert.ToInt32(Console.ReadLine());
        Console.Write("Enter width: ");
        int w = Convert.ToInt32(Console.ReadLine());

        for(int i=1; i<=w; i++)
        {
            for(int j=1; j<=i; j++)
                Console.Write(n);
            Console.WriteLine();
        }
    }
}
________________________________________
💡 1️⃣4️⃣ Sum of Series [1 - X²/2! + X⁴/4! - ...]
using System;

class Program
{
    static void Main()
    {
        int x = 2;
        double sum = 1, term;
        int sign = -1;
        for (int i = 2; i <= 10; i += 2)
        {
            term = Math.Pow(x, i) / Factorial(i);
            sum += sign * term;
            sign *= -1;
        }
        Console.WriteLine("Sum = " + sum);
    }

    static double Factorial(int n)
    {
        double f = 1;
        for (int i = 1; i <= n; i++)
            f *= i;
        return f;
    }
}
🧠 Concept:
Alternate signs (+, -), power & factorial.
________________________________________
💡 1️⃣5️⃣ Sum of Series [9 + 99 + 999 + 9999 + ...]
using System;

class Program
{
    static void Main()
    {
        int n = 4;
        int term = 9;
        int sum = 0;

        for (int i = 1; i <= n; i++)
        {
            Console.Write(term + " ");
            sum += term;
            term = term * 10 + 9;
        }
        Console.WriteLine("\nSum = " + sum);
    }
}
🧠 Concept:
Each term formed by appending 9 at end.
________________________________________
💡 1️⃣6️⃣ Count Number of Spaces in a String
using System;

class Program
{
    static void Main()
    {
        Console.Write("Enter a string: ");
        string str = Console.ReadLine();
        int count = 0;

        foreach(char c in str)
        {
            if(c == ' ') count++;
        }
        Console.WriteLine("Number of spaces: " + count);
    }
}
________________________________________
💡 1️⃣7️⃣ Sum of Array Elements
using System;

class Program
{
    static void Main()
    {
        int[] arr = {1, 2, 3, 4, 5};
        int sum = 0;
        foreach(int x in arr)
            sum += x;
        Console.WriteLine("Sum = " + sum);
    }
}
________________________________________
💡 1️⃣8️⃣ Check if Number is Prime
using System;

class Program
{
    static void Main()
    {
        Console.Write("Enter number: ");
        int n = Convert.ToInt32(Console.ReadLine());
        bool isPrime = true;

        for(int i=2; i<=n/2; i++)
        {
            if(n % i == 0)
            {
                isPrime = false;
                break;
            }
        }

        if(isPrime) Console.WriteLine("Prime");
        else Console.WriteLine("Not Prime");
    }
}
________________________________________
💡 1️⃣9️⃣ Sum of Digits
using System;

class Program
{
    static void Main()
    {
        Console.Write("Enter number: ");
        int n = Convert.ToInt32(Console.ReadLine());
        int sum = 0;

        while(n > 0)
        {
            sum += n % 10;
            n /= 10;
        }
        Console.WriteLine("Sum of digits = " + sum);
    }
}
________________________________________
💡 2️⃣0️⃣ Recursive Fibonacci
using System;

class Program
{
    static int Fib(int n)
    {
        if (n <= 1)
            return n;
        else
            return Fib(n - 1) + Fib(n - 2);
    }

    static void Main()
    {
        Console.Write("Enter terms: ");
        int n = Convert.ToInt32(Console.ReadLine());
        for (int i = 0; i < n; i++)
            Console.Write(Fib(i) + " ");
    }
}

"""
