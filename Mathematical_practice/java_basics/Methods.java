import java.util.Scanner;

public class Methods {
    void choice() {
        System.out.println("请选择功能：");
        System.out.println("1. 雇员信息录入");
        System.out.println("2. 雇员信息查看和编辑");
        System.out.println("3. 雇员信息查询");
        System.out.println("4. 雇员信息删除");
        System.out.println("5. 薪资管理");
        System.out.println("0. 退出程序");
        System.out.print("请选择：");
    }
    void handle(int option, Scanner scanner) {
        switch(option) {
            case 1:
                System.out.print("请输入员工姓名：");
                String name = scanner.nextLine();
                System.out.print("请输入员工职务：");
                String position = scanner.nextLine();
                System.out.print("请输入请假天数：");
                int leaveDays = scanner.nextInt();
                System.out.print("请输入基本工资：");
                double basicSalary = scanner.nextDouble();
                //此处完成创建对象，并把信息录入
                System.out.println("----已完成雇员信息录入-----");
                System.out.println("雇员信息录入成功");
                break;
            case 2:
                System.out.print("请输入要查看和编辑的雇员ID：");
                int employeeID = scanner.nextInt();
                //此处完成查看和编辑员工ID
                System.out.println("----已完成雇员信息查看和编辑录入-----");
            case 3:
                System.out.println("请选择查询方式：");
                //此处完成查询功能
                System.out.println("----已完成雇员信息的查询-----");
                break;
            case 4:
                System.out.print("请输入要删除的雇员ID：");
                int deleteEmployeeID = scanner.nextInt();
                //此处完成按雇员ID擅长雇员信息
                System.out.println("----已完成雇员信息删除-----");
                break;
            case 5:
                System.out.print("请输入要调整薪资的雇员ID：");
                //此处完成按雇员ID调整薪资
                System.out.println("----已完成雇员薪资管理-----");
                break;
            default:
                break;
        }
    }
    
}
class MMain {
    public static void main(String[] args) {
        Methods m = new Methods();
        Scanner scanner = new Scanner(System.in);
        int option = 0;

        do{
            m.choice();
            option = scanner.nextInt();
            scanner.nextLine();

            m.handle(option, scanner);
        } while (option != 0);

        scanner.close();
        System.out.println("程序已退出");
    }
}