import functools

# lambda parameters: expression

lst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

print(lst)

# map(function, iterable, *iterables) -> iterable

lst_2 = list(map(lambda i: i**2, lst))

print(lst_2)

print([i**2 for i in lst])

lst_3 = list(map(lambda x, y: x + y, lst, lst_2))

print(lst_3)

# filter(function, iterable) -> iterable

result = list(filter(lambda x: x % 2 == 0, lst))

print(result)

print([item for item in lst if item % 2 == 0])


# reduce(function, iterable[, initializer])

result = functools.reduce(lambda x, y: x + y, lst)

print(result)


# zip(*iterables)

# sorted(iterable, key=None, reverse=False)

