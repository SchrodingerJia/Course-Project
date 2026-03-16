% 实验1：双边指数信号的时域和频域图
syms t;
f1 = exp(-abs(t));

% 绘制时域波形
figure;
subplot(2,1,1);
fplot(f1, [-5, 5]);
title('时域波形 f_1(t) = e^{-|t|}');
xlabel('t');
ylabel('f_1(t)');

% 计算傅里叶变换并绘制频谱
F1 = fourier(f1);
subplot(2,1,2);
fplot(abs(F1), [-10, 10]);
title('幅度频谱 |F_1(jω)|');
xlabel('ω');
ylabel('|F_1(jω)|');