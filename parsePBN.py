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
import random
import numpy as np
import itertools
import math
import os
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


class RankDB():
    
    def __init__(self,name):
        self.name = name
        self.rankingParam = dict()
        self.importedFiles = dict()        
        self.namesDict = dict()
        self.ratingHist = dict()
        self.scoreHist = dict()
        self.env = trueskill.TrueSkill()
        self.namesDictInv = dict()        
        
    def importFile(self,path,env):
    
        file = PBNFile(path)
        fileId = file.infoDict['ContestName'] +'_'+ file.infoDict['ContestDate']        
        if fileId in self.importedFiles.keys():
            return None
        else:
            self.importedFiles[fileId] = file
            
        if type(file.TotScoreTable) == str:
            return None
        
        self.updateDBNames(file.TotScoreTable,env)
        pairTable = self.pairIdTable(file.TotScoreTable)
        
        self.updateMPScore(file.TotScoreTable)
        
        random.shuffle(file.gamesList)        
        
        for game in file.gamesList:
            newRatingDict = self.rateGame_4vs4_partial(game,pairTable,env)
            if type(newRatingDict) == type(None):
                continue
            
            #self.updateDBRanking(newRatingDict)            
            
        return None
        
    def initRankingParam(self,env):
        return env.Rating()
        
    def addPlayer(self,ID,env):
        self.rankingParam[ID] = self.initRankingParam(env)
        
        tmpR = list()
        #tmpR.append(0)
        tmpR.append(self.rankingParam[ID])     
        self.ratingHist[ID] = tmpR
        #print(self.ratingHist[ID],'hei')
        
        
    
    def updateDBNames(self,totScoreTable,env):
        for i,row in totScoreTable.iterrows():
            if row['MemberID1'] not in self.rankingParam.keys():
                self.addPlayer(row['MemberID1'],env)
                self.namesDict[row['MemberID1']] = row['Names'].split(' - ')[0].strip()
            if row['MemberID2'] not in self.rankingParam.keys():
                self.addPlayer(row['MemberID2'],env)
                self.namesDict[row['MemberID2']] = row['Names'].split(' - ')[1].strip()
        self.namesDictInv = {v:k for k,v in self.namesDict.items()}
        
    def updateDBRanking(self,ratingDict):
        #print(self.ratingHist)
        for k,v in ratingDict.items():
            self.rankingParam[k] = v
            tmpR = self.ratingHist[k]
            tmpR.append(v)
            self.ratingHist[k] = tmpR

    def updateMPScore(self,totScoreTable):
        for i,row in totScoreTable.iterrows():
            if row['MemberID1'] in self.scoreHist.keys():
                tmpL = self.scoreHist[row['MemberID1']]
                tmpL.append(float(row['TotalPercentage']))
                self.scoreHist[row['MemberID1']] = tmpL
            else:
                self.scoreHist[row['MemberID1']] = [float(row['TotalPercentage'])]
            if row['MemberID2'] in self.scoreHist.keys():
                tmpL = self.scoreHist[row['MemberID2']]
                tmpL.append(float(row['TotalPercentage']))
                self.scoreHist[row['MemberID2']] = tmpL
            else:
                self.scoreHist[row['MemberID2']] = [float(row['TotalPercentage'])]
        
                
    
    def partialUpdate(self,perc,rObjNew,rObjOld,env):
        sig = (rObjOld.sigma*rObjNew.sigma)/ np.sqrt(perc*rObjOld.sigma**2 - (perc-1)*rObjNew.sigma**2)
        mu = (rObjOld.mu*(perc-1)*rObjNew.sigma**2 - rObjNew.mu*perc*rObjOld.sigma**2)/((perc-1)*rObjNew.sigma**2 - perc*rObjOld.sigma**2)
        rNew = env.Rating(mu=mu,sigma=sig)
        
        return rNew
    
    def rateGame_2vs2_partial(self,game,pairTable,env):
        
        newRankDict = dict()        
        
        if type(game.ScoreTable) == str:
            return None
        
        for i,row in game.ScoreTable.iterrows():
            idNS = [x for x in pairTable[row['PairId_NS']]]
            idEW = [x for x in pairTable[row['PairId_EW']]]        
            t_NS = tuple([self.rankingParam[x] for x in idNS])
            t_EW = tuple([self.rankingParam[x] for x in idEW])
            if row['MP_NS'] > row['MP_EW']:
                nt_NS,nt_EW = env.rate([t_NS,t_EW],ranks=[0,1])
            elif row['MP_EW'] > row['MP_NS']:
                nt_NS,nt_EW = env.rate([t_NS,t_EW],ranks=[1,0])
            else:
                nt_NS,nt_EW = env.rate([t_NS,t_EW],ranks=[0,0])       


            a = abs(int(row['Percentage_NS']) - 50)/50            
            
            newRankDict[idNS[0]] = self.partialUpdate(a,nt_NS[0],t_NS[0],env)
            newRankDict[idNS[1]] = self.partialUpdate(a,nt_NS[1],t_NS[1],env)

            newRankDict[idEW[0]] = self.partialUpdate(a,nt_EW[0],t_EW[0],env)
            newRankDict[idEW[1]] = self.partialUpdate(a,nt_EW[1],t_EW[1],env)
        
        return newRankDict
            
      





    def win_probability(self,team1, team2,env):
        delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
        sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
        size = len(team1) + len(team2)
        denom = math.sqrt(size * (env.beta * env.beta) + sum_sigma)
        ts = trueskill.global_env()
        return ts.cdf(delta_mu / denom)
        
    
    def rateGame_2vs2(self,game,pairTable,env):
        
        newRankDict = dict()        
        
        if type(game.ScoreTable) == str:
            return None
        
        
        for i,row in game.ScoreTable.iterrows():
            idNS = [x for x in pairTable[row['PairId_NS']]]
            idEW = [x for x in pairTable[row['PairId_EW']]]        
            t_NS = tuple([self.rankingParam[x] for x in idNS])
            t_EW = tuple([self.rankingParam[x] for x in idEW])
            if row['MP_NS'] > row['MP_EW']:
                nt_NS,nt_EW = env.rate([t_NS,t_EW],ranks=[0,1])
            elif row['MP_EW'] > row['MP_NS']:
                nt_NS,nt_EW = env.rate([t_NS,t_EW],ranks=[1,0])
            else:
                nt_NS,nt_EW = env.rate([t_NS,t_EW],ranks=[0,0])       
            
            newRankDict[idNS[0]] = nt_NS[0]
            newRankDict[idNS[1]] = nt_NS[1]
            
            newRankDict[idEW[0]] = nt_EW[0]
            newRankDict[idEW[1]] = nt_EW[1]
        
                
        
        
        
        return newRankDict
    
    def rateGame_4vs4_partial(self,game,pairTable,env):
        
        newRankDict = {x:self.rankingParam[x] for x in [x for y in pairTable.values() for x in y]}  
        
        
        if type(game.ScoreTable) == str:
            return None
        
        a = 1/game.ScoreTable.index.size
        sct = game.ScoreTable.sample(frac=1).reset_index(drop=True)
        #sct = game.ScoreTable
        sct = sct[~(sct.PairId_NS == '-')]
        sct = sct[~(sct.PairId_EW == '-')]
        for i,row in sct.iterrows():
            
            idNS_root = [x for x in pairTable[row['PairId_NS']]]
            idEW_root = [x for x in pairTable[row['PairId_EW']]]
            for i2,row2 in sct.loc[i+1:].iterrows():
                idNS_next = [x for x in pairTable[row2['PairId_NS']]]
                idEW_next = [x for x in pairTable[row2['PairId_EW']]]
                team1 = idNS_root + idEW_next
                team2 = idEW_root + idNS_next
                t1 = tuple([newRankDict[x] for x in team1])
                t2 = tuple([newRankDict[x] for x in team2])
