a = [1, 2, 1];
b = [1, 2];
sys = tf(b, a);

t = 0:0.01:5;
f = exp(2 * t);

figure;
lsim(sys, f, t);
title('系统响应及输入信号');
xlabel('时间');
ylabel('幅值');
legend('系统响应');
grid on;

y = lsim(sys, f, t);

fprintf('时间(s)\t响应值\n');
for time = 0:1:5
    idx = find(t >= time, 1);
    fprintf('%.1f\t\t%.4f\n', t(idx), y(idx));
end