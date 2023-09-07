import random
import pygame, sys
from pygame.locals import *
from const import *
from block import *
from utils import *

class BlockGroup(object):    
    def GenerateBlockGroupConfig(rowIdx, colIdx):
        shapeIdx = random.randint(0, len(BLOCK_SHAPE) - 1)
        bType = random.randint(0, BlockType.BLOCKMAX - 1)
        configList = []
        rotIdx = random.randint(0, len(BLOCK_SHAPE[shapeIdx]) - 1)
        for i in range(len(BLOCK_SHAPE[shapeIdx][rotIdx])):
            config = {
                'blockType' : bType,
                'blockShape' : shapeIdx,
                'blockRot' : rotIdx,
                'blockGroupIdx' : i,
                'rowIdx' : rowIdx,
                'colIdx' : colIdx
            }
            configList.append(config)
        return configList
    
    def __init__(self, blockGroupType, width, height, blockConfigList, relPos):
        super().__init__()
        self.blocks = []
        self.time = 0
        self.pressTime = {}
        self.blockGroupType = blockGroupType
        self.isEliminating = False
        self.dropInterval = 1000
        for config in blockConfigList:
            blk = Block(config['blockType'], config['rowIdx'], config['colIdx'], config['blockShape'], config['blockGroupIdx'], config['blockRot'], width, height, relPos)
            self.blocks.append(blk)
            
    def setBaseIndexes(self, baseRow, baseCol):
        for blk in self.blocks:
            blk.setBaseIndex(baseRow, baseCol)
    
    def draw(self, surface):
        for b in self.blocks:
            b.draw(surface)
            
    def update(self):
        oldTime = self.time
        curTime = getCurrentTime()
        diffTime = curTime - oldTime
        if self.blockGroupType == BlockGroupType.DROP:
            if diffTime >= self.dropInterval:
                self.time = curTime
                for b in self.blocks:
                    b.drop()
            self.keyDownHandler()

        for blk in self.blocks:
            blk.update()
        if self.isEliminate():
            if getCurrentTime() - self.elinimateTime > 500:
                tmpBlocks = []
                for blk in self.blocks:
                    if not blk.getIndex()[0] in self.eliminateRow:
                        if blk.getIndex()[0] < min(self.eliminateRow):
                            for i in range(len(self.eliminateRow)):
                                blk.drop()                            
                        tmpBlocks.append(blk)
                self.blocks = tmpBlocks
                self.setEliminate(False)
                    
    def getBlockIndexes(self):
        return [block.getIndex() for block in self.blocks]

    def getNextBlockIndexes(self):
        return [block.getNextIndex() for block in self.blocks]
    
    
    def getBlocks(self):
        return self.blocks
    
    def clearBlokcs(self):
        self.blocks = []
        
    def addBlocks(self, blk):
        self.blocks.append(blk)
        
    def checkAndSetPressTime(self, key):
        ret = False
        if getCurrentTime() - self.pressTime.get(key, 0) > 30:
            ret = True
        self.pressTime[key] = getCurrentTime()
        return ret    
    
    def keyDownHandler(self):
        pressed = pygame.key.get_pressed()
        if pressed[K_LEFT] and self.checkAndSetPressTime(K_LEFT):
            b = True
            for blk in self.blocks:
                if blk.isLeftBound():
                    b = False
                    break
            if b:
                for blk in self.blocks:
                    blk.doLeft()
        if pressed[K_RIGHT] and self.checkAndSetPressTime(K_RIGHT):
            b = True
            for blk in self.blocks:
                if blk.isRightBound():
                    b = False
                    break
            if b:
                for blk in self.blocks:
                    blk.doRight()
                    
        if pressed[K_DOWN]:
            self.dropInterval = 50
        else:
            self.dropInterval = 1000
        
        if pressed[K_UP] and self.checkAndSetPressTime(K_UP):
            flag = 1
            for blk in self.blocks:
                temp = (blk.blockRot + 1) % (len(BLOCK_SHAPE[blk.blockShape]))
                if BLOCK_SHAPE[blk.blockShape][temp][blk.blockGroupIdx][1] + blk.baseColIdx > GAME_COL - 1:
                    flag = 0
                    break
            if flag:
                for blk in self.blocks:
                    blk.doRotate()
                
    def doEliminate(self, row):
        eliminateRow = {}
        self.elinimateTime = getCurrentTime()
        for col in range(0, GAME_COL):
            idx = (row, col)
            eliminateRow[idx] = 1
        
        for blk in self.blocks:
            if eliminateRow.get(blk.getIndex()):
                blk.startBlink()
                
    def processEliminate(self):
        hash = {}
        
        allIndexes = self.getBlockIndexes()
        for idx in allIndexes:
            hash[idx] = 1
            
        self.eliminateRow = []
        for row in range(GAME_ROW - 1, -1, -1):
            full = True
            for col in range(0, GAME_COL):
                idx = (row, col)
                if not hash.get(idx):
                    full = False
                    break
            if full:
                self.setEliminate(True)
                self.eliminateRow.append(row)
                self.doEliminate(row)
                
        return len(self.eliminateRow)
    
    def setEliminate(self, el):
        self.isEliminating = el
    
    def isEliminate(self):
        return self.isEliminating