#                if float(row['MP_NS'].replace('-','0')) > float(row2['MP_NS'].replace('-','0')):
#                    nt1,nt2 = env.rate([t1,t2],ranks=[0,1])
#                elif float(row['MP_NS'].replace('-','0')) < float(row2['MP_NS'].replace('-','0')):
#                    nt1,nt2 = env.rate([t1,t2],ranks=[1,0])
#                else:
#                    nt1,nt2 = env.rate([t1,t2],ranks=[0,0])
#                    
                if float(row['Percentage_NS'].replace('-','0')) > float(row2['Percentage_NS'].replace('-','0')):
                    nt1,nt2 = env.rate([t1,t2],ranks=[0,1])
                elif float(row['Percentage_NS'].replace('-','0')) < float(row2['Percentage_NS'].replace('-','0')):
                    nt1,nt2 = env.rate([t1,t2],ranks=[1,0])
                else:
                    nt1,nt2 = env.rate([t1,t2],ranks=[0,0])                    
                
                newRankDict[team1[0]] = self.partialUpdate(a,nt1[0],t1[0],env)
                newRankDict[team1[1]] = self.partialUpdate(a,nt1[1],t1[1],env)
                newRankDict[team1[2]] = self.partialUpdate(a,nt1[2],t1[2],env)
                newRankDict[team1[3]] = self.partialUpdate(a,nt1[3],t1[3],env)
                
                newRankDict[team2[0]] = self.partialUpdate(a,nt2[0],t2[0],env)
                newRankDict[team2[1]] = self.partialUpdate(a,nt2[1],t2[1],env)
                newRankDict[team2[2]] = self.partialUpdate(a,nt2[2],t2[2],env)
                newRankDict[team2[3]] = self.partialUpdate(a,nt2[3],t2[3],env)
                
                newnewUpdateDict = {team1[0]:newRankDict[team1[0]],team1[1]:newRankDict[team1[1]],team1[2]:newRankDict[team1[2]],team1[3]:newRankDict[team1[3]],team2[0]:newRankDict[team2[0]],team2[1]:newRankDict[team2[1]],team2[2]:newRankDict[team2[2]],team2[3]:newRankDict[team2[3]]}
        
                self.updateDBRanking(newnewUpdateDict)
        
        
        
        return newRankDict

    def rateGame_4vs4(self,game,pairTable,env):
        
        newRankDict = {x:self.rankingParam[x] for x in [x for y in pairTable.values() for x in y]}  
        
        
        if type(game.ScoreTable) == str:
            return None
        #sct = game.ScoreTable.sample(frac=1).reset_index(drop=True)
        sct = game.ScoreTable
        sct = sct[~(sct.PairId_NS == '-')]
        sct = sct[~(sct.PairId_EW == '-')]
        for i,row in sct.iterrows():
            
            idNS_root = [x for x in pairTable[row['PairId_NS']]]
            idEW_root = [x for x in pairTable[row['PairId_EW']]]
            for i2,row2 in sct.loc[i+1:].iterrows():
                idNS_next = [x for x in pairTable[row2['PairId_NS']]]
                idEW_next = [x for x in pairTable[row2['PairId_EW']]]
                team1 = idNS_root + idEW_next
                team2 = idEW_root + idNS_next
                t1 = tuple([newRankDict[x] for x in team1])
                t2 = tuple([newRankDict[x] for x in team2])
                if float(row['MP_NS'].replace('-','0')) > float(row2['MP_NS'].replace('-','0')):
                    nt1,nt2 = env.rate([t1,t2],ranks=[0,1])
                elif float(row['MP_NS'].replace('-','0')) < float(row2['MP_NS'].replace('-','0')):
                    nt1,nt2 = env.rate([t1,t2],ranks=[1,0])
                else:
                    nt1,nt2 = env.rate([t1,t2],ranks=[0,0])
                    
                
                newRankDict[team1[0]] = nt1[0]
                newRankDict[team1[1]] = nt1[1]
                newRankDict[team1[2]] = nt1[2]
                newRankDict[team1[3]] = nt1[3]
                
                newRankDict[team2[0]] = nt2[0]
                newRankDict[team2[1]] = nt2[1]
                newRankDict[team2[2]] = nt2[2]
                newRankDict[team2[3]] = nt2[3]
        
                self.updateDBRanking(newRankDict)
        
        
        
        return newRankDict
        
    def pairIdTable(self,totScoreTable):
        
        pairIdTable = dict()
        for i,row in totScoreTable.iterrows():
            pairIdTable[row['PairId']] = [row['MemberID1'],row['MemberID2']]
            
        
        return pairIdTable
        

