f(x:float,a:int) = x**2 + h(a)
h(x:int) = x**10 - 10
g(x:int) = 1 / (f(x,5) - h(3)) + h(5)

print(f(10,5))
print(h(3))
print(h(5))
print(g(10))