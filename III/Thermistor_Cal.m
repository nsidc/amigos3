%Calculates Best fit curve for thermistor calbration data
%Plots resistance v temperature for 12 thermistor strings

%Skylar Edwards
%Ryan Weatherbee

%TARSAN-JANE
%Colorado Space Grant Consortium
%University of Colorado Boulder

%Last edited 30 January 2019



%Thermistor data is very close to linear. 
%The slopes and y-int of each line of best fit are in "Reg_Data"
%Numbers in Column 1 are slopes and in column 2 are y-intercepts





clear,clc

data = xlsread('Thermistor_data.xlsx');
temp_1 = data(2:end,2);
temp_2 = data(2:end,7);
temp_3 = data(2:end,12);

r6_1 = data(2:end,3);
r10_1 = data(2:end,4);
r20_1 = data(2:end,5);
r40_1 = data(2:end,6);
r6_2 = data(2:end,8);
r10_2 = data(2:end,9);
r20_2 = data(2:end,10);
r40_2 = data(2:end,11);
r6_3 = data(2:end,13);
r10_3 = data(2:end,14);
r20_3 = data(2:end,15);
r40_3 = data(2:end,16);


s = length(r6_1);

mg1 = 1;
bg1 = 1;
init_guesses = [mg1,bg1];
f1 = @(init_guesses)SSE(init_guesses(1),init_guesses(2),temp_1,r6_1);
out = fminsearch(f1,init_guesses);
m_1real = out(1);
b_1real = out(2);
R_approx1 = lin_func(m_1real,b_1real,temp_1);


mg2 = 1;
bg2 = 1;
init_guesses = [mg2,bg2];
f2 = @(init_guesses)SSE(init_guesses(1),init_guesses(2),temp_1,r10_1);
out = fminsearch(f2,init_guesses);
m_2real = out(1);
b_2real = out(2);
R_approx2 = lin_func(m_2real,b_2real,temp_1);


mg3 = 1;
bg3 = 1;
init_guesses = [mg3,bg3];
f3 = @(init_guesses)SSE(init_guesses(1),init_guesses(2),temp_1,r20_1);
out = fminsearch(f3,init_guesses);
m_3real = out(1);
b_3real = out(2);
R_approx3 = lin_func(m_3real,b_3real,temp_1);


mg4 = 1;
bg4 = 1;
init_guesses = [mg4,bg4];
f4 = @(init_guesses)SSE(init_guesses(1),init_guesses(2),temp_1,r40_1);
out = fminsearch(f4,init_guesses);
m_4real = out(1);
b_4real = out(2);
R_approx4 = lin_func(m_4real,b_4real,temp_1);




figure(1),clf,hold on
plot(temp_1,r6_1,'r+')
plot(temp_1,R_approx1,'r-')
plot(temp_1,r10_1,'g+')
plot(temp_1,R_approx2,'g-')
plot(temp_1,r20_1,'k+')
plot(temp_1,R_approx3,'k-')
plot(temp_1,r40_1,'y+')
plot(temp_1,R_approx4,'y-')

xlabel('Temperature (deg C)')
ylabel('Resistance (Ohms)')
title('Thermistor Group 1')




mg5 = 1;
bg5 = 1;
init_guesses = [mg5,bg5];
f5 = @(init_guesses)SSE(init_guesses(1),init_guesses(2),temp_2,r6_2);
out = fminsearch(f5,init_guesses);
m_5real = out(1);
b_5real = out(2);
R_approx5 = lin_func(m_5real,b_5real,temp_2);


mg6 = 1;
bg6 = 1;
init_guesses = [mg6,bg6];
f6 = @(init_guesses)SSE(init_guesses(1),init_guesses(2),temp_2,r10_2);
out = fminsearch(f6,init_guesses);
m_6real = out(1);
b_6real = out(2);
R_approx6 = lin_func(m_6real,b_6real,temp_2);


