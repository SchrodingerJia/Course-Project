% 实验2：三角脉冲频谱的三种方法
E = 1;
tao = 1;
omega = linspace(-50, 50, 1000);

% 方法1：数值积分法
F2_num = zeros(size(omega));
for i = 1:length(omega)
    w = omega(i);
    integrand = @(t) E*(1 - 2*abs(t)) .* exp(-1j*w*t) .* (abs(t) <= tao/2);
    F2_num(i) = integral(integrand, -tao/2, tao/2, 'ArrayValued', true);
end

% 方法2：卷积定理法
F_rect = sqrt(E * tao/2) .* sin(omega * tao/4) ./ (omega * tao/4);
F2_conv = F_rect.^2;

% 方法3：理论计算
F2_theory = (4 * E * (1 - cos(omega * tao/2))) ./ (tao * omega.^2);
F2_theory(omega == 0) = 0.5; % 处理omega=0的奇点

% 绘制结果
figure;
subplot(3,1,1);
plot(omega, abs(F2_num));
title('方法1：数值积分法');
xlabel('ω'); ylabel('|F_2(jω)|');

subplot(3,1,2);
plot(omega, abs(F2_conv));
title('方法2：卷积定理法');
xlabel('ω'); ylabel('|F_2(jω)|');

subplot(3,1,3);
plot(omega, abs(F2_theory));
title('方法3：理论计算');
xlabel('ω'); ylabel('|F_2(jω)|');