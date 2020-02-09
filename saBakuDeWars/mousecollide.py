import pyxel
import math

PLAYER_VEL = 30
fangle = math.pi / 6.0 
vx = PLAYER_VEL * math.cos(fangle)
vy = PLAYER_VEL * math.sin(fangle)
 
class MouseCollied:
    def __init__(self, pos_x, pos_y, wid, hei):
        # ここから
        self.pos_x = pos_x
        self.pos_y = pos_y
        # ここまで
        self.wid = wid
        self.hei = hei
    
    def draw(self):
        pass
    
    def update(self):
        pass

    def click_check_hit(self):
        nResult = False
        if pyxel.btn(pyxel.MOUSE_LEFT_BUTTON):
            if self.point_check_hit():
                nResult = True
            return nResult

    def point_check_hit(self):
        nResult = False
        if ((pyxel.mouse_x > self.pos_x) and
            (pyxel.mouse_x < self.pos_x + self.wid)):
            if ((pyxel.mouse_y > self.pos_y) and
                (pyxel.mouse_y < self.pos_y + self.hei)):
                nResult = True
        return nResult

class Button(MouseCollied):
    def draw(self):
        pyxel.blt(vx, vy, 0, 0, self.buttoned, 16, 8)
    
    def update(self):
        self.buttoned = 16
        if self.click_check_hit():
            self.buttoned = 24

"""
# サンプル
class App:
    def __init__(self):
        pyxel.init(120, 80, caption="実験")
        pyxel.load("Tile.pyxres")
        self.mousecollied = MouseCollied(vx, vy, 16, 16)
        self.button = Button(vx,vy,16,8)
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)
    
    def update(self):
        self.button.update()
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
    
    def draw(self):
        pyxel.cls(0)
        self.button.draw()
        # クリックしたらスライムが出るようにしたい。
        if self.mousecollied.click_check_hit():
            pyxel.blt(60, 20, 0, 0, 0, 16, 16, 1)

App()
"""