% 实验3：周期矩形脉冲的傅里叶级数分解
disp('Please input the value of T and tao');   % 命令窗口提示用户输入参数
T = input('T = '); 
tao = input('tao = '); 
E=1;
Nf = 30;
syms t n k x                                 % 定义符号变量 
Nn = 32; 
an = zeros(Nf+1,1);                           % 分配 an 系数数组 
bn = zeros(Nf+1,1);                           % 分配 bn 系数数组 
phase = zeros(Nf+1,1); 
A0 = (E * tao) / T;         % 填空1：求周期信号直流量A0
As = (2*E/(n*pi)) * sin(n*pi*tao/T);         % 填空2：求出周期信号余弦系数As
Bs = 0;       % 填空3：求出周期信号正弦系数Bs
an(1) = double(vpa(A0,Nn));
for k = 1:Nf
   an(k+1) = double(vpa(subs(As,n,k),Nn)); 
   bn(k+1) = double(vpa(subs(Bs,n,k),Nn)); 
end
cn = sqrt(an.^2 + bn.^2);         % 填空4：利用an和bn计算幅度值，并赋予给cn
for i = 1:Nf
if an(i)>=0
phase(i) = 0; 
else 
phase(i) = pi; 
end 
end
t = -T*5:0.001:T*5; 
d = -T*5:T:T*5; 
xx = pulstran(t,d,'rectpuls',tao);                 % 生成矩形脉冲信号 
subplot(3,1,1); 
plot(t,xx); 
axis([-T*5 T*5 0 1.1]);                       % 指定坐标系显示范围 
s1 = strcat('周期矩形脉冲信号T=', num2str(T),' Tao=',num2str(tao),'t'); 
xlabel(s1,'Fontsize',8);                        % x轴标签 
subplot(3,1,2); 
k =0:Nf; 
stem(k,cn);                                 % 绘制幅度谱 
hold on; 
plot(k,cn);                                  % 绘制幅度谱包络线 
xlabel('幅度谱\omega','Fontsize',8); 
subplot(3,1,3); 
stem(k,phase);                               % 绘制相位谱 
xlabel('相位谱\omega','Fontsize',8);