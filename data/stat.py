import sys
fname = sys.argv[1]

with open(fname, "r") as f:
    f.readline()
    cnt = 0
    attack = 0
    benign = 0
    for line in f:
        tmp = line.strip().split(",")
        flag = int(tmp[-3])

        cnt += 1
        if flag == 0:
            benign += 1
        else:
            attack += 1

print ("total: {}".format(cnt))
print ("benign: {}".format(benign))
print ("attack: {}".format(attack))
