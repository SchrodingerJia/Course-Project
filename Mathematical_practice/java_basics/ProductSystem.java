import java.util.*;

class Product {
    // 成员变量
    protected String name;
    protected double price;
    protected String description;

    // 构造方法
    public Product(String name, double price, String description) {
        this.name = name;
        this.price = price;
        this.description = description;
    }

    // 成员方法
    // 显示产品信息
    public void displayProduct() {
        System.out.printf("产品名称:%s\n产品价格:%.2f\n产品描述:%s\n", name, price, description);
    }
}

class Phone extends Product {
    // 构造方法
    public Phone(String name, double price, String description) {
        super(name, price, description);
    }
    
    // 成员方法
    public void call() {
        System.out.println("手机通话启动");
    }

    @Override
    public void displayProduct() {
        System.out.println("产品类型:手机");
        super.displayProduct();
    }
}

class Tablet extends Product {
    // 构造方法
    public Tablet(String name, double price, String description) {
        super(name, price, description);
    }
    
    // 成员方法
    public void touch() {
        System.out.println("平板触屏功能启动");
    }

    @Override
    public void displayProduct() {
        System.out.println("产品类型:平板");
        super.displayProduct();
    }
}

class Laptop extends Product {
    // 私有变量
    private double battery_capacity;
    
    // 构造方法
    public Laptop(String name, double price, String description, double battery_capacity) {
        super(name, price, description);
        this.battery_capacity = battery_capacity;
    }
    
    // 成员方法
    public void getbattery() {
        System.out.printf("电池容量:%.2f\n",battery_capacity);
    }

    @Override
    public void displayProduct() {
        System.out.println("产品类型:笔记本");
        getbattery();
        super.displayProduct();
    }
}

public class ProductSystem {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        List<Product> products = new ArrayList<>();
        String name;
        double price;
        String description;
        double battery_capacity;
        int choice = -1;
        while(true) {
            System.out.println("\n选择功能:");
            System.out.println("1. 查询产品信息");
            System.out.println("2. 创建手机产品");
            System.out.println("3. 创建平板产品");
            System.out.println("4. 创建笔记本产品");
            System.out.println("0. 退出系统");
            System.out.print("请选择: ");

            choice = scanner.nextInt();
            scanner.nextLine();

            switch (choice) {
                case 1:
                    if (products.isEmpty()) {
                        System.err.println("当前没有已创建的产品");
                    } else {
                        int index = 1;
                        for (Product product : products) {
                            System.out.println("\n产品 #" + index++);
                            product.displayProduct();
                        }
                    }
                    break;

                case 2:
                    System.out.print("请输入产品名称:");
                    name = scanner.nextLine();
                    System.out.print("请输入产品价格:");
                    price = scanner.nextDouble();
                    scanner.nextLine();
                    System.out.print("请输入产品描述:");
                    description = scanner.nextLine();

                    Phone phone = new Phone(name, price, description);
                    products.add(phone);
                    break;

                case 3:
                    System.out.print("请输入产品名称:");
                    name = scanner.nextLine();
                    System.out.print("请输入产品价格:");
                    price = scanner.nextDouble();
                    scanner.nextLine();
                    System.out.print("请输入产品描述:");
                    description = scanner.nextLine();

                    Tablet tablet = new Tablet(name, price, description);
                    products.add(tablet);
                    break;

                case 4:
                    System.out.print("请输入产品名称:");
                    name = scanner.nextLine();
                    System.out.print("请输入产品价格:");
                    price = scanner.nextDouble();
                    scanner.nextLine();
                    System.out.print("请输入产品描述:");
                    description = scanner.nextLine();
                    System.out.print("请输入电池容量:");
                    battery_capacity = scanner.nextDouble();
                    scanner.nextLine();

                    Laptop laptop = new Laptop(name, price, description, battery_capacity);
                    products.add(laptop);
                    break;

                case 0:
                    System.err.println("已成功退出系统");
                    scanner.close();
                    System.exit(0);

                default:
                    System.out.print("无效输入，请重新选择:");
                    break;
            }
        }
    }
}