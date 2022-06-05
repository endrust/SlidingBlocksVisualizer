# -*- coding: sjis -*-
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_a, K_s, K_d, K_f
from copy import deepcopy
import sys

class DrawPuzzle:
    def __init__(self, screen, minX, minY, cellSize, h, w):
        self.screen = screen
        self.minX = minX
        self.minY = minY
        self.cellSize = cellSize
        self.h = h
        self.w = w
        self.font = pygame.font.SysFont(None, int(self.cellSize * 0.8))
    
    def get_dist(self, now_r, now_c, num):
        goal_r = num // self.w
        goal_c = num % self.w
        return abs(now_r - goal_r) + abs(now_c - goal_c)
    
    def get_color(self, now_r, now_c, num):
        dist = self.get_dist(now_r, now_c, num)
        farest_dist = self.h + self.w - 2
        #RGB
        farest_color = (128, 128, 255)
        center_color = (255, 255, 255)
        nearest_color = (255, 128, 128)
        goal_color = (255, 128, 0) # Orange
        # 空白（左上ゴール）のcolor
        zero_color = (128, 255, 128)
        
        if num == 0:
            return zero_color
        if dist == 0:
            return goal_color
        
        ratio = dist / farest_dist
        color = [0] * 3
        for i in range(3):
            if ratio < 0.5:
                color[i] = int(nearest_color[i] * (1 - 2 * ratio) + center_color[i] * 2 * ratio)
            else:
                r = 2 * ratio - 1
                color[i] = int(farest_color[i] * r + center_color[i] * (1 - r))
        return tuple(color)
    
    def draw(self, puzzle):
        for i in range(self.h):
            for j in range(self.w):
                ly = self.minY + self.cellSize * i
                lx = self.minX + self.cellSize * j
                ry = ly + self.cellSize
                rx = lx + self.cellSize
                cy = (ly + ry) // 2
                cx = (lx + rx) // 2
                color = self.get_color(i, j, puzzle[i][j])
                pygame.draw.rect(self.screen, color, (lx, ly, rx - lx, ry - ly), 0)
                pygame.draw.rect(self.screen, (0, 0, 0), (lx, ly, rx - lx, ry - ly), 2)
                if puzzle[i][j] > 0:
                    text = self.font.render(str(puzzle[i][j]), False, (0, 0, 0))
                else:
                    text = self.font.render('', False, (0, 0, 0))
                text_rect = text.get_rect(center = (cx, cy))
                self.screen.blit(text, text_rect)
        

class PuzzleUI:
    def __init__(self, input_path, screen, minX, minY, cellSize):
        self.sleep_time = 100  # 大きくするほど再生がゆっくりになる
        self.process_dir = 1  # 1: 進む、0: 停止、-1: 戻る
        
        with open(input_path, 'r') as f:
            self.h, self.w = map(int, f.readline().split())
            init_puzzle = []
            for i in range(self.h):
                row = list(map(int, f.readline().split()))
                assert(len(row) == self.w)
                init_puzzle.append(row)
            self.corsor = 0
            self.command = f.readline()
        self.history = []
        self.history.append(init_puzzle)
        
        h = len(init_puzzle)
        w = len(init_puzzle[0])
        self.drawPuzzle = DrawPuzzle(screen, minX, minY, cellSize, h, w)
        
    
    def move(self):
        if self.corsor < len(self.command):
            self.corsor += 1   
        if self.corsor >= len(self.history):
            puzzle = deepcopy(self.history[self.corsor - 1])
            oy = -1
            ox = -1
            for y in range(len(puzzle)):
                for x in range(len(puzzle[y])):
                    if puzzle[y][x] == 0:
                        oy = y
                        ox = x
            ny = oy
            nx = ox
            if self.command[self.corsor - 1] == 'U':
                ny -= 1
            elif self.command[self.corsor - 1] == 'R':
                nx += 1
            elif self.command[self.corsor - 1] == 'D':
                ny += 1
            elif self.command[self.corsor - 1] == 'L':
                nx -= 1
            puzzle[oy][ox], puzzle[ny][nx] = puzzle[ny][nx], puzzle[oy][ox]
            self.history.append(puzzle)            
    
    def undo(self):
        if self.corsor - 1 >= 0:
            self.corsor -= 1
    
    def process(self, event_key):
        if event_key == K_UP:
            if self.process_dir != 0:
                self.process_dir = 0
            else:
                self.process_dir = -1
        elif event_key == K_DOWN:
            if self.process_dir != 0:
                self.process_dir = 0
            else:
                self.process_dir = 1
        
        elif self.process_dir == 0:
            if event_key == K_LEFT:
                self.undo()
            if event_key == K_RIGHT:
                self.move()
        
        else:
            if event_key == K_a:
                self.sleep_time = 300
            elif event_key == K_s:
                self.sleep_time = 100
            elif event_key == K_d:
                self.sleep_time = 30
            elif event_key == K_f:
                self.sleep_time = 10
            if self.process_dir > 0:
                self.move()
            else:
                self.undo()
        return
    
    def draw(self):
        self.drawPuzzle.draw(self.history[self.corsor])


def main(args):
    pygame.init() # 初期化
    (w, h) = (500, 500)
    screen = pygame.display.set_mode((w, h), 0, 32) # スクリーン設定
    puzzle_ui = PuzzleUI(args[1], screen, 50, 50, 30)
    
    while(True):
        key = ''
        for event in pygame.event.get(): # 終了処理
            if event.type == QUIT:
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                key = event.key
        
        screen.fill((255, 255, 255)) # 背景色の指定。RGB
        puzzle_ui.process(key)
        puzzle_ui.draw()
        pygame.display.update() # 画面更新
        pygame.time.wait(puzzle_ui.sleep_time)    # 待機（ミリ秒）

if __name__ == '__main__':
    main(sys.argv)