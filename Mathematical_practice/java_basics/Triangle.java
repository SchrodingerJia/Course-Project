import java.util.*;
import java.lang.Math;
class NotTriangleException extends Exception {
    NotTriangleException(String message) {
        super(message);
    }
    @Override
    public String toString() {
        return "NotTriangleException[" + getMessage();
    }
}
public class Triangle {
    int x,y,z;
    public Triangle(int x, int y, int z) throws NotTriangleException {
        if (x + y <= z || x + z <= y || y + z <= x) {
            throw new NotTriangleException("三条边无法构成三角形");
        } else {
            this.x = x;
            this.y = y;
            this.z = z;
        }
    }
    double getArea() {
        double p = (x + y + z) / 2;
        return Math.sqrt(p*(p - x)*(p - y)*(p - z));
    }
}
class Test {
    public static void main(String args[]) {
        Scanner scanner = new Scanner(System.in);
        try {
            System.out.print("请输入x:");
            int x = scanner.nextInt();
            scanner.nextLine();
            System.out.print("请输入y:");
            int y = scanner.nextInt();
            scanner.nextLine();
            System.out.print("请输入z:");
            int z = scanner.nextInt();
            scanner.nextLine();
            Triangle triangle = new Triangle(x, y, z);
            System.out.println("该三角形的面积为:"+triangle.getArea());
        } catch (NotTriangleException e) {
            System.err.println(e.getMessage());
        } finally {
            scanner.close();
        }
    }
}