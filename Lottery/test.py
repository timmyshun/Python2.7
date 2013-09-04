def rank(n):
    if n < 1:
        return 1
    return n*rank(n-1)

TOTOL = 16.0*(rank(33)/rank(6)/rank(33-6))
A = 13
filter_1 = 16.0*(rank(33-A)/rank(6)/rank(33-A-6))
B = 28
filter_1 = 16.0*(rank(33-A)/rank(6)/rank(33-A-6))

if __name__  == "__main__":
   print  filter_1/TOTOL
