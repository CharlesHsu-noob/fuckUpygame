month="JanFebMarAprMayJunJulAugSepOctNovDec"
in_=1
while in_<=12 and in_>=1:
    in_=int(input("請輸入月份:"))
    month_index=(in_-1)*3#1  0,1,2  2  3,4,5  3  6,7,8
    if in_<=12 and in_>=1:
        print(month[month_index:in_*3])
        break
    else:
        print("糖")
        in_=1
