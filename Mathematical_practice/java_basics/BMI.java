import java.util.Scanner;

public class BMI {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // 输入
        System.out.print("请输入身高(单位:米):");
        double height = scanner.nextDouble();
        System.out.print("请输入体重(单位：千克):");
        double weight = scanner.nextDouble();
        
        // BMI
        double bmi = weight / (height * height);

        // 输出
        System.out.printf("BMI = %.2f", bmi);

        scanner.close();
    }
}