#leaderboard = pd.DataFrame()
#ratingS = pd.Series(testRankF.rankingParam)
#ratingS.index = [testRankF.namesDict[x] for x in ratingS.index]
#leaderboard['rating'] = ratingS.apply(lambda x: testRankF.env.expose(x))
#leaderboard['mu'] = ratingS.apply(lambda x: x.mu)
#leaderboard['sigma'] = ratingS.apply(lambda x: x.sigma)
#leaderboard.sort_values('rating',ascending = False)

#for i,row in gm2.ScoreTable.iterrows():
#    print(i)
#    idNS_root = [x for x in pairIdTable[row['PairId_NS']]]
#    idEW_root = [x for x in pairIdTable[row['PairId_EW']]]
#    for i2,row2 in gm2.ScoreTable.loc[i+1:].iterrows():
#        idNS_next = [x for x in pairIdTable[row2['PairId_NS']]]
#        idEW_next = [x for x in pairIdTable[row2['PairId_EW']]]
#        team1 = idNS_root + idEW_next
#        team2 = idEW_root + idNS_next
#        print(team1)
#        print(team2)
        
class PBNFile():
    
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
                if line[0] == '[':
                    break
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
                 
        
PBNPath = r'C:\Users\u35249\git\bridgeRanking\PBN_DB\bridgekam_2015-10-08'

def leaderboard(obj,sortby = 'rating'):
    leaderboard = pd.DataFrame()
    ratingS = pd.Series(obj.rankingParam)
    ratingS.index = [obj.namesDict[x] for x in ratingS.index]
    leaderboard['rating'] = ratingS.apply(lambda x: obj.env.expose(x))
    leaderboard['mu'] = ratingS.apply(lambda x: x.mu)
    leaderboard['sigma'] = ratingS.apply(lambda x: x.sigma)
    leaderboard['mean_perc'] = [history(obj,name = x)[1] for x in leaderboard.index]
    return leaderboard.sort_values(sortby,ascending = False)

def history(obj,name='na',mid = 'na'):
    if name!='na':
        mid = obj.namesDictInv[name]
    if mid in obj.scoreHist.keys():
        
        return obj.scoreHist[mid], sum(obj.scoreHist[mid])/len(obj.scoreHist[mid])
    else: 
        return 'na','na'
    


def plot(obj,name='na',mid='na'):
    if name!='na':
        mid = obj.namesDictInv[name]
    pd.Series([x.mu for x in obj.ratingHist[mid]]).plot()

#testP = PBNFile(PBNPath)        
            
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
