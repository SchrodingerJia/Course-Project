import java.io.*;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.stream.Collectors;
// 用户类（基类）
abstract class User {
    // 成员变量:名称,密码,用户类型,手机号
    protected String username;
    protected String password;
    protected String userType; // "student" , "merchant" 或 "admin"
    protected String phone;
    // 构造方法
    public User(String username, String password, String userType, String phone) {
        this.username = username;
        this.password = password;
        this.userType = userType;
        this.phone = phone;
    }
    // 成员方法
    // 身份认证
    public boolean authenticate(String password) {
        return this.password.equals(password);
    }
    // 获取用户名
    public String getUsername() {
        return username;
    }
    // 获取用户密码
    public String getPassword() {
        return password;
    }
    // 获取用户类型
    public String getUserType() {
        return userType;
    }
    // 获取用户电话
    public String getPhone() {
        return phone;
    }
    // 将用户数据转换为CSV格式
    public String toCSV() {
        return username + "," + password + "," + userType + "," + phone;
    }
}
// 学生类
class Student extends User {
    // 私有变量:订单列表
    private List<Order> orders;
    // 构造方法
    public Student(String username, String password, String phone) {
        super(username, password, "student", phone);
        this.orders = new ArrayList<>();
    }
    // 成员方法
    // 点单
    public void placeOrder(Order order) {
        orders.add(order);
    }
    //取消订单
    public void cancelOrder(Order order) {
        if (orders.contains(order) && order.getStatus().equals("待处理")) {
            orders.remove(order);
            order.cancel();
            System.out.println("订单已取消");
        } else {
            System.out.println("无法取消订单，订单状态为: " + order.getStatus());
        }
    }
    // 获取订单
    public List<Order> getOrders() {
        return orders;
    }
}
// 商家类
class Merchant extends User {
    // 私有变量:菜单列表
    private List<Dish> menu;
    // 构造方法
    public Merchant(String username, String password, String phone) {
        super(username, password, "merchant", phone);
        this.menu = new ArrayList<>();
    }
    // 成员方法
    // 添加菜品
    public void addDish(Dish dish) {
        menu.add(dish);
    }
    // 移除菜品
    public void removeDish(String dishName) {
        menu.removeIf(dish -> dish.getName().equals(dishName));
    }
    // 更新菜品
    public void updateDish(String dishName, double newPrice, int newStock) {
        for (Dish dish : menu) {
            if (dish.getName().equals(dishName)) {
                dish.setPrice(newPrice);
                dish.setStock(newStock);
                dish.setWarning(0);
                return;
            }
        }
        System.out.println("未找到菜品: " + dishName);
    }
    // 获取菜单
    public List<Dish> getMenu() {
        return menu;
    }
    // 展示菜单
    public void displayMenu() {
        System.out.println("\n===== " + username + " 的菜单 =====");
        if (menu.isEmpty()) {
            System.out.println("暂无菜品");
        } else {
            for (int i = 0; i < menu.size(); i++) {
                System.out.printf("%d. %s - ￥%.2f (库存: %d)\n",
                                 i + 1, menu.get(i).getName(),
                                 menu.get(i).getPrice(), menu.get(i).getStock());
            }
        }
        System.out.println("=============================");
    }
}
// 管理员类
class Admin extends User {
    public Admin(String username, String password, String phone) {
        super(username, password, "admin", phone);
    }
}
// 菜品类
class Dish {
    // 成员变量:名称,价格,库存,预警
    private String name;
    private double price;
    private int stock;
    private int warning;
    // 构造方法
    public Dish(String name, double price, int stock, int warning) {
        this.name = name;
        this.price = price;
        this.stock = stock;
        this.warning = warning;
    }
    // 成员方法
    // 获取名称
    public String getName() {
        return name;
    }
    // 获取价格
    public double getPrice() {
        return price;
    }
    // 获取库存
    public int getStock() {
        return stock;
    }
    // 获取警告
    public int getWarning() {
        return warning;
    }
    // 设置价格
    public void setPrice(double price) {
        this.price = price;
    }
    // 设置库存
    public void setStock(int stock) {
        this.stock = stock;
    }
    // 设置警告
    public void setWarning(int warning) {
        this.warning = warning;
    }
    // 减少库存
    public void reduceStock(int quantity) {
        if (stock >= quantity) {
            stock -= quantity;
        } else {
            System.err.println("SystemError:NotEnoughStock");
            // 错误处理
        }
    }
    // 增加库存
    public void increaseStock(int quantity) {
        stock += quantity;
    }
    // 将菜品数据转换为CSV格式
    public String toCSV() {
        return name + "," + price + "," + stock + "," + warning;
    }
}
// 订单类
class Order {
    // 下一订单号,用于管理订单号
    private static int nextId = 1;
    // 静态方法更新nextId
    public static void updateNextId(int id) {
        if (id >= nextId) {
            nextId = id + 1;
        }
    }
    // 成员变量:ID,点单学生,供应商家,菜品及其数量,总价,订单状态,点单时间
    int id;
    Student student;
    Merchant merchant;
    Map<Dish, Integer> items;
    double totalAmount;
    String status; // "待处理", "已完成", "已取消"
    Date orderTime;
    // 成员方法
    // 创建订单
    public Order(Student student, Merchant merchant) {
        this.id = nextId++;
        this.student = student;
        this.merchant = merchant;
        this.items = new HashMap<>();
        this.totalAmount = 0.0;
        this.status = "待处理";
        this.orderTime = new Date();
    }
    // 向订单添加菜品
    public void addItem(Dish dish, int quantity) {
        if (dish.getStock() >= quantity) {
            items.put(dish, items.getOrDefault(dish, 0) + quantity);
            totalAmount += dish.getPrice() * quantity;
            dish.reduceStock(quantity);
        } else {
            System.out.println("库存不足，无法添加: " + dish.getName());
        }
    }
    // 从订单移除菜品
    public void removeItem(Dish dish) {
        if (items.containsKey(dish)) {
            totalAmount -= dish.getPrice() * items.get(dish);
            dish.increaseStock(items.get(dish));
            items.remove(dish);
        }
    }
    // 取消订单
    public void cancel() {
        status = "已取消";
        // 恢复库存
        for (Map.Entry<Dish, Integer> entry : items.entrySet()) {
            entry.getKey().increaseStock(entry.getValue());
        }
    }
    // 完成订单
    public void complete() {
        status = "已完成";
    }
    // 获取订单号
    public int getId() {
        return id;
    }
    // 获取点单学生
    public Student getStudent() {
        return student;
    }
    // 获取供应商家
    public Merchant getMerchant() {
        return merchant;
    }
    // 获取总价
    public double getTotalAmount() {
        return totalAmount;
    }
    // 获取状态
    public String getStatus() {
        return status;
    }
    // 获取点单时间
    public Date getOrderTime() {
        return orderTime;
    }
    // 获取订单菜品
    public Map<Dish, Integer> getItems() {
        return items;
    }
    // 获取订单信息
    public void displayOrder() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        System.out.println("\n===== 订单详情 =====");
        System.out.println("订单号: #" + id);
        System.out.println("学生: " + student.getUsername());
        System.out.println("商家: " + merchant.getUsername());
        System.out.println("下单时间: " + sdf.format(orderTime));
        System.out.println("状态: " + status);
        System.out.println("订单内容:");
        for (Map.Entry<Dish, Integer> entry : items.entrySet()) {
            System.out.printf("- %s x %d: ￥%.2f\n",
                             entry.getKey().getName(),
                             entry.getValue(),
                             entry.getKey().getPrice() * entry.getValue());
        }
        System.out.printf("总金额: ￥%.2f\n", totalAmount);
        System.out.println("====================");
    }
    // 将订单数据转换为CSV格式
    public String toCSV() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        StringBuilder itemsStr = new StringBuilder();
        for (Map.Entry<Dish, Integer> entry : items.entrySet()) {
            itemsStr.append(entry.getKey().getName())
                   .append(":")
                   .append(entry.getValue())
                   .append(";");
        }
        return id + "," +
               student.getUsername() + "," +
               merchant.getUsername() + "," +
               sdf.format(orderTime) + "," +
               status + "," +
               totalAmount + "," +
               itemsStr.toString();
    }
}
// CSV文件管理工具类
class CSVFileManager {
    private static final String USERS_FILE = "users.csv";
    private static final String DISHES_FILE = "dishes.csv";
    private static final String ORDERS_FILE = "orders.csv";
    private static final String MESSEGES_FILE = "messeges.csv";
    // 用户管理
    // 保存用户数据到CSV
    public static void saveUsers(List<User> users) {
        try (PrintWriter writer = new PrintWriter(new FileWriter(USERS_FILE))) {
            writer.println("username,password,userType,phone");
            for (User user : users) {
                writer.println(user.toCSV());
            }
        } catch (IOException e) {
            System.out.println("保存用户数据失败: " + e.getMessage());
        }
    }
    // 从CSV加载用户数据
    public static List<User> loadUsers() {
        List<User> users = new ArrayList<>();
        File file = new File(USERS_FILE);
        if (!file.exists()) {
            // 如果文件不存在，创建初始样本数据
            createSampleUsers(users);
            saveUsers(users);
            return users;
        }
        try (BufferedReader reader = new BufferedReader(new FileReader(USERS_FILE))) {
            // 跳过标题行
            String line = reader.readLine();
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length == 4) {
                    String username = parts[0];
                    String password = parts[1];
                    String userType = parts[2];
                    String phone = parts[3];
                    if (userType.equals("student")) {
                        users.add(new Student(username, password, phone));
                    } else if (userType.equals("merchant")) {
                        users.add(new Merchant(username, password, phone));
                    } else if (userType.equals("admin")) {
                        users.add(new Admin(username, password, phone));
                    }
                }
            }
        } catch (IOException e) {
            System.out.println("加载用户数据失败: " + e.getMessage());
        }
        return users;
    }
    // 创建初始样本用户
    private static void createSampleUsers(List<User> users) {
        // 添加管理员
        users.add(new Admin("admin", "admin123", "12332112345"));
        // 添加商家
        users.add(new Merchant("SampleMerchant", "password","13443113456"));
        users.add(new Merchant("示例商户", "password","12442112456"));
        // 添加学生
        users.add(new Student("SampleStudent", "password", "13553113567"));
        users.add(new Student("示例学生", "password","12552112567"));
    }
    // 保存菜品数据到CSV
    public static void saveDishes(List<Merchant> merchants) {
        try (PrintWriter writer = new PrintWriter(new FileWriter(DISHES_FILE))) {
            writer.println("merchant,dishName,price,stock,warning");
            for (Merchant merchant : merchants) {
                for (Dish dish : merchant.getMenu()) {
                    writer.println(merchant.getUsername() + "," + dish.toCSV());
                }
            }
        } catch (IOException e) {
            System.out.println("保存菜品数据失败: " + e.getMessage());
        }
    }
    // 从CSV加载菜品数据
    public static void loadDishes(List<Merchant> merchants) {
        File file = new File(DISHES_FILE);
        if (!file.exists()) {
            // 如果文件不存在，创建初始样本菜品
            createSampleDishes(merchants);
            saveDishes(merchants);
            return;
        }
        try (BufferedReader reader = new BufferedReader(new FileReader(DISHES_FILE))) {
            // 跳过标题行
            String line = reader.readLine();
            Map<String, Merchant> merchantMap = new HashMap<>();
            for (Merchant m : merchants) {
                merchantMap.put(m.getUsername(), m);
            }
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length == 5) {
                    String merchantName = parts[0];
                    String dishName = parts[1];
                    double price = Double.parseDouble(parts[2]);
                    int stock = Integer.parseInt(parts[3]);
                    int warning = Integer.parseInt(parts[4]);
                    Merchant merchant = merchantMap.get(merchantName);
                    if (merchant != null) {
                        merchant.addDish(new Dish(dishName, price, stock, warning));
                    }
                }
            }
        } catch (IOException | NumberFormatException e) {
            System.out.println("加载菜品数据失败: " + e.getMessage());
        }
    }
    // 创建初始样本菜品
    private static void createSampleDishes(List<Merchant> merchants) {
        for (Merchant merchant : merchants) {
            if (merchant.getUsername().equals("SampleMerchant")) {
                merchant.addDish(new Dish("Dish1", 18.0, 50, 0));
                merchant.addDish(new Dish("Dish2", 20.0, 40, 0));
                merchant.addDish(new Dish("Dish3", 15.0, 60, 0));
            } else if (merchant.getUsername().equals("示例商户")) {
                merchant.addDish(new Dish("示例菜品1", 30.0, 30, 0));
                merchant.addDish(new Dish("示例菜品2", 25.0, 40, 0));
                merchant.addDish(new Dish("示例菜品3", 15.0, 50, 0));
            }
        }
    }
    // 从CSV加载订单数据
    public static List<Order> loadOrders(List<Student> students, List<Merchant> merchants) {
        List<Order> orders = new ArrayList<>();
        File file = new File(ORDERS_FILE);
        if (!file.exists()) {
            saveOrders(orders);
            return orders;
        }
        try (BufferedReader reader = new BufferedReader(new FileReader(ORDERS_FILE))) {
            // 跳过标题行
            String line = reader.readLine();
            Map<String, Student> studentMap = students.stream()
                .collect(Collectors.toMap(Student::getUsername, s -> s));
            Map<String, Merchant> merchantMap = merchants.stream()
                .collect(Collectors.toMap(Merchant::getUsername, m -> m));
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
            int maxId = 0; // 用于记录最大ID
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length < 7) {
                    System.out.println("无效订单行: " + line);
                    continue;
                }
                try {
                    int id = Integer.parseInt(parts[0]);
                    // 更新最大ID
                    if (id > maxId) maxId = id;
                    String studentName = parts[1];
                    String merchantName = parts[2];
                    Date orderTime = sdf.parse(parts[3]);
                    String status = parts[4];
                    double totalAmount = Double.parseDouble(parts[5]);
                    String itemsStr = parts[6];
                    Student student = studentMap.get(studentName);
                    Merchant merchant = merchantMap.get(merchantName);
                    if (student == null || merchant == null) {
                        System.out.println("无法找到学生或商家: " + studentName + "/" + merchantName);
                        continue;
                    }
                    // 创建订单对象
                    Order order = new Order(student, merchant);
                    // 手动设置ID
                    order.id = id;
                    order.orderTime = orderTime;
                    order.status = status;
                    order.totalAmount = totalAmount;
                    // 解析菜品项
                    String[] itemPairs = itemsStr.split(";");
                    for (String itemPair : itemPairs) {
                        if (itemPair.isEmpty()) continue;
                        String[] itemParts;
                        if (itemPair.indexOf("x") == -1){
                            itemParts = itemPair.split(":");
                            if (itemParts.length != 2) continue;
                        } else {
                            itemParts = itemPair.split("x");
                            if (itemParts.length != 2) continue;
                            itemParts[0] = itemParts[0].substring(0, itemParts[0].length() - 1);
                            itemParts[1] = itemParts[1].substring(0, itemParts[1].length() - 1);
                        }
                        String dishName = itemParts[0];
                        int quantity = Integer.parseInt(itemParts[1]);
                        // 在商家菜单中查找菜品
                        Optional<Dish> dishOpt = merchant.getMenu().stream()
                            .filter(d -> d.getName().equals(dishName))
                            .findFirst();
                        if (dishOpt.isPresent()) {
                            Dish dish = dishOpt.get();
                            order.items.put(dish, quantity);
                        }
                    }
                    student.placeOrder(order);
                    orders.add(order);
                } catch (Exception e) {
                    System.out.println("解析订单失败: " + line + " - " + e.getMessage());
                }
            }
            // 更新全局nextId
            Order.updateNextId(maxId);
        } catch (IOException e) {
            System.out.println("加载订单数据失败: " + e.getMessage());
        }
        return orders;
    }
    // 保存订单数据到CSV
    public static void saveOrders(List<Order> orders) {
        try (PrintWriter writer = new PrintWriter(new FileWriter(ORDERS_FILE))) {
            writer.println("id,student,merchant,orderTime,status,totalAmount,items");
            for (Order order : orders) {
                writer.println(order.toCSV());
            }
        } catch (IOException e) {
            System.out.println("保存订单数据失败: " + e.getMessage());
        }
    }
    // 保存消息数据到CSV
    public static void saveMesseges(List<Order> orders) {
        try (PrintWriter writer = new PrintWriter(new FileWriter(MESSEGES_FILE))) {
            writer.println("id,student,merchant,orderTime,status,totalAmount,items");
            for (Order order : orders) {
                writer.println(order.toCSV());
            }
        } catch (IOException e) {
            System.out.println("保存消息数据失败: " + e.getMessage());
        }
    }
    // 生成订单记录CSV
    public static void generateOrderReport(List<Order> orders) {
        try (PrintWriter writer = new PrintWriter(new File("订单记录.csv"))) {
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
            // 写入CSV头部
            writer.println("订单号,学生,商家,下单时间,状态,总金额,菜品详情");
            // 写入订单数据
            for (Order order : orders) {
                StringBuilder items = new StringBuilder();
                for (Map.Entry<Dish, Integer> entry : order.getItems().entrySet()) {
                    items.append(entry.getKey().getName())
                         .append("(x")
                         .append(entry.getValue())
                         .append(");");
                }
                writer.println(
                    order.getId() + "," +
                    order.getStudent().getUsername() + "," +
                    order.getMerchant().getUsername() + "," +
                    sdf.format(order.getOrderTime()) + "," +
                    order.getStatus() + "," +
                    order.getTotalAmount() + "," +
                    "\"" + items.toString() + "\""
                );
            }
            System.out.println("订单记录已导出到: 订单记录.csv");
        } catch (FileNotFoundException e) {
            System.out.println("导出订单记录失败: " + e.getMessage());
        }
    }
}
// 订餐系统主类
class CampusFoodOrderingSystem {
    // 成员变量:用户,商家,学生,订单,消息,当前用户,输入源
    private List<User> users;
    private List<Merchant> merchants;
    private List<Student> students;
    private List<Order> allOrders;
    private List<Order> newOrders;
    private User currentUser;
    private Scanner scanner;
    // 构造方法
    public CampusFoodOrderingSystem() {
        scanner = new Scanner(System.in);
        // 从CSV加载用户数据
        users = CSVFileManager.loadUsers();
        // 分离学生和商家
        merchants = new ArrayList<>();
        students = new ArrayList<>();
        for (User user : users) {
            if (user instanceof Merchant) {
                merchants.add((Merchant) user);
            } else if (user instanceof Student) {
                students.add((Student) user);
            }
        }
        // 从CSV加载菜品数据
        CSVFileManager.loadDishes(merchants);
        newOrders = new ArrayList<>();
        // 从CSV加载订单数据
        allOrders = CSVFileManager.loadOrders(students, merchants);
    }
    // 成员方法
    // 启动
    public void start() {
        // 添加关闭Hook，确保程序退出时保存数据
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            saveAllData();
            System.out.println("所有数据已保存到CSV文件");
        }));
        while (true) {
            if (currentUser == null) {
                showMainMenu();
            } else if (currentUser.getUserType().equals("student")) {
                showStudentMenu();
            } else if (currentUser.getUserType().equals("merchant")) {
                try {
                    showMerchantMenu();
                } catch (Exception e) {
                    System.err.println(e);
                }
            } else if (currentUser.getUserType().equals("admin")) {
                showAdminMenu();
            }
        }
    }
    // 保存所有数据到CSV文件
    private void saveAllData() {
        System.out.println("正在保存数据到CSV文件...");
        CSVFileManager.saveUsers(users);
        CSVFileManager.saveDishes(merchants);
        CSVFileManager.saveOrders(allOrders);
        CSVFileManager.saveMesseges(newOrders);
        CSVFileManager.generateOrderReport(allOrders);
    }
    // 展示系统功能
    private void showMainMenu() {
        System.out.println("\n===== 校园餐厅订餐系统 =====");
        System.out.println("1. 学生登录");
        System.out.println("2. 商家登录");
        System.out.println("3. 学生注册");
        System.out.println("4. 商家注册");
        System.out.println("0. 退出系统");
        // -1. 管理员登录
        System.out.print("请选择: ");
        int choice = scanner.nextInt();
        scanner.nextLine(); // 清除换行符
        switch (choice) {
            case -1:
                login("admin");
                break;
            case 1:
                login("student");
                break;
            case 2:
                login("merchant");
                break;
            case 3:
                register("student");
                break;
            case 4:
                register("merchant");
                break;
            case 0:
                System.out.println("感谢使用校园餐厅订餐系统，再见！");
                System.exit(0);
            default:
                System.out.println("无效选择，请重新输入");
        }
    }
    // 查询用户
    private User findUser(String username) {
        for (User user : users) {
            if (user.getUsername().equals(username)) {
                return user;
            }
        }
        return null;
    }
    // 用户登录
    private void login(String userType) {
        System.out.print("请输入用户名: ");
        String username = scanner.nextLine();
        System.out.print("请输入密码: ");
        String password = scanner.nextLine();
        User user = findUser(username);
        if (user != null && user.getUserType().equals(userType)) {
            if (user.authenticate(password)) {
                currentUser = user;
                System.out.println("\n登录成功！欢迎, " + username);
            } else {
                System.out.println("密码错误");
            }
        } else {
            System.out.println("用户不存在或用户类型不匹配");
        }
    }
    // 用户注册
    private void register(String userType) {
        System.out.print("请输入用户名: ");
        String username = scanner.nextLine();
        if (findUser(username) != null) {
            System.out.println("用户名已存在");
            return;
        }
        System.out.print("请输入密码: ");
        String password = scanner.nextLine();
        System.out.print("请输入手机号: ");
        String phone = scanner.nextLine();
        User newUser;
        if (userType.equals("student")) {
            newUser = new Student(username, password, phone);
            students.add((Student) newUser);
        } else {
            newUser = new Merchant(username, password, phone);
            merchants.add((Merchant) newUser);
        }
        users.add(newUser);
        System.out.println("注册成功！");
    }
    // 管理员页面
    private void showAdminMenu() {
        System.out.println("\n===== 管理员菜单 (" + currentUser.getUsername() + ") =====");
        System.out.println("1. 查看所有用户");
        System.out.println("2. 删除用户");
        System.out.println("3. 查看所有订单");
        System.out.println("4. 删除订单");
        System.out.println("5. 查看所有菜品");
        System.out.println("0. 退出登录");
        System.out.print("请选择: ");
        int choice = scanner.nextInt();
        scanner.nextLine(); // 清除换行符
        switch (choice) {
            case 1:
                displayAllUsers();
                break;
            case 2:
                deleteUser();
                break;
            case 3:
                displayAllOrders();
                break;
            case 4:
                deleteOrder();
                break;
            case 5:
                displayAllDishes();
                break;
            case 0:
                currentUser = null;
                System.out.println("已退出管理员登录");
                break;
            default:
                System.out.println("无效选择，请重新输入");
        }
    }
    // 显示所有用户
    private void displayAllUsers() {
        System.out.println("\n===== 所有用户 =====");
        System.out.printf("%-10s\t%-10s\t%-10s\t%-15s\n", "用户名", "用户类型", "密码", "电话");
        for (User user : users) {
            System.out.printf("%-10s\t%-10s\t%-10s\t%-20s\n",
                             user.getUsername(),
                             user.getUserType(),
                             user.getPassword(),
                             user.getPhone());
        }
    }
    // 删除用户
    private void deleteUser() {
        displayAllUsers();
        System.out.print("请输入要删除的用户名: ");
        String username = scanner.nextLine();
        User userToDelete = findUser(username);
        if (userToDelete == null) {
            System.out.println("用户不存在");
            return;
        }
        // 不能删除当前登录用户
        if (userToDelete == currentUser) {
            System.out.println("不能删除当前登录用户");
            return;
        }
        // 删除用户
        users.remove(userToDelete);
        // 如果是学生，从学生列表中移除
        if (userToDelete instanceof Student) {
            students.remove((Student) userToDelete);
        }
        // 如果是商家，从商家列表中移除
        else if (userToDelete instanceof Merchant) {
            merchants.remove((Merchant) userToDelete);
        }
        // 删除相关订单
        List<Order> ordersToRemove = new ArrayList<>();
        for (Order order : allOrders) {
            if (order.getStudent().getUsername().equals(username) ||
                order.getMerchant().getUsername().equals(username)) {
                ordersToRemove.add(order);
            }
        }
        allOrders.removeAll(ordersToRemove);
        System.out.println("用户 " + username + " 及其相关数据已删除");
    }
    // 显示所有订单
    private void displayAllOrders() {
        if (allOrders.isEmpty()) {
            System.out.println("暂无订单");
            return;
        }
        System.out.println("\n===== 所有订单 =====");
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm");
        for (Order order : allOrders) {
            System.out.println("订单号: #" + order.getId());
            System.out.println("学生: " + order.getStudent().getUsername());
            System.out.println("商家: " + order.getMerchant().getUsername());
            System.out.println("时间: " + sdf.format(order.getOrderTime()));
            System.out.println("状态: " + order.getStatus());
            System.out.println("金额: ￥" + order.getTotalAmount());
            System.out.print("菜品: ");
            for (Map.Entry<Dish, Integer> entry : order.getItems().entrySet()) {
                System.out.print(entry.getKey().getName() + "x" + entry.getValue() + " ");
            }
            System.out.println("\n-----------------------");
        }
    }
    // 删除订单
    private void deleteOrder() {
        displayAllOrders();
        if (allOrders.isEmpty()) {
            return;
        }
        System.out.print("请输入要删除的订单号: ");
        int orderId = scanner.nextInt();
        scanner.nextLine();
        boolean found = false;
        Iterator<Order> iterator = allOrders.iterator();
        while (iterator.hasNext()) {
            Order order = iterator.next();
            if (order.getId() == orderId) {
                iterator.remove();
                // 从学生订单列表中移除
                order.getStudent().getOrders().remove(order);
                System.out.println("订单 #" + orderId + " 已删除");
                found = true;
                break;
            }
        }
        if (!found) {
            System.out.println("未找到订单 #" + orderId);
        }
    }
    // 显示所有菜品
    private void displayAllDishes() {
        System.out.println("\n===== 所有菜品 =====");
        if (merchants.isEmpty()) {
            System.out.println("暂无商家");
            return;
        }
        for (Merchant merchant : merchants) {
            System.out.println("商家: " + merchant.getUsername());
            if (merchant.getMenu().isEmpty()) {
                System.out.println("  暂无菜品");
            } else {
                for (Dish dish : merchant.getMenu()) {
                    System.out.printf("  %s - ￥%.2f (库存: %d)\n", dish.getName(), dish.getPrice(), dish.getStock());
                }
            }
            System.out.println("-----------------------");
        }
    }
    // 学生页面
    private void showStudentMenu() {
        Student student = (Student) currentUser;
        System.out.println("\n===== 学生菜单 (" + student.getUsername() + ") =====");
        System.out.println("1. 查看商家列表");
        System.out.println("2. 查看菜单");
        System.out.println("3. 下单");
        System.out.println("4. 查看我的订单");
        System.out.println("5. 取消订单");
        System.out.println("0. 退出登录");
        System.out.print("请选择: ");
        int choice = scanner.nextInt();
        scanner.nextLine(); // 清除换行符
        switch (choice) {
            case 1:
                displayMerchants();
                break;
            case 2:
                displayMerchantMenu();
                break;
            case 3:
                placeOrder(student);
                CSVFileManager.saveMesseges(newOrders);
                newOrders.clear();
                break;
            case 4:
                displayStudentOrders(student);
                break;
            case 5:
                cancelOrder(student);
                CSVFileManager.saveMesseges(newOrders);
                newOrders.clear();
                break;
            case 0:
                currentUser = null;
                System.out.println("已退出登录");
                break;
            default:
                System.out.println("无效选择，请重新输入");
        }
    }
    // 商户页面
    private void showMerchantMenu() throws InterruptedException{
        Merchant merchant = (Merchant) currentUser;
        System.out.println("\n===== 商家菜单 (" + merchant.getUsername() + ") =====");
        System.out.println("1. 查看菜单");
        System.out.println("2. 添加菜品");
        System.out.println("3. 删除菜品");
        System.out.println("4. 修改菜品");
        System.out.println("5. 查看订单");
        System.out.println("6. 完成订单");
        System.out.println("0. 退出登录");
        System.out.print("请选择: ");
        int choice = scanner.nextInt();
        scanner.nextLine(); // 清除换行符
        switch (choice) {
            case 1:
                merchant.displayMenu();
                break;
            case 2:
                addDish(merchant);
                break;
            case 3:
                removeDish(merchant);
                break;
            case 4:
                updateDish(merchant);
                break;
            case 5:
                displayMerchantOrders(merchant);
                break;
            case 6:
                completeOrder(merchant);
                CSVFileManager.saveMesseges(newOrders);
                newOrders.clear();
                break;
            case 0:
                currentUser = null;
                System.out.println("已退出登录");
                break;
            default:
                System.out.println("无效选择，请重新输入");
        }
    }
    // 学生功能
    // 展示商户
    private void displayMerchants() {
        System.out.println("\n===== 商家列表 =====");
        if (merchants.isEmpty()) {
            System.out.println("暂无商家");
        } else {
            for (int i = 0; i < merchants.size(); i++) {
                System.out.println((i + 1) + ". " + merchants.get(i).getUsername());
            }
        }
    }
    // 展示商户菜单
    private void displayMerchantMenu() {
        displayMerchants();
        if (merchants.isEmpty()) return;
        System.out.print("请选择商家序号: ");
        int merchantIndex = scanner.nextInt() - 1;
        scanner.nextLine();
        if (merchantIndex >= 0 && merchantIndex < merchants.size()) {
            merchants.get(merchantIndex).displayMenu();
        } else {
            System.out.println("无效的商家序号");
        }
    }
    // 下单
    private void placeOrder(Student student) {
        displayMerchants();
        if (merchants.isEmpty()) return;
        System.out.print("请选择商家序号: ");
        int merchantIndex = scanner.nextInt() - 1;
        scanner.nextLine();
        if (merchantIndex < 0 || merchantIndex >= merchants.size()) {
            System.out.println("无效的商家序号");
            return;
        }
        Merchant merchant = merchants.get(merchantIndex);
        Order order = new Order(student, merchant);
        while (true) {
            merchant.displayMenu();
            if (merchant.getMenu().isEmpty()) {
                System.out.println("商家暂无菜品，无法下单");
                return;
            }
            System.out.print("请选择菜品序号 (输入0完成下单): ");
            int dishIndex = scanner.nextInt() - 1;
            scanner.nextLine();
            if (dishIndex == -1) {
                if (order.getItems().isEmpty()) {
                    System.out.println("订单为空，未下单");
                } else {
                    student.placeOrder(order);
                    allOrders.add(order);
                    newOrders.add(order);
                    System.out.println("下单成功！订单号: #" + order.getId());
                    order.displayOrder();
                }
                return;
            }
            if (dishIndex >= 0 && dishIndex < merchant.getMenu().size()) {
                Dish dish = merchant.getMenu().get(dishIndex);
                System.out.print("请输入数量: ");
                int quantity = scanner.nextInt();
                scanner.nextLine();
                if (quantity > 0 && dish.getStock() >= quantity) {
                    order.addItem(dish, quantity);
                    System.out.println("已添加: " + dish.getName() + " x " + quantity);
                } else {
                    System.out.println("库存不足或数量无效");
                }
            } else {
                System.out.println("无效的菜品序号");
            }
        }
    }
    // 展示当前订单
    private void displayStudentOrders(Student student) {
        List<Order> orders = student.getOrders();
        if (orders.isEmpty()) {
            System.out.println("暂无订单");
            return;
        }
        System.out.println("\n===== 我的订单 =====");
        for (Order order : orders) {
            order.displayOrder();
        }
    }
    // 取消订单
    private void cancelOrder(Student student) {
        List<Order> orders = student.getOrders().stream()
                .filter(o -> o.getStatus().equals("待处理"))
                .collect(Collectors.toList());
        if (orders.isEmpty()) {
            System.out.println("没有待处理的订单");
            return;
        }
        System.out.println("\n===== 待处理订单 =====");
        for (int i = 0; i < orders.size(); i++) {
            System.out.println((i + 1) + ". 订单号: #" + orders.get(i).getId() +
                              ", 商家: " + orders.get(i).getMerchant().getUsername() +
                              ", 金额: ￥" + orders.get(i).getTotalAmount());
        }
        System.out.print("请选择要取消的订单序号: ");
        int orderIndex = scanner.nextInt() - 1;
        scanner.nextLine();
        if (orderIndex >= 0 && orderIndex < orders.size()) {
            student.cancelOrder(orders.get(orderIndex));
            int flag = 0;
            for (Order neworder : orders) {
                if (neworder.getId() == orders.get(orderIndex).getId()) {
                    flag = 1;
                    break;
                }
            }
            if (flag == 1) {
                newOrders.add(orders.get(orderIndex));
            }
        } else {
            System.out.println("无效的订单序号");
        }
    }
    // 商户功能
    // 添加菜品
    private void addDish(Merchant merchant) {
        System.out.print("请输入菜品名称: ");
        String name = scanner.nextLine();
        System.out.print("请输入价格: ");
        double price = scanner.nextDouble();
        System.out.print("请输入库存: ");
        int stock = scanner.nextInt();
        scanner.nextLine();
        merchant.addDish(new Dish(name, price, stock, 0));
        System.out.println("菜品添加成功");
    }
    // 移除菜品
    private void removeDish(Merchant merchant) {
        merchant.displayMenu();
        if (merchant.getMenu().isEmpty()) return;
        System.out.print("请输入要删除的菜品序号: ");
        int dishIndex = scanner.nextInt() - 1;
        scanner.nextLine();
        if (dishIndex >= 0 && dishIndex < merchant.getMenu().size()) {
            String dishName = merchant.getMenu().get(dishIndex).getName();
            merchant.removeDish(dishName);
            System.out.println("菜品删除成功");
        } else {
            System.out.println("无效的菜品序号");
        }
    }
    // 更新菜品
    private void updateDish(Merchant merchant) {
        merchant.displayMenu();
        if (merchant.getMenu().isEmpty()) return;
        System.out.print("请输入要修改的菜品序号: ");
        int dishIndex = scanner.nextInt() - 1;
        scanner.nextLine();
        if (dishIndex >= 0 && dishIndex < merchant.getMenu().size()) {
            Dish dish = merchant.getMenu().get(dishIndex);
            System.out.print("请输入新价格 (当前: " + dish.getPrice() + "): ");
            double newPrice = scanner.nextDouble();
            System.out.print("请输入新库存 (当前: " + dish.getStock() + "): ");
            int newStock = scanner.nextInt();
            scanner.nextLine();
            merchant.updateDish(dish.getName(), newPrice, newStock);
            System.out.println("菜品修改成功");
        } else {
            System.out.println("无效的菜品序号");
        }
    }
    // 展示订单
    private void displayMerchantOrders(Merchant merchant) {
        List<Order> orders = allOrders.stream()
                .filter(o -> o.getMerchant().equals(merchant))
                .collect(Collectors.toList());
        if (orders.isEmpty()) {
            System.out.println("暂无订单");
            return;
        }
        System.out.println("\n===== 订单列表 =====");
        for (Order order : orders) {
            System.out.println("订单号: #" + order.getId() +
                              ", 学生: " + order.getStudent().getUsername() +
                              ", 状态: " + order.getStatus() +
                              ", 金额: ￥" + order.getTotalAmount());
        }
    }
    // 完成订单
    private void completeOrder(Merchant merchant) {
        List<Order> orders = allOrders.stream()
                .filter(o -> o.getMerchant().equals(merchant) && o.getStatus().equals("待处理"))
                .collect(Collectors.toList());
        if (orders.isEmpty()) {
            System.out.println("没有待处理的订单");
            return;
        }
        System.out.println("\n===== 待处理订单 =====");
        for (int i = 0; i < orders.size(); i++) {
            System.out.println((i + 1) + ". 订单号: #" + orders.get(i).getId() +
                              ", 学生: " + orders.get(i).getStudent().getUsername() +
                              ", 金额: ￥" + orders.get(i).getTotalAmount());
        }
        System.out.print("请选择要完成的订单序号: ");
        int orderIndex = scanner.nextInt() - 1;
        scanner.nextLine();
        if (orderIndex >= 0 && orderIndex < orders.size()) {
            orders.get(orderIndex).complete();
            newOrders.add(orders.get(orderIndex));
            System.out.println("订单 #" + orders.get(orderIndex).getId() + " 已完成");
        } else {
            System.out.println("无效的订单序号");
        }
    }
    public static void main(String[] args) {
        CampusFoodOrderingSystem system = new CampusFoodOrderingSystem();
        system.start();
    }
}