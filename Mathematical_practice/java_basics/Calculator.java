import java.util.Scanner;

public class Calculator {
    double calculate(int a, int b, String operator) {
        switch (operator) {
            case "+":
                return a + b;
            case "-":
                return a - b;
            case "*":
                return a * b;
            case "/":
                if (b != 0) {
                    return (double) a / b;
                } else {
                    System.err.println("除零错误");
                    break;
                }
            default:
                System.out.println("运算符错误");
                break;
        }
        return 0;
    }
}

class CMain {
    public static void main(String[] args) {
        Calculator c = new Calculator();
        Scanner scanner = new Scanner(System.in);
        
        System.out.print("请输入整数1:");
        int a = scanner.nextInt();
        System.out.print("请输入整数2:");
        int b = scanner.nextInt();
        System.out.print("请输入运算符:");
        String operator = scanner.next();

        double ans = c.calculate(a, b, operator);
        System.out.printf("%d %s %d = %.2f\n", a, operator, b, ans);
        scanner.close();
    }
}