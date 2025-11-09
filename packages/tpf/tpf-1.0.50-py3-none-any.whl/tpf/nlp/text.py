# import numpy as np 
# import pandas as pd 
# from tpf import read,write
# from tpf.data.deal import DataDeal as dtl

# class TextDeal:
    
#     def __init__(self, data) -> None:
#         """文本处理方法集 
#         - data: pandas数表 
#         """
#         self.data = data 
        
#     def log(self,msg, print_level=1):
#         if self.print_level >= print_level:
#             print(msg)
        
        
#     def get_data(self):
#         return self.data 
    
#     def update_data(self,data):
#         self.data = data 
        
#     def head(self,num):
#         return self.data.head(num)
        

#     def word2id(self, c_names, word2id=None):
#         """文本转换成索引
#         - c_names:列名
#         - word2id:编码字典，key为关键字，value为连续的整数索引；若非None，则在该字典基本上添加新的key与index
        
#         return 
#         -----------------------------
#         每个列的编码字典,'<UNK>':0，即每一列的索引0代表未记录的词
        
#         """
        
#         cls_dict = {'<UNK>': 0}
#         global_word2id = {'<UNK>': 0} if word2id is None else word2id.copy()
#         next_index = len(global_word2id)
        
#         # 首先收集所有列的所有唯一词汇
#         all_words = set()
#         for cname in c_names:
#             all_words.update(set(self.data[cname]))
        
#         # 为所有词汇创建全局映射
#         for word in all_words:
#             if word not in global_word2id:
#                 global_word2id[word] = next_index
#                 next_index += 1
        
#         # 为每列创建单独的映射字典（基于全局映射）
#         for cname in c_names:
#             cls_dict[cname] = global_word2id
        
#         # 应用映射到每列
#         for col in c_names:
#             self.data[col] = (
#                 self.data[col]
#                     .map(cls_dict[col])          # 已知类别 → 索引，未知 → NaN
#                     .fillna(0)                   # NaN → 0
#                     .astype(np.int64)            # 转换为整数
#             )
            
#         return self.data, cls_dict

    
    
#     def word2id_pre(self, c_names, word2id=None):
#         """
#         预测时将指定列中的类别转成索引。
#         未知类别统一映射为 0。
        
#         Parameters
#         ----------
#         c_names : list[str]
#             需要转换的列名列表。
#         word2id : dict, optional
#             类别到索引的映射字典。若未提供，则所有值视为未知，全部填 0。
#         """
#         if word2id is None:
#             word2id = {}

#         # 用 0 作为默认值，一次性完成映射
#         for col in c_names:
#             self.data[col] = (
#                 self.data[col]
#                     .map(word2id[col])          # 已知类别 → 索引，未知 → NaN
#                     .fillna(0)             # NaN → 0
#                     .astype("int32")       # 或 Int64 以保留缺失，但这里统一用 0
#             )
            
    
#     def col_filter(self,regex):
#         """
#         选择指定的列,不同的列以|分隔,"name|age",
#         "一元.*" 匹配 "一元一次","一元二次"等所有以"一元"开头的字符串 
#         """
#         self.data = self.data.filter(regex=regex)
#         self.log("数据过滤之后的列-------------------------:",2)
#         self.log(self.data.info(),2)

#     def empty_num(self,col_name):
#         self.data.loc[(self.data[col_name].isnull()), col_name] = np.mean(self.data[col_name])

#     def empty_str(self,col_name,char_null="N"):
#         self.data.loc[(self.data[col_name].isnull()), col_name] = char_null

#     def error_max_7mean(self,col_name):
#         """
#         超过均值7倍的数据转为均值7倍
#         """
#         col_mean = np.mean(self.data[col_name])
#         self.data[col_name][self.data[col_name]>7*col_mean] = 7*col_mean
    
    
#     def onehot_encoding(self,c_names):
#         """pandas onehot编码，每个类别一个新列
#         """
#         for cname in c_names:
#             c_new_1 = pd.get_dummies(self.data[cname], prefix=cname)
#             self.data = pd.concat([self.data,c_new_1],axis=1)
#             self.data.drop([cname], axis=1, inplace=True)

#     def col_drop(self,c_names):
#         self.data.drop(c_names,axis=1,inplace=True)

#     def replace_blank(self,to_float=True):
#         """
#         去除空格，并将NIL置0
#         """
#         for col in self.columns():
#             index = 0
#             for val in self.data[col]:
#                 # print("data type :",type(val))
#                 if isinstance(val,str):
#                     matchObj = re.search( r'\s+', val)

#                     if to_float:
#                         # print("---col:{},val--{}==".format(col,val))
#                         if val == "NIL":
#                             val = "0"
#                         if matchObj:
#                             self.data[col].iloc[index] = float(val.replace('\s+','',regex=True,inplace=True))
#                         else:
#                             self.data[col].iloc[index] = float(val)
#                     else:
#                         if matchObj:
#                             self.data[col].iloc[index] = val.replace('\s+','',regex=True,inplace=True)
#                 else:
#                     continue
#                 index +=1



#     def min_max_scaler(self,feature_range=(0, 1)):
#         """
#         return
#         ---------------------
#         <class 'numpy.ndarray'>,MinMaxScaler自动将pandas.core.frame.DataFrame转为了numpy.ndarray
        
#         """
#         self.scaler = MinMaxScaler(feature_range=feature_range)
#         self.replace_blank()
#         data = self.scaler.fit_transform(self.data)
#         return data 

#     def min_max_scaler_inverse(self, data):
#         data = self.scaler.inverse_transform(data)
#         return data 

    

# class TextEmbedding:
#     cls_dict = {}
#     def __init__(self):
#         pass
    
#     @classmethod
#     def cls2index(cls,df, classify_type=[],word2id=None):
#         """类别转索引"""
#         dtl.str_pd(df,classify_type)
#         tt = TextDeal(data=df)
#         for cc in classify_type:
#             df,cls_dict = tt.word2id([cc],word2id=word2id)
#             cls.cls_dict.update(cls_dict)
#         return  df 
    
#     @classmethod
#     def cls2index2(cls,df, classify_type=[],word2id=None):
#         """类别转索引"""
#         dtl.str_pd(df,classify_type)
#         tt = TextDeal(data=df)
        
#         df,cls_dict = tt.word2id(classify_type,word2id=word2id)
#         cls.cls_dict.update(cls_dict)
#         return  df 
    
#     @classmethod
#     def cls2index_pre(cls,df, classify_type, word2id):
#         """类别转索引预测"""
#         dtl.str_pd(df,classify_type)
#         tt = TextDeal(data=df)
#         tt.word2id_pre(classify_type,word2id=word2id)


#     @classmethod
#     def col2index(cls,df,classify_type,classify_type2=[],dict_file="dict_file.dict",is_pre=False,word2id=None):
#         """pandas列转索引
#         - classify_type:类别列
#         - classify_type2:类别列2,每个元素是一个列表，如[[a,b],[c,d]]，每个元素是一个类别列
#         """
#         if is_pre:
#             if word2id is None:
#                 word2id = read(dict_file)
#             for cc in classify_type2:
#                 classify_type.extend(cc)
#             cls.cls2index_pre(df, classify_type=classify_type, word2id=word2id) 
#         else: #重新编码
#             for c in classify_type2:
#             ## 类别编码扩充,机构作为账户特征,pc.col_type.classify_type不能再包含bank了，否则会重复编码
#                 df = cls.cls2index2(df, classify_type=c,word2id={})

#             ## 类别索引编码
#             df = cls.cls2index(df, classify_type=classify_type)
#             write(cls.cls_dict,dict_file)
             

