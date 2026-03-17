import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

// 课程类
class Course {
    private String courseName;
    private String teacher;
    private String classTime;

    public Course(String courseName, String teacher, String classTime) {
        this.courseName = courseName;
        this.teacher = teacher;
        this.classTime = classTime;
    }

    public String getCourseName() {
        return courseName;
    }

    public String getTeacher() {
        return teacher;
    }

    public String getClassTime() {
        return classTime;
    }

    @Override
    public String toString() {
        return "课程名称: " + courseName + 
               "\n授课老师: " + teacher + 
               "\n上课时间: " + classTime;
    }
}

// 学生类
class Student {
    private String name;
    private int age;
    private List<Course> courses; // 学生所选课程列表

    public Student(String name, int age) {
        this.name = name;
        this.age = age;
        this.courses = new ArrayList<>();
    }

    // 选择课程
    public void addCourse(Course course) {
        courses.add(course);
        System.out.println(name + "成功选择了课程:" + course.getCourseName());
    }

    // 修改选课
    public void modifyCourse(int index, Course newCourse) {
        if (index >= 0 && index < courses.size()) {
            Course oldCourse = courses.get(index);
            courses.set(index, newCourse);
            System.out.println(name + " 已将课程 " + oldCourse.getCourseName() + 
                               " 替换为 " + newCourse.getCourseName());
        } else {
            System.out.println("无效的课程索引!");
        }
    }

    // 删除课程
    public void removeCourse(int index) {
        if (index >= 0 && index < courses.size()) {
            Course removedCourse = courses.remove(index);
            System.out.println(name + " 已删除课程: " + removedCourse.getCourseName());
        } else {
            System.out.println("无效的课程索引!");
        }
    }

    // 显示学生信息
    public void displayInfo() {
        System.out.println("\n学生信息:");
        System.out.println("姓名: " + name);
        System.out.println("年龄: " + age);
        
        if (courses.isEmpty()) {
            System.out.println("\n该学生尚未选择任何课程");
        } else {
            System.out.println("\n所选课程列表:");
            for (int i = 0; i < courses.size(); i++) {
                System.out.println("\n课程 #" + (i + 1));
                System.out.println(courses.get(i));
            }
        }
    }
}

public class StudentCourseSystem {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        // 创建课程对象
        List<Course> availableCourses = new ArrayList<>();
        availableCourses.add(new Course("Java编程", "张教授", "周一 8:00-10:00"));
        availableCourses.add(new Course("数据结构", "李教授", "周二 10:00-12:00"));
        availableCourses.add(new Course("算法分析", "王教授", "周三 14:00-16:00"));
        availableCourses.add(new Course("数据库原理", "赵教授", "周四 8:00-10:00"));
        availableCourses.add(new Course("计算机网络", "刘教授", "周五 14:00-16:00"));
        
        // 创建学生对象
        List<Student> students = new ArrayList<>();
        students.add(new Student("张三", 20));
        students.add(new Student("李四", 21));
        students.add(new Student("王五", 19));
        
        do {
            System.out.println("\n===== 学生选课系统 =====");
            System.out.println("1. 显示所有学生信息");
            System.out.println("2. 显示所有可用课程");
            System.out.println("3. 为学生选择课程");
            System.out.println("4. 修改学生选课");
            System.out.println("5. 删除学生选课");
            System.out.println("0. 退出系统");
            System.out.print("请选择操作: ");
            
            int choice = scanner.nextInt();
            scanner.nextLine();
            
            switch (choice) {
                case 1: // 显示所有学生信息
                    System.out.println("\n所有学生信息:");
                    for (Student student : students) {
                        student.displayInfo();
                    }
                    break;
                    
                case 2: // 显示所有可用课程
                    System.out.println("\n可用课程列表:");
                    for (int i = 0; i < availableCourses.size(); i++) {
                        System.out.println("\n课程 #" + (i + 1));
                        System.out.println(availableCourses.get(i));
                    }
                    break;
                    
                case 3: // 为学生选择课程
                    System.out.print("请输入学生序号: ");
                    int studentIndex = scanner.nextInt() - 1;
                    scanner.nextLine();
                    
                    if (studentIndex >= 0 && studentIndex < students.size()) {
                        System.out.print("请输入课程序号: ");
                        int courseIndex = scanner.nextInt() - 1;
                        scanner.nextLine();
                        
                        if (courseIndex >= 0 && courseIndex < availableCourses.size()) {
                            students.get(studentIndex).addCourse(availableCourses.get(courseIndex));
                        } else {
                            System.out.println("无效的课程序号!");
                        }
                    } else {
                        System.out.println("无效的学生序号!");
                    }
                    break;
                    
                case 4: // 修改学生选课
                    System.out.print("请输入学生序号: ");
                    studentIndex = scanner.nextInt() - 1;
                    scanner.nextLine();
                    
                    if (studentIndex >= 0 && studentIndex < students.size()) {
                        Student student = students.get(studentIndex);
                        System.out.print("请输入要修改的课程序号: ");
                        int oldCourseIndex = scanner.nextInt() - 1;
                        scanner.nextLine();
                        
                        System.out.print("请输入新课程序号: ");
                        int newCourseIndex = scanner.nextInt() - 1;
                        scanner.nextLine();
                        
                        if (newCourseIndex >= 0 && newCourseIndex < availableCourses.size()) {
                            student.modifyCourse(oldCourseIndex, availableCourses.get(newCourseIndex));
                        } else {
                            System.out.println("无效的新课程序号!");
                        }
                    } else {
                        System.out.println("无效的学生序号!");
                    }
                    break;
                    
                case 5: // 删除学生选课
                    System.out.print("请输入学生序号: ");
                    studentIndex = scanner.nextInt() - 1;
                    scanner.nextLine();
                    
                    if (studentIndex >= 0 && studentIndex < students.size()) {
                        Student student = students.get(studentIndex);
                        System.out.print("请输入要删除的课程序号: ");
                        int courseIndex = scanner.nextInt() - 1;
                        scanner.nextLine();
                        
                        student.removeCourse(courseIndex);
                    } else {
                        System.out.println("无效的学生序号!");
                    }
                    break;
                    
                case 0: // 退出系统
                    System.out.println("退出选课系统");
                    scanner.close();
                    return;
                    
                default:
                    System.out.println("无效的选择，请重新输入!");
            }
        } while (true);
    }
}