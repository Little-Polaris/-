import pygame, sys
from pygame.locals import *
from blockGroup import *
from const import *

class Game(pygame.sprite.Sprite):
    def __init__(self, surface):
        self.surface = surface
        self.fixedBlockGroup = BlockGroup(BlockGroupType.FIXED, BLOCK_SIZE_W, BLOCK_SIZE_H, [], self.getRelPos())
        self.dropBlockGroup = None
        self.nextBlockGroup = BlockGroup(BlockGroupType.DROP, BLOCK_SIZE_W, BLOCK_SIZE_H, BlockGroup.GenerateBlockGroupConfig(0, GAME_COL + 3), self.getRelPos())
        self.gameOverImage = pygame.image.load("pic\\GameOver.png")
        gameOverImageSize = [i * GAME_WIDTH_SIZE / self.gameOverImage.get_size()[0]  for i in self.gameOverImage.get_size()]  
        self.gameOverImage = pygame.transform.scale(self.gameOverImage, gameOverImageSize)
        self.scoreFont = pygame.font.Font(None, 60)
        self.score = 0
        self.isGameOver = False
    
    def generateDropBlockGroup(self):
        self.dropBlockGroup = self.nextBlockGroup
        self.dropBlockGroup.setBaseIndexes(0, GAME_COL / 2 - 1)
        self.generateNextBlockGroup()
        
    def generateNextBlockGroup(self):
        conf = BlockGroup.GenerateBlockGroupConfig(0, GAME_COL + 3)
        self.nextBlockGroup = BlockGroup(BlockGroupType.DROP, BLOCK_SIZE_W, BLOCK_SIZE_H, conf, self.getRelPos())
    
    def update(self):
        if self.isGameOver:
            return
        self.checkGameOver()
        self.fixedBlockGroup.update()
        if self.fixedBlockGroup.isEliminate():
            return
        if self.dropBlockGroup:
            self.dropBlockGroup.update()
        else:
            self.generateDropBlockGroup()
        if self.willCollide():
            blocks = self.dropBlockGroup.getBlocks()
            for blk in blocks:
                self.fixedBlockGroup.addBlocks(blk)
            self.dropBlockGroup.clearBlokcs()
            self.dropBlockGroup = None
            self.score += self.fixedBlockGroup.processEliminate()
            
    def draw(self):
        self.fixedBlockGroup.draw(self.surface)
        if self.dropBlockGroup:
            self.dropBlockGroup.draw(self.surface)
        self.nextBlockGroup.draw(self.surface)
        if self.isGameOver:
            rect = self.gameOverImage.get_rect()
            rect.centerx = GAME_WIDTH_SIZE / 2
            rect.centery = GAME_HEIGHT_SIZE / 2
            self.surface.blit(self.gameOverImage, rect)
        
        scoreTextImage = self.scoreFont.render('Score: ' + str(self.score), True, (255, 255, 255))
        self.surface.blit(scoreTextImage, (10, 20))
            
    def getRelPos(self):
        return (240, 50)
    
    def willCollide(self):
        hash = {}
        allIndexes = self.fixedBlockGroup.getBlockIndexes()
        for idx in allIndexes:
            hash[idx] = 1
        dropIndexes = self.dropBlockGroup.getNextBlockIndexes()
        
        for dropIndex in dropIndexes:
            if hash.get(dropIndex):
                return True
            if dropIndex[0] >= GAME_ROW:
                return True
        return False
    
    def checkGameOver(self):
        allIndex = self.fixedBlockGroup.getBlockIndexes()
        for idx in allIndex:
            if idx[0] < 2:
                self.isGameOver = True