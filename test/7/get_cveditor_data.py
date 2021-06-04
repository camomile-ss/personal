# coding: utf-8
'''
鉄道人流模擬環境自動化ツール cv_editor 関係
'''
import sys

class StationData:
    ''' 駅マスタ '''
    def __init__(self, fname):
        with open(fname, 'r', encoding='utf-8') as f:
            _ = next(f)
            self.data = [[x.strip() for x in l.split('\t')] for l in f]
        self.col_cd, self.col_id, self.col_nm, self.col_lat, self.col_lon = 0, 1, 4, 6, 7
        #self.dic_name_to_cd = {l[self.col_nm]: (l[self.col_cd], l[self.col_id]) for l in self.data}
        self.name_list, self.cd_list, self.id_list = [], [], []
    def conf_data(self):
        print(self.data)
    def mk_name_list(self):
        self.name_list = [x[self.col_nm] for x in self.data]
    def mk_cd_list(self):
        self.cd_list = [x[self.col_cd] for x in self.data]

    def name_to_cd(self, sname):
        ''' 駅名 -> 駅コード, 駅ID '''
        if not self.name_list:
            self.mk_name_list()
        l = self.data[self.name_list.index(sname)]
        return (l[self.col_cd], l[self.col_id])
        #return self.dic_name_to_cd[sname]

    def get_latlon(self, scd):
        ''' 緯度経度 get '''
        if not self.cd_list:
            self.mk_cd_list()
        l = self.data[self.cd_list.index(scd)]
        return (float(l[self.col_lat]), float(l[self.col_lon]))

class RailwayData:
    ''' 路線マスタ '''
    def __init__(self, fname):
        with open(fname, 'r', encoding='utf-8') as f:
            self.data = [[x.strip() for x in l.split('\t')] for l in f]
            col_line_cd, col_line_name = 0, 1
            self.dic_cd_to_name = {x[col_line_cd]: x[col_line_name] for x in self.data}

    def cd_to_name(self, cd):
        ''' 路線コード -> 路線名 '''
        return self.dic_cd_to_name[cd]

#sd = StationData(sys.argv[1])
#latlon = sd.get_latlon('10')
#print(latlon)
#cd = sd.name_to_cd('さくらんぼ東根')
#print(cd)
