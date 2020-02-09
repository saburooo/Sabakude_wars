import pyxel
import sys
import copy
from mousecollide import MouseCollied
import random
import math
from enum import Enum

"""
現状の課題。
１、キャラを選択して云々の処理がまだ入ってない。
２、クラスを分割できない。(正直見通しが悪くなってしまった。)
"""
CHIPSIZE = 16

MAPSIZE_X = 18
MAPSIZE_Y = 16

VIEW_WIDTH = 256
VIEW_HEIGHT = 256 

class Phase(Enum):
    pause = -1
    not_selected= 0    # 選ばれていない。
    moving = 1          # 移動中
    attack = 2          # 攻撃
    wait = 3            # 待機
    end_faze = 5        # 行動終了

    enemy_end_faze = 6        # 行動終了

class Turn(Enum):
    player = 0
    enemy = 1

class UnitPhase(Enum):
    not_selected = 0
    selected = 1

class Board():
    def __init__(self):
        self.map = []
        for y in range(MAPSIZE_Y):
            self.map.append([-1] * MAPSIZE_X)

        for x in range(MAPSIZE_X):
            self.map[0][x] = -10
            self.map[MAPSIZE_Y - 1][x] = -10

        for y in range(MAPSIZE_Y):
            self.map[y][0] = -10
            self.map[y][MAPSIZE_X - 1] = -10

        self.fcamera_x = 0
        self.fcamera_y = 0
        # チップの数に問題あり

        self.fcamera_x_chip = 0
        self.fcamera_y_chip = 0

        self.enemy_type = {
            'A':10,
            'B':9,
            'C':8,
            'D':7,
            'E':6,
        }
        self.ob_list = []
        self.open_list = []
        self.close_list = []
        self.route_list = []

    def init(self):
        self.phase = Phase.not_selected
        self.turn = Turn.player
    
    def anime_init(self):
        self.move_timer = 0
        self.move_speed = 10

    def create_map(self):
        for y in range(1, len(self.map) - 1):
            for x in range(1, len(self.map[0]) - 1):
                if self.rand_parsen(5): # 5%の確率で岩山を出す。 
                    self.map[y][x] = -2
        self.copy_map = copy.deepcopy(self.map)
        self.unit_map = copy.deepcopy(self.map)
        self.unit_map[MAPSIZE_Y - 3][MAPSIZE_X // 2 - 1] = 5
        self.unit_map[MAPSIZE_Y - 3][MAPSIZE_X // 2] = 5
        self.unit_map[MAPSIZE_Y - 3][MAPSIZE_X // 2 + 1] = 5
        # ついでにここで敵生成
        self.unit_map[MAPSIZE_Y // 4][MAPSIZE_X // 2 - 2] = 10
        self.unit_map[MAPSIZE_Y // 4][MAPSIZE_X // 2 - 1] = 9
        self.unit_map[MAPSIZE_Y // 4][MAPSIZE_X // 2    ] = 8
        self.unit_map[MAPSIZE_Y // 4][MAPSIZE_X // 2 + 1] = 7
        self.unit_map[MAPSIZE_Y // 4][MAPSIZE_X // 2 + 2] = 6
        self.init()
        self.anime_init()
        self.ob_search()

    class Unit:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.life = 50
            self.at_point = 10

        def life_draw(self):
            pyxel.rect(0, 0, self.life, CHIPSIZE, 5)

    def update(self):
        self.check_click_unit()
        self.move_unit()
        self.unit_search()
        self.scroll_map()
        self.turn_judge()
        self.enemy_turn()

    def draw(self):
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                self.map_draw(y,x)
                self.unit_draw(y,x)
                self.map_searched_draw(y,x)

    def ob_search(self):
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                if self.map[y][x] <= -5:
                    self.ob_list.append((x, y))

    def unit_search(self):
        self.unit_list = []
        self.enemy_list = []
        for y in range(len(self.unit_map)):
            for x in range(len(self.unit_map[0])):
                if self.unit_map[y][x] == 5:
                    self.unit_list.append((x,y))
                if self.unit_map[y][x] >= 6:
                    #                       x,y,enemy_type
                    self.enemy_list.append((x,y,self.unit_map[y][x]))
        # import pdb;pdb.set_trace()

    def unit_generage(self):
        for i in self.unit_list:
            unit = self.Unit(i[1], i[0])
        for j in self.enemy_list:
            enemy = self.Unit(j[1],j[0])
    
    def co_search(self, p_tuple):
        return p_tuple[0] * CHIPSIZE, p_tuple[1] * CHIPSIZE

    def rand_parsen(self, n):
        if random.randint(0, 99) < n:
            return True

    # むしろカメラが動いてマップの見える位置が変わる

    def scroll_map(self):
        if pyxel.btnp(pyxel.KEY_D, 1, 3):
            self.fcamera_x += CHIPSIZE
            self.fcamera_x_chip += 1
            if self.fcamera_x > CHIPSIZE * (MAPSIZE_X - CHIPSIZE):
                self.fcamera_x = CHIPSIZE * (MAPSIZE_X - CHIPSIZE)
                self.fcamera_x_chip = MAPSIZE_X - CHIPSIZE
       
        if pyxel.btnp(pyxel.KEY_A, 1, 3):
            self.fcamera_x -= CHIPSIZE
            self.fcamera_x_chip -= 1
            if self.fcamera_x < 0:
                self.fcamera_x = 0 
                self.fcamera_x_chip = 0

        if pyxel.btnp(pyxel.KEY_W, 1, 3):
            self.fcamera_y -= CHIPSIZE
            self.fcamera_y_chip -= 1
            if self.fcamera_y < 0:
                self.fcamera_y = 0 
                self.fcamera_y_chip = 0
       
        if pyxel.btnp(pyxel.KEY_S, 1, 3):
            self.fcamera_y += CHIPSIZE
            self.fcamera_y_chip += 1
            if self.fcamera_y > CHIPSIZE * (MAPSIZE_Y - CHIPSIZE):
                self.fcamera_y = CHIPSIZE * (MAPSIZE_Y - CHIPSIZE) 
                self.fcamera_y_chip = MAPSIZE_Y - CHIPSIZE
       
        return
   
    # ここから移動範囲のupdateメソッド、そしてユニットのメソッド
    
    def check_click_unit(self):
        self.mx = pyxel.mouse_x // 16 + self.fcamera_x_chip
        self.my = pyxel.mouse_y // 16 + self.fcamera_y_chip
        if self.phase == Phase.not_selected and self.turn == Turn.player:
            if pyxel.btn(pyxel.MOUSE_LEFT_BUTTON):
                if self.unit_map[self.my][self.mx] == 5:
                    self.sx = self.mx
                    self.sy = self.my
                    self.phase = Phase.moving
                    self.movepoint = self.unit_map[self.my][self.mx]
                    self.search_4_vec(self.mx, self.my, self.movepoint)
                    #分身を防ぐための苦肉の策
                    self.unit_map[self.my][self.mx] = self.copy_map[self.my][self.mx]

    def move_unit(self):
        if self.phase == Phase.moving:
            if pyxel.btnr(pyxel.MOUSE_RIGHT_BUTTON):
                if self.copy_map[self.my][self.mx] >= 0:
                    pyxel.play(0, 0, loop=False)
                    self.gx = self.mx
                    self.gy = self.my
                    # ここにmove関数
                    self.unit_map[self.my][self.mx] = 5
                    self.copy_map = copy.deepcopy(self.map)
                    self.phase = Phase.end_faze 
                    # self.phase = Phase.not_selected
    
    def search_4_vec(self, x, y, movepoint):
        """
        ４方向をsearchする。
        移動範囲を調べる
        """
        if 0 < x and x < len(self.map[0]) and 0 < y and y < len(self.map):
            self.search_map(x, y-1, movepoint)
            self.search_map(x, y+1, movepoint)
            self.search_map(x-1, y, movepoint)
            self.search_map(x+1, y, movepoint)

    def search_map(self, x, y, movepoint):
        if x < 0 or len(self.copy_map[0]) <= x:
            return

        if y < 0 or len(self.copy_map) <= y:
            return
        
        if (movepoint - 1) <= self.copy_map[y][x]:
            return

        # 今サーチしてるマスのunit_map上に何かいたら。
        if self.unit_map[y][x] >= 5:
            return
        
        movepoint += self.map[y][x]
        
        if movepoint > 0:
            self.copy_map[y][x] = movepoint
            self.search_4_vec(x, y, movepoint)
        else:
            movepoint = 0

    # ここからdraw関数

    def map_draw(self,y,x):
        pyxel.blt(x * CHIPSIZE, y * 16, 0, 0, 16, 16, 16)
        if self.map[y][x] == -1:
            pyxel.blt(x * CHIPSIZE - self.fcamera_x, y * 16 - self.fcamera_y, 0, 0, 16, 16, 16)
        elif self.map[y][x] == -10:
            pyxel.blt(x * CHIPSIZE - self.fcamera_x, y * 16 - self.fcamera_y, 0, 0, 32, 16, 16)
        elif self.map[y][x] == -2:
            pyxel.blt(x * CHIPSIZE - self.fcamera_x, y * 16 - self.fcamera_y, 0, 0, 48, 16, 16, colkey=1)

    def unit_draw(self,y,x):
        # いちいちcopy_mapを初期化するため、そこにユニットを置いたら、ほかのユニットが消える恐れがある。
        if self.unit_map[y][x] == 5:
            pyxel.blt(x * CHIPSIZE - self.fcamera_x, y * CHIPSIZE - self.fcamera_y, 0, 16, 0, 16, 16,colkey=0)
        if self.unit_map[y][x] == self.enemy_type['A']:
            pyxel.blt(x * CHIPSIZE - self.fcamera_x, y * CHIPSIZE - self.fcamera_y, 0, 16, 16, 16, 16,colkey=1)
        if self.unit_map[y][x] == self.enemy_type['B']:
            pyxel.blt(x * CHIPSIZE - self.fcamera_x, y * CHIPSIZE - self.fcamera_y, 0, 16, 32, 16, 16,colkey=1)
        if self.unit_map[y][x] == self.enemy_type['C']:
            pyxel.blt(x * CHIPSIZE - self.fcamera_x, y * CHIPSIZE - self.fcamera_y, 0, 16, 48, 16, 16,colkey=1)
        if self.unit_map[y][x] == self.enemy_type['D']:
            pyxel.blt(x * CHIPSIZE - self.fcamera_x, y * CHIPSIZE - self.fcamera_y, 0, 16, 64, 16, 16,colkey=1)
        if self.unit_map[y][x] == self.enemy_type['E']:
            pyxel.blt(x * CHIPSIZE - self.fcamera_x, y * CHIPSIZE - self.fcamera_y, 0, 16, 80, 16, 16,colkey=1)

    def map_searched_draw(self, y, x):
        self.msc = MouseCollied(y, x, y * CHIPSIZE, x * 16)
        if self.msc.point_check_hit():
            pyxel.blt(pyxel.mouse_x // 16 * CHIPSIZE, pyxel.mouse_y // 16 * 16, 0, 0, 0, 16, 16, colkey=0)
        if self.copy_map[y][x] >= 0 and self.copy_map[y][x] <= 4:
            pyxel.rectb(x*CHIPSIZE - self.fcamera_x, y*CHIPSIZE - self.fcamera_y, CHIPSIZE, CHIPSIZE, 12)
        if self.copy_map[y][x] == 5:
            pyxel.blt(x * CHIPSIZE - self.fcamera_x, y * CHIPSIZE - self.fcamera_y, 0, 16, 0, 16, 16,colkey=0)
        if self.phase == Phase.moving:
            pyxel.blt(pyxel.mouse_x // 16 * CHIPSIZE, pyxel.mouse_y // 16 * 16, 0, 32, 0, 16, 16, colkey=0)
    
    """
    ちなみにここから敵AIのルーチン
    敵Ａ：猪突猛進型（ひたすらプレイヤーを追いかけてくる）
    敵Ｂ：通常型（ＰＣとの単純距離差５５以内なら近づいてくる）
    敵Ｃ：守備型（ＰＣとの単純距離差が３以内になった所で近づき、以後は距離に関係なく常にプレイヤーを追いかけるＡ型になる）
    敵Ｄ：ピボット型（ある地点から単純距離半径６以上の地点へは何があっても進めない。その範囲の中でプレイヤーに近づこうとする）
    敵Ｅ：アーチャー（単純距離差が５以内で近づくのだが、主人公からの単純距離差が３になる地点を確保しようとする） 
    """
    class Node:
        def __init__(self, x, y, cost = 0, pare_id = None):
            self.x = x
            self.y = y
            self.cost = cost
            # 親ノード
            self.pare_id = pare_id
        
        def return_cost(self):
            return self.cost

    def enemy_turn(self):
        if self.turn == Turn.enemy and self.phase == Phase.not_selected:
            if self.enemy_list == None:
                print("Enemy Not Found")
                return
            self.phase = Phase.moving
            self.enemy_move(self.enemy_list[random.randint(0, len(self.enemy_list)-1)], \
                self.unit_list[random.randint(0, len(self.unit_list)-1)])
            self.enemy_attack()
            self.enemy_end()

    def enemy_move(self, enemy_ad, unit_ad):
        if self.phase == Phase.moving:
            self.search_4_vec(enemy_ad[0], enemy_ad[1], 6)
            self.calc_move(enemy_ad, unit_ad)
            # import pdb;pdb.set_trace()
            self.copy_map = copy.deepcopy(self.map)
            self.phase = Phase.attack

    def calc_move(self, enemy_ad, unit_ad, t_cost = 0):
        move_id = self.Node(enemy_ad[0], enemy_ad[1])
        self.open_list.append(move_id)
        try:
            # まず自分の周りをオープンして、そこに移動したらターゲットの地点に近づくか遠のくか計算し、それをNodeのコストに換算する。
            # Nodeクラスで作ったその時点でのコストをよそと比較し、一番コストが小さいNodeの地点へ移動する。
            # open_nodeを行う範囲を拡張すれば、移動範囲が広がるのだが・・・
            for i in range(-1, 1):
                for j in range(-1, 1):
                    self.open_node(enemy_ad[0] + i, enemy_ad[1] + j, unit_ad[0], unit_ad[1], t_cost)

            if not self.open_list:
                return

            move_id = self.cost_search()

            if move_id.x == enemy_ad[1] and move_id.y == enemy_ad[0]:
                return
            
            if move_id.x == unit_ad[1] and move_id.y == unit_ad[0]:
                print("Find Goal")
                return
            
            """
            self.route_list.append(move_id)
            
            if self.copy_map[move_id.y][move_id.x] > 0 and self.unit_map[move_id.y][move_id.y] < 5:
                self.calc_move(enemy_ad, (move_id.x, move_id.y), t_cost=t_cost + 1)
            """

            self.unit_map[enemy_ad[1]][enemy_ad[0]] = self.map[enemy_ad[1]][enemy_ad[0]]
            self.unit_map[move_id.y][move_id.x] = enemy_ad[2]

        except IndexError as inde:
            print("Unexpected error in calc_move: {}".format(inde))
            print("self.open_list", self.open_list)

    def open_node(self, x, y, tx, ty, t_cost):
        heu_cost = abs(max(tx - x, ty - y))

        if self.unit_map[y][x] >= 5:
            return

        if self.copy_map[y][x] <= 0:
            return

        for i in self.ob_list:
            if i[0] == x and i[1] == y:
                return

        aNode = self.Node(x, y, cost=heu_cost + t_cost)

        for _, bNode in enumerate(self.open_list):
            if aNode.x == bNode.x and aNode.y == bNode.y:
                if aNode.cost < bNode.cost:
                    bNode.cost = aNode.cost

        self.open_list.append(aNode)
        # self.unit_map[y][x] = self.enemy_type["B"]

        return self.open_list
    
    def cost_search(self):
        if not self.open_list:
            print("Not Node")
            return
        # close_listに計算済みのノードを格納したい。
        # import pdb;pdb.set_trace()
        try:
            most_min_cost = sorted(self.open_list, key=lambda c:c.return_cost())[1]
            return most_min_cost
        except:
            print("Unexpected error in cost_search:", sys.exc_info()[0])
    
    def enemy_attack(self):
        if self.phase == Phase.attack:
            # print("Enemy Attacks")
            self.phase = Phase.wait

    def enemy_end(self):
        if self.phase == Phase.wait:
            # print("Enemy End")
            self.phase = Phase.enemy_end_faze

    def turn_judge(self):
        if self.phase == Phase.end_faze:
            self.turn = Turn.enemy
            self.phase = Phase.not_selected
        if self.phase == Phase.enemy_end_faze:
            # import pdb; pdb.set_trace()
            self.init()

class App():
    def __init__(self):
        pyxel.init(VIEW_WIDTH, VIEW_HEIGHT, caption="mouse")
        pyxel.load("Tile.pyxres")
        self.board = Board()
        self.board.create_map()
        pyxel.run(self.update, self.draw)

    def update(self):
        self.board.update()

    def draw(self):
        self.board.draw()

App()