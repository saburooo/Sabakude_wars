import pyxel

class Player(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        if pyxel.btn(pyxel.KEY_W):
            self.y -= 1

        if pyxel.btn(pyxel.KEY_S):
            self.y += 1

class Draw:
    CHIPSIZE = 16

    @classmethod
    def to_screen(cls, i, j):
        return (i * cls.CHIPSIZE, j * cls.CHIPSIZE)
    
    @classmethod
    def draw(cls, i, j):
        x, y = cls.to_screen(i, j)
        pyxel.blt(x, y, 0, 16, 0, 16, 16,colkey=1)

if __name__ == "__main__":
    class App():
        def __init__(self):
            self.player = Player(5,5)
            pyxel.init(256, 256, caption="SABAKU DE WARS")
            pyxel.load("Tile.pyxres")
            pyxel.run(self.update, self.draw)

        def update(self):
            self.player.update()

        def draw(self):
            Draw.draw(self.player.x, self.player.y)

    App()
