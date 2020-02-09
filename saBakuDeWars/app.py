import pyxel
import sys
import copy
import random
import math
from enum import Enum

"""
現状の課題。
１、キャラを選択して云々の処理がまだ入ってない。
２、クラスを分割できない。(正直見通しが悪くなってしまった。)
"""
CHIPSIZE = 16

# それぞれのユニットのフェイズ
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

class Menu:
    def __init__(self):
        pass

    def draw(self):
        pyxel.bltm(192, 0, 0, 32, 0, 32, 96)
        pyxel.bltm(0, 256 - 64, 0, 0, 0, 256, 64)

class Player(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 50
        self.attack = 10
        self.unit_map = copy.deepcopy(Map().load_map())
        # 選ばれたらTrue
        self.is_active = False
    
    def judge_active(self):
        if self.is_active == True:
            self.update()

    def update(self):
        mx = pyxel.mouse_x // CHIPSIZE
        my = pyxel.mouse_y // CHIPSIZE
        Action().search_4_vec(self.x, self.y, 3, self.unit_map)
        if pyxel.btnp(pyxel.MOUSE_RIGHT_BUTTON, hold= 3, period= 1):
            try:
                if self.unit_map[my][mx] >= 0:
                    pyxel.play(0,0)
                    self.x, self.y = mx, my
                    self.unit_map = copy.deepcopy(Map().load_map())
                    self.is_active = False
            except:
                print("out of range")
        else:
            return False
    
    def __getitem__(self, number):
        return number
    
    def __bool__(self):
        return self.is_active
    
    def get_place(self, x, y):
        return x * CHIPSIZE, y * CHIPSIZE

    def __sub__(self, other):
        return self.life - other.attack
    
    def draw(self):
        x, y = self.get_place(self.x, self.y)
        pyxel.blt(x, y, 0, 16, 0, 16, 16,colkey=1)
        if self.is_active:
            pyxel.text(5, 208, "LIFE POINT", col=7)
            pyxel.rect(48, 208, self.life, 8, col=11)
        Action.draw_mass(self.unit_map)

class Enemy(Player):
    def __init__(self, x, y):
        super().__init__(x, y)

class GameManagement():
    def __init__(self):
        self.player_list = []
        self.enemy_list = []
        self.p_id = 0
    
    def generate_unit(self):
        p_point = [(4,8),(5,8),(6,8)]
        e_point = [(4,2),(5,2),(6,2)]

        for i in p_point:
            player = Player(i[0], i[1])
            self.player_list.append(player)

    def update(self):
        if pyxel.btnp(pyxel.KEY_TAB, hold=10):
            self.player_list[self.p_id].is_active = True
            self.p_id += 1
            if self.p_id == len(self.player_list):
                self.p_id = 0
        '''
        if any(i for i in self.player_list):
            self.player_list[self.p_id - 1].is_active = False 
        '''
        self.player_list[self.p_id].judge_active()

    def draw(self):
        for i in self.player_list:
            i.draw()
        pyxel.blt(pyxel.mouse_x // 16 * CHIPSIZE, pyxel.mouse_y // 16 * 16, 0, 0, 0, 16, 16, colkey=0)
        pyxel.text(5, 224, "PLAYER ID = " + str(self.p_id), col=7)

class Action():
    # ここにてシミュレーション・ゲームの骨格になる移動範囲の計算や移動処理などを実装する。
    @classmethod
    def search_4_vec(cls, x, y, move_point, base_map):
        if 0 < x and x < len(base_map[0]) and 0 < y and y < len(base_map):
            cls.search_map(x, y - 1, move_point, base_map)
            cls.search_map(x, y + 1, move_point, base_map)
            cls.search_map(x - 1, y, move_point, base_map)
            cls.search_map(x + 1, y, move_point, base_map)
    
    @classmethod
    def search_map(cls, x, y, move_point, base_map):
        if x < 0 or len(base_map[0]) <= x:
            return

        if y < 0 or len(base_map) <= y:
            return
        
        if (move_point - 1) <= base_map[y][x]:
            return
        
        if base_map[y][x] >= 5:
            return

        move_point += base_map[y][x]

        if move_point > 0:
            base_map[y][x] = move_point
            cls.search_4_vec(x, y, move_point, base_map)
        else:
            move_point = 0

    @classmethod
    def draw_mass(cls, base_map):
        for y in range(len(base_map)):
            for x in range(len(base_map[0])):
                if base_map[y][x] >= 0 and base_map[y][x] <= 4:
                    pyxel.rectb(x*CHIPSIZE, y*CHIPSIZE, CHIPSIZE, CHIPSIZE, 12)

class Map():
    def __init__(self):
        # マップになるテキストファイルを読み込んでおく。
        self.stage_no = 1
        self.stage = self.load_map()
        self.camera_x = 0
        self.camera_y = 0
    
    def change_stage(self):
        if pyxel.btn(pyxel.KEY_SPACE):
            self.stage_no += 1
            self.load_map()

    def load_map(self):
        row_map = []
        with open("stage_" + str(self.stage_no) + ".txt") as stage:
            for l in stage:
                l = l.rstrip("\n")
                l = l.split(",")
                row_map.append(l)
        row_map = [[int(x) for x in y] for y in row_map]
        return row_map
    
    @staticmethod
    def rand_parsen(n):
        if random.randint(0, 99) < n:
            return True
    
    def draw(self):
        for y in range(len(self.stage)):
            for x in range(len(self.stage[0])):
                if self.stage[y][x] == -1:
                    pyxel.blt(x * CHIPSIZE - self.camera_x, y * CHIPSIZE - self.camera_y, 0, 0, 16, 16, 16)
                elif self.stage[y][x] == -10:
                    pyxel.blt(x* CHIPSIZE - self.camera_x , y * CHIPSIZE - self.camera_y, 0, 0, 32, 16, 16)
                elif self.stage[y][x] == -3:
                    pyxel.blt(x * CHIPSIZE - self.camera_x , y * CHIPSIZE - self.camera_y, 0, 0, 48, 16, 16, colkey=1)

if __name__ == "__main__":
    class App():
        def __init__(self):
            self.map = Map()
            self.manage = GameManagement()
            self.manage.generate_unit()
            self.menu = Menu()
            pyxel.init(256, 256, caption="SABAKU DE WARS", scale=2)
            pyxel.load("Tile.pyxres")
            pyxel.run(self.update, self.draw)

        def update(self):
            try:
                self.manage.update()
            except IndexError as id:
                print("Index error:{0}".format(id))

        def draw(self):
            self.map.draw()
            self.menu.draw()
            self.manage.draw()

    App()