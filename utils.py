import pandas as pd
import numpy as np

# this is used for renaming df columns
def rename_columns(df,existing,renamed_in):
    if len(existing) != len(renamed_in): raise "Invalid len in rename columns"

    for i in range(len(existing)):
        df[renamed_in[i]]=df[existing[i]]
        del df[existing[i]]
        
    return df


# This is used to switch columns that satisfy the condition
def switch_columns(column1_name,column2_name,condition,df):
    (
    df.loc[condition,column1_name],
    df.loc[condition,column2_name]
    ) = (
    df.loc[condition,column2_name],
    df.loc[condition,column1_name]
    )
    return df

# Add experience (played matched)
def _get_number_of_appears(name,date,reference_data):
    return (
        len(reference_data.loc[(reference_data.P1 == name) & (reference_data.Date < date)]) +
        len(reference_data.loc[(reference_data.P2 == name) & (reference_data.Date < date)])
        )
        

def compute_xp(source,reference_data):
    # source contains the data for which the xp is computed
    # reference_data is the that in which the xp is searched
    P1_Experince = []
    P2_Experince = []
    
    for index, row in source.iterrows():
        P1_Experince.append(_get_number_of_appears(row.P1,row.Date,reference_data))
        P2_Experince.append(_get_number_of_appears(row.P2,row.Date,reference_data))
        
    return P1_Experince,P2_Experince



# Computes the W/L ratio until the match time
def _get_wins(name,date,reference_data):
    return(
        len(reference_data.loc[(reference_data.P1 == name) & 
                             (reference_data.Date < date) &  
                             (reference_data.P1_won == True)]) +
        len(reference_data.loc[(reference_data.P2 == name) & 
                             (reference_data.Date < date) &  
                             (reference_data.P1_won == False)])
    ) or 1

def _get_loses(name,date,reference_data):
    return(
        len(reference_data.loc[(reference_data.P1 == name) & 
                             (reference_data.Date < date) &  
                             (reference_data.P1_won == False)]) +
        len(reference_data.loc[(reference_data.P2 == name) & 
                             (reference_data.Date < date) &  
                             (reference_data.P1_won == True)])
    ) or 1


def get_WL_ratio(name,date,reference_data):
    return _get_loses(name,date,reference_data)/_get_wins(name,date,reference_data) *100
                                 

def compute_WL_ratio(source,reference_data):
    # source contains the data for which the ratio is computed
    # reference_data is the that in which the ratio is searched
    P1_WL_ratio = []
    P2_WL_ratio = []
    
    for index, row in source.iterrows():
        P1_WL_ratio.append(get_WL_ratio(row.P1,row.Date,reference_data))
        P2_WL_ratio.append(get_WL_ratio(row.P2,row.Date,reference_data))
        
    return P1_WL_ratio,P2_WL_ratio

def rename_handler(df):
    #  renames data in regards with the new format (p1 and p2) 
    df['P1_won'] = np.random.uniform(0, 1,len(df)) <= .50
    
    existing = ["Winner","Loser","WRank","LRank","WPts","LPts","AvgL","AvgW"]
    renamed_in = ["P1","P2","P1Rank","P2Rank","P1Pts","P2Pts","AvgP2","AvgP1"]
    df = rename_columns(df,existing,renamed_in)
    
    return df


def switcher_handler(df):
    # handle the switching where needed      
    condition = (df["P1_won"] == 0)
    df = switch_columns("P1Rank","P2Rank",condition,df)
    df = switch_columns("P1Pts","P2Pts",condition,df)
    df = switch_columns("P1","P2",condition,df)

    return df

def unwanted_handler(df):
    df = df.replace('NR',df.mean())
    df = df.fillna(df.mean())
    
    return df


def factorize_handler(df):
    # factorizeing non numerical data 
    df["Tournament"] = pd.factorize(df["Tournament"])[0]
    df["Court"] = pd.factorize(df['Court'])[0]
    df["Series"] = pd.factorize(df["Series"])[0]
    df["Surface"] = pd.factorize(df["Surface"])[0]

    # Add weight for the round
    df["Round"] = pd.factorize(df["Round"])[0]
    df["Round"] = df["Round"].apply(lambda x: x*x)
    
    return df

def experience_handler(df,reference_data):
    # Add experience for each player on each match
    Exp1,Exp2 =  compute_xp(df,reference_data)
    df["P1_Experince"] = Exp1
    df["P2_Experince"] = Exp2
    
    return df

def W_L_ratio_handler(df,reference_data):
    # Add Win/Lose ratio for each player on each match
    P1_WL_ratio,P2_WL_ratio = compute_WL_ratio(df,reference_data)
    df["P1_W/L"] = P1_WL_ratio
    df["P2_W/L"] = P2_WL_ratio
    
    return df

def data_handler(df,relevant_columns):
    df = df[relevant_columns]

    df = rename_handler(df)
    print("Finished renaming columns!")
    
    df = switcher_handler(df)
    print("Finish switching columns!")
    
    df = unwanted_handler(df)
    print("Finish dealing with unwanted values!") 
    
    df = factorize_handler(df)
    print("Finish dealing with non numerical values!") 
    
    return df

def features_handler(df,reference_data):
    df = experience_handler(df,reference_data)
    print("Finish dealing with experience feature!") 
    
    df = W_L_ratio_handler(df,reference_data)
    print("Finish dealing with W/L feature!")
    
    return df





