nums = [1, 2, 3, 4, 5, 6, 7, 8]

nums = filter(lambda x: x % 2 == 0, nums)
print(list(nums))