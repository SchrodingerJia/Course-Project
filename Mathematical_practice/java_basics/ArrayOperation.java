import java.util.*;

public class ArrayOperation {
    public static void main(String[] args) {
        int [] a = new int [10];
        for(int i = 0; i < 10; i++) {
            a[i] = i + 1;
        }
        int sum = 0;
        for(int e : a) {
            sum += e;
        }
        System.out.println(sum);
    }
}