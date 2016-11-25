# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 18:36:58 2016

@author: u35249
"""

#pbnFile = open(r'C:\Users\u35249\PBN_DB.pbn')

# This an added comment

import re
import pandas as pd
import trueskill
#
#class bridgeResult():
#    
#    def init(self,PBNPath):
#        
#        
#        f = open(PBNPath)
#        lines = f.readlines()
#        f.close()        
#                
##        if PBNversion2_0:
##            PBN2_0File(PBNPath)
                

#tau
#Also bridge specific tau based on number people played with,against and number times with that person


class rankDB():
    
    def __init__(self,name):
        self.name = name
        self.rankingParam = dict()
        self.importedFiles = list()        
        self.namesDict = dict()        
        
    def importFile(self,path,env):
    
        file = PBNFile(path)
        fileId = file.infoDict[ContestName] +'_'+ file.infoDict[ContestDate]        
        if fileId in self.importedFiles:
            return None
        else:
            self.importedFiles.append(fileId)
            
        if type(file.TotScoreTable) == str:
            return None
        
        self.updateDBNames(file.TotScoreTable,env)
        pairTable = self.pairIdTable(file.TotScoreTable)
        
        
        for game in file.gamesList:
            newRatingDict = self.rateGame(game,pairTable,env)
            if type(newRatingDict) == type(None):
                continue
        
        return None
        
    def initRankingParam(self,env):
        return env.Rating()
        
    def updateDBNames(self,totScoreTable,env):
        for i,row in totScoreTable.iterrows():
            if row['MemberID1'] != self.rankingParam.keys():
                self.rankingParam[row['MemberID1']] = self.initRankingParam(env)
                self.namesDict[row['MemberID1']] = row['Names'].split('-')[0].strip()
            if row['MemberID2'] != self.rankingParam.keys():
                self.rankingParam[row['MemberID2']] = self.initRankingParam(env)
                self.namesDict[row['MemberID2']] = row['Names'].split('-')[1].strip()
        
    def updateDBRanking(self,ratingDict):
        return None
    
    def rateGame(self,game,pairTable,env):
        
        if type(game.ScoreTable) == str:
            return None
        
        for i,row in game.ScoreTable.iterrows():
            t_NS = [self.rankingParam[x] for x in pairTable[row['PairID_NS']]]
            t_EW = [self.rankingParam[x] for x in pairTable[row['PairID_NS']]]
            if row['MP_NS'] > row['MP_EW']:
                nt_NS,nt_EW = env.rate([t_NS,t_EW],ranks=[0,1])
            elif row['MP_EW'] > row['MP_NS']:
                nt_NS,nt_EW = env.rate([t_NS,t_EW],ranks=[1,0])
            else:
                nt_NS,nt_EW = env.rate([t_NS,t_EW],ranks=[0,0])       
        
        
        return newRank
        
    def pairIdTable(self,totScoreTable):
        
        pairIdTable = dict()
        for i,row in totScoreTable.iterrows():
            pairIdTable[row['PairId']] = [row['MemberID1'],row['MemberID2']]
            
        
        return pairIdTable
        
        
class PBNfile():
    
    def __init__(self,PBNPath):
        
        f = open(PBNPath)
        full = f.read()
        f.close()
       
        self.version = re.search(r'(?<=PBN).*',full).group().strip()                
        if type(re.search(r'EXPORT',full)) == type(None):
            self.mode = 'IMPORT'
        else:
            self.mode = 'EXPORT'

        self.parsePBN_2_0(full)
        

    def parsePBN_2_0(self,fullStr):
        names = re.findall(r'(?<=name=)\w+',fullStr)
        contents = re.findall(r'(?<=content=)'+r'\"(.*?)\"',fullStr) 
        if len(names)>0:        
            self.infoDict = dict(zip(names,contents))
        else:
            self.infoDict = 'NA'
        fullEscaped = re.sub(r'\n%.*','',fullStr)
        games = re.split(r'\n\n',fullEscaped)        
                
        self.gamesList = [GamePBN_2_0(x) for x in games]
        for game in self.gamesList:
            if type(game.TotScoreTable) != str:
                self.TotScoreTable = game.TotScoreTable
                break
            else:
                self.TotScoreTable = 'NA'


class GamePBN_2_0():
    
    def __init__(self,gameStr):
        gamesLines = gameStr.split('\n')

        state = 'init'
        totScoreTab = list()
        scoreTab = list()
        for line in gamesLines:
        
        
            firstLine = False
            try:    
                name = line.split()[0]
            except:
                continue
            if name == '[TotalScoreTable':
                state = 'totalScore'
                firstLine = True
                tsHeader = [re.search(r'^[^\\]*',x.replace('"','')).group(0) for x in line.split()[1].split(';')]
            if name == '[ScoreTable':
                state = 'score'
                firstLine = True
                sHeader = [re.search(r'^[^\\]*',x.replace('"','')).group(0) for x in line.split()[1].split(';')]
        
            if state == 'totalScore' and not firstLine:
                totScoreTab.append([x.replace('\"','') for x in re.findall(r'[^"\s]\S*|".*?"', line)])
            if state == 'score' and not firstLine:
                scoreTab.append([x.replace('\"','') for x in re.findall(r'[^"\s]\S*|".*?"', line)])  
        
        if len(totScoreTab)>0:
            TotScoreFrame = pd.DataFrame(totScoreTab, columns = tsHeader) 
            self.TotScoreTable = TotScoreFrame
        else:
            self.TotScoreTable = 'NA'
        if len(scoreTab) >0:
            scoreFrame = pd.DataFrame(scoreTab, columns = sHeader)
            self.ScoreTable = scoreFrame
        else:
            self.ScoreTable = 'NA'
                 
        
PBNPath = r'C:\Users\u35249\PBN_DB\bridgekam_2015-10-08'

testP = PBNfile(PBNPath)        
            
#f = open(PBNPath)
#lines = f.readlines()
#f.close()
#
#f = open(PBNPath)
#full = f.read()
#f.close()

#[x for x in lines if 'META' in x]

#names = re.findall(r'(?<=name=)\w+',full)
#contents = re.findall(r'(?<=content=)'+r'\"(.*?)\"',full)
#
#version = re.search(r'(?<=PBN).*',full).group().strip()
#if type(re.search(r'EXPORT',full)) == type(None):
#    mode = 'IMPORT'
#else:
#    mode = 'EXPORT'
#
#infoDict = dict(zip(names,contents))
#
#fullEscaped = re.sub(r'\n%.*','',full)
#
#games = re.split(r'\n\n',fullEscaped)
#
#
#
#
#infoDict = dict(zip(names,contents))
#
#
#headers = re.search(r'TotalScoreTable.*',games[0]).group(0).split()[1].split(';')
#gamesLines = games[0].split('\n')
#
#
#state = 'init'
#totScoreTab = list()
#scoreTab = list()
#for line in gamesLines:
#
#
#    firstLine = False
#        
#    name = line.split()[0]
#    if name == '[TotalScoreTable':
#        state = 'totalScore'
#        firstLine = True
#        tsHeader = line.split()[1].split(';')
#    if name == '[ScoreTable':
#        state = 'score'
#        firstLine = True
#        sHeader = line.split()[1].split(';')
#
#    if state == 'totalScore' and not firstLine:
#        totScoreTab.append([x.replace('\"','') for x in re.findall(r'[^"\s]\S*|".*?"', line)])
#    if state == 'score' and not firstLine:
#        scoreTab.append([x.replace('\"','') for x in re.findall(r'[^"\s]\S*|".*?"', line)])  
#
#scoreFrame = pd.DataFrame(scoreTab, columns = sHeader)
#TotScoreFrame = pd.DataFrame(totScoreTab, columns = tsHeader)    