mg7 = 1;
bg7 = 1;
init_guesses = [mg7,bg7];
f7 = @(init_guesses)SSE(init_guesses(1),init_guesses(2),temp_2,r20_2);
out = fminsearch(f7,init_guesses);
m_7real = out(1);
b_7real = out(2);
R_approx3 = lin_func(m_7real,b_7real,temp_2);


mg8 = 1;
bg8 = 1;
init_guesses = [mg8,bg8];
f8 = @(init_guesses)SSE(init_guesses(1),init_guesses(2),temp_2,r40_2);
out = fminsearch(f8,init_guesses);
m_8real = out(1);
b_8real = out(2);
R_approx8 = lin_func(m_8real,b_8real,temp_2);


figure(2),clf,hold on

plot(temp_2,r6_2,'r-')
plot(temp_2,r10_2,'g-')
plot(temp_2,r20_2,'k-')
plot(temp_2,r40_2,'y+')
plot(temp_2,r40_2,'y-')
plot(temp_2,r6_2,'r+')
plot(temp_2,r10_2,'g+')
plot(temp_2,r20_2,'k+')



xlabel('Temperature (deg C)')
ylabel('Resistance (Ohms)')
title('Thermistor Group 2')


mg9 = 1;
bg9 = 1;
init_guesses = [mg9,bg9];
f9 = @(init_guesses)SSE(init_guesses(1),init_guesses(2),temp_3,r6_3);
out = fminsearch(f9,init_guesses);
m_9real = out(1);
b_9real = out(2);
R_approx9 = lin_func(m_9real,b_9real,temp_3);


mg10 = 1;
bg10 = 1;
init_guesses = [mg10,bg10];
f10 = @(init_guesses)SSE(init_guesses(1),init_guesses(2),temp_3,r10_3);
out = fminsearch(f10,init_guesses);
m_10real = out(1);
b_10real = out(2);
R_approx10 = lin_func(m_10real,b_10real,temp_3);

mg11 = 1;
bg11 = 1;
init_guesses = [mg11,bg11];
f11 = @(init_guesses)SSE(init_guesses(1),init_guesses(2),temp_3,r20_3);
out = fminsearch(f11,init_guesses);
m_11real = out(1);
b_11real = out(2);
R_approx11 = lin_func(m_11real,b_11real,temp_3);

mg12 = 1;
bg12 = 1;
init_guesses = [mg12,bg12];
f12 = @(init_guesses)SSE(init_guesses(1),init_guesses(2),temp_3,r40_3);
out = fminsearch(f12,init_guesses);
m_12real = out(1);
b_12real = out(2);
R_approx12 = lin_func(m_12real,b_12real,temp_3);


figure(3),clf,hold on
plot(temp_3,r6_3,'r+')
plot(temp_3,r6_3,'r-')
plot(temp_3,r10_3,'g+')
plot(temp_3,r10_3,'g-')
plot(temp_3,r20_3,'k+')
plot(temp_3,r20_3,'k-')
plot(temp_3,r40_3,'y+')
plot(temp_3,r40_3,'y-')

xlabel('Temperature (deg C)')
ylabel('Resistance (Ohms)')
title('Thermistor Group 3')


%Slopes and Y-intercepts for each of the 12 thermistors
Reg_data = [m_1real b_1real;m_2real b_2real;m_3real b_3real;m_4real b_4real;...
    m_5real b_5real;m_6real b_6real;m_7real b_7real;m_8real b_8real;...
    m_9real b_9real;m_10real b_10real;m_11real b_11real;m_12real b_12real];


function R = lin_func(m,b,T)

s = length(T);

R = zeros(1,s);
for j = 1:s
    R(j) = m*T(j)+b;
end

end


function SSE_out = SSE(m,b,T,data)

s = length(data);
SSE_vec = zeros(1,s);

for i = 1:s
    SSE_vec(i) = (lin_func(m,b,T(i))-data(i))^2;
end

SSE_out = sum(SSE_vec);
end