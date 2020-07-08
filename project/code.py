from dbConnect import connect
import pandas as pd
import math
import numpy as np


def split_df(df, chunk_size=500):
    list_of_df = list()
    num_chunks = math.ceil(len(df) / chunk_size)
    for i in range(num_chunks):
        list_of_df.append(df[i * chunk_size:(i + 1) * chunk_size])
    return num_chunks, list_of_df

def select_query(cur,conn):
    query = 'SELECT id FROM "public"."SRC";'
    cur.execute(query)
    records = cur.fetchall()
    # for i in records:
    #     print(i)
    # print(records)
    ls = {i[0] for i in records}
    return ls

def update_db_col(inter,cur,conn,df_dict,cols):
    for j in inter:
        query = 'UPDATE "public"."SRC" SET '
        for i in cols:
            query += i
            query += " = '"+str(df_dict[j][i])+"',"
        query = query[:-1] + " WHERE ID = "+str(j)
        print(query)
        #     execute query
        cur.execute(query)
        conn.commit()
        query = ""
    print("update sucess ....")

def update_db(inter,cur,conn,df):
    query = 'DELETE FROM "public"."SRC" WHERE id IN '+ str(tuple(inter)) +';'
    print("delete query   :",query)
    cur.execute(query)
    conn.commit()
    insert_to_db(inter,cur,conn,df)
    print("update sucess ....")

def insert_to_db(diff,cur,conn,df_dict):
    # print(df_dict,diff)
    query = 'INSERT INTO "public"."SRC" VALUES '
    num = 0
    # print("out",diff)
    for i in diff:
        query += '('+str(i)+', '+(str(tuple(df_dict[i].values()))[1:])+','
        num += 1
    query = query[:-1]
    cur.execute(query)
    conn.commit()
    print("insert sucess",num)

def populate_data(cur, conn, cols=['title']):
    try:
        df = pd.read_csv("test.csv")
        df.fillna(value=np.nan, inplace=True) 
        df.fillna('', inplace=True)
        df.replace({"'": '`'}, regex=True, inplace=True)
        from_db = select_query(cur,conn)
        num_chunks, list_of_df = split_df(df)
        print("num_chunks",num_chunks)
        for df in list_of_df:
            from_df = set(df["id"])
            del df['Unnamed: 0']
            df = df.set_index("id")
            df_dict = df.T.to_dict()
            
            print("from_db:",from_db," from_df:",from_df)
            
            diff = from_df.difference(from_db)
            inter = from_db.intersection(from_df)

            print("insert : ",diff)
            if len(diff) > 0:
                insert_to_db(diff,cur,conn,df_dict)
        
            print("update : ",inter)
            if len(inter) > 0:
                if cols:
                    update_db_col(inter, cur, conn, df_dict, cols)
                else:
                    update_db(inter,cur,conn,df_dict)

    except Exception as e:
        print(e)

if __name__ == "__main__":
    cur, conn = connect()
    
    # create_yotpo_reviews_src(cur,conn)
    # populate_data(cur,conn)
    # print(select_query(cur,conn))
    # print(conn.encoding)
    # conn.close()
    # df = pd.read_csv("dummy.csv")
    # col = ['marks']
    # inter = {1,2}
    # update_db_col(inter,cur,conn,df,col)

