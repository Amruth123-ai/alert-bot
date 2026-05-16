# arr = [0,1,1,0,1,0]

# find_the_biggest_consecutive_num = 



def sort_arr(arr,a,b,c):
    result = []
    for i in arr:
        value = a*i*i + b*i + c
        result.append(value)

    result.sort()
    return result

arr = [-4,-2,0,2,4]
print(sort_arr(arr,1,3,5))
