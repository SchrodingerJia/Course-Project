import java.util.Scanner;

public class Temperature {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // 输入
        System.out.print("请输入华氏温度:");
        double F = scanner.nextDouble();

        double C = (F - 32) * 5 / 9;

        // 输出
        System.out.printf("摄氏温度为:%.2f摄氏度", C);

        scanner.close();
    }
}