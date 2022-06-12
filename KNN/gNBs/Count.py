from turtle import position


f = open('./points.txt')
datas=[]
for line in f:
    datarray=line.split(" ")
    position=datarray[0][1:-1].split(",")
    position_x=float(position[0])
    position_y=float(position[1])
    RSRPARRAY=[]
    for i in range(1,6):
        RSRPARRAY.append(float(datarray[i]))
    PCell=datarray[-1]
    print(PCell)

# print(text)

# for line in text:
#     print()

