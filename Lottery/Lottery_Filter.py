# -*- coding: utf-8 -*-

def filter_1(redBall,blueBall):
    """规则1:限定最小值"""
    if redBall[0] > 13:
        return False
    return True
def filter_2(redBall,blueBall):
    """规则2:限定和值"""
    strict = [159,141,149,50,143,52,153,145,43,54,47,147,158,48,49,58,163,170,51,41,42,154]
    sumRed = sum(redBall)
    if sumRed in strict:
        return False
    return True
def filter_3(redBall,blueBall):
    """规则3:限定连续数"""
    sum_2 = 0
    sum_3 = 0
    sum_4 = 0
    sum_5 = 0
    sum_6 = 0
    if redBall[5] - redBall[0] == 5 :
            sum_6 +=1
    for i in range(2):
        if redBall[i+4] - redBall[i] == 4 :
            sum_5 +=1
    for i in range(3):
        if redBall[i+3] - redBall[i] == 3 :
            sum_4 +=1
    for i in range(4):
        if redBall[i+2] - redBall[i] == 2 :
            sum_3 +=1
    for i in range(5):
        if redBall[i+1] - redBall[i] == 1 :
            sum_2 +=1
    sum_5 -= 2* sum_6
    sum_4 -= (2* sum_5 +3*sum_6)
    sum_3 -= (2* sum_4 +3*sum_5+4*sum_6)
    sum_2 -= (2* sum_3 +3*sum_4+4*sum_5+5*sum_6)

    if sum_4+sum_5 +sum_6 > 0 :
        return False
    if sum_3+ sum_2 > 1:
        return False
    if sum_2 > 2:
        return False
    return True
def filter_4(redBall,blueBall):
    """规则4:去掉全奇数,全偶数"""
    sum_1 = 0
    sum_2 = 0
    for red in redBall:
        if red % 2 == 1:
            sum_1 += 1
        else :
            sum_2 += 1
    if sum_1 == 6  or sum_2 == 6:
        return False
    return True
def filter_5(redBall,blueBall):
    """规则5:限定三区比"""
    sum_1 = 0
    sum_2 = 0
    sum_3 = 0
    for red in redBall:
        if red <12 :
            sum_1 += 1
        elif red < 23:
            sum_2 += 1
        else:
            sum_3 += 1
    a = max([sum_1,sum_2,sum_3])
    if a > 4:
        return False
    return True
def filter_6(redBall,blueBall):
    """规则6:限定同尾"""
    a = [0,0,0,0,0,0,0,0,0,0]
    for red in redBall:
        a[red%10] += 1
    if max(a) > 3 :
        return False
    return True
def filter_7(redBall,blueBall):
    """规则7:限定最大值"""
    if redBall[5] < 21:
        return False
    return True

def filter_8(redBall,blueBall):
    """规则8: """
    
    return True
def filter_9(redBall,blueBall):
    """规则9:  """
    
    return True
def filter_10(redBall,blueBall):
    """规则10: """
    return True


if __name__ == '__main__':


    filter_3([1,2,4,5,6,7],[10])
