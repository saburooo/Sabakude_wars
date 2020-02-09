import csv

MAP_SIZE = [[-1 for i in range(12)] for j in range(12)]

for x in range(len(MAP_SIZE[0])):
    MAP_SIZE[0][x] = -10
    MAP_SIZE[len(MAP_SIZE) - 1][x] = -10

for y in range(len(MAP_SIZE)):
    MAP_SIZE[y][0] = -10
    MAP_SIZE[y][len(MAP_SIZE[0]) - 1] = -10

STAGE_NUM = 1

with open('stage_' + str(STAGE_NUM) + '.txt', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(MAP_SIZE)
