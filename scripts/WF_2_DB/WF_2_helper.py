import sys
sys.path.insert(0,'/epi/home/ssh_user/Documents/GitHub/Waste-Water/scripts')
from ms_sql_handler import ms_sql_handler
import pandas as pd
import cx_Oracle as co
import reader 
import datetime
from other import add_cols
import json



class demographics_import():

    def __init__(self,cache_path) : #0
        #here need to import json file
        #and used that to store
        demo_cahce= json.load(open(cache_path+"/data/private_cache.json"))
        for item in [*demo_cahce] :
            setattr(self,item, demo_cahce[item])
        
        self.l=['Lineages_1','Lineages_2','Lineages_3','Lineages_4','Lineages_5','Lineages_6','Lineages_7','Lineages_8','Lineages_9','Lineages_10','Lineages_11','Lineages_12','Lineages_13','Lineages_14','Lineages_15']
        self.a=['Abundance_1','Abundance_2','Abundance_3','Abundance_4','Abundance_5','Abundance_6','Abundance_7','Abundance_8','Abundance_9','Abundance_10','Abundance_11','Abundance_12','Abundance_13','Abundance_14','Abundance_15']
        
        

    
    def get_lims_demographics(self,hsn,date): #1

        self.wgs_run_date = date[:2]+"/"+date[2:4]+"/20"+date[4:]
        unfound_hsn=[]
        conn = co.connect(self.lims_connection)
                
        query="select * from WWPCR_DEMO where HSN in ("+",".join(hsn)+")"
        
        self.lims_df = pd.read_sql(query,conn)   
        print("lims imported")

        conn.close()

        #format LIMS DF
        self.lims_df = self.lims_df.rename(columns = self.demo_names)
        self.lims_df["WGS_RunDate"] = self.wgs_run_date
        return hsn
    

    def create_genes_df(self,path_to_res,runD): #2
        path_to_res += "/"+runD+"/final/"+runD+"_all.tsv"


        #open/read file
        all_tsv = pd.read_csv(path_to_res,sep="\t")
        #RENAME AND fix HSN
        all_tsv = all_tsv.rename(columns={'Unnamed: 0':"HSN"})
        all_tsv["HSN"] = [ i.split("_")[0] for i in all_tsv['HSN'].values ]
        #print(all_tsv)
        self.num_of_columns = len(all_tsv['lineages'].str.split(' ', n=14, expand=True).columns)
        
        
        #seperate lineage and abundaNCES
        all_tsv[self.l[:self.num_of_columns]] = all_tsv['lineages'].str.split(' ', n=14, expand=True)
        all_tsv[self.a[:self.num_of_columns]] = all_tsv['abundances'].str.split(' ', n=14, expand=True)
        #print(all_tsv.to_string())
       
        #all_tsv = all_tsv[["HSN","coverage"]+l[:num_of_columns]+a[:num_of_columns]]
        #keeping only nessaary columns
        all_tsv = all_tsv[["HSN"]+self.l[:self.num_of_columns]+self.a[:self.num_of_columns]]

        self.gene_df = all_tsv
        print("GENE DF created")
        
    def create_coverage_df(self,run_data):
        
        self.coverage_df = pd.DataFrame.from_dict(run_data, orient="index",columns=["Position","HSN","Machine_ID","Avg_Q_Score","Coverage_10x","Coverage_100x"])
        self.coverage_df = self.coverage_df[["HSN","Coverage_10x","Coverage_100x"]]
        


# Uncomment this if its not a full run of 16 samples
    # def create_coverage_df(self, run_data): #3
    #     self.coverage_df = pd.DataFrame.from_dict(run_data, orient="index", columns=["Position", "HSN", "Machine_ID", "Avg_Q_Score", "Coverage_10x", "Coverage_100x"])
    #     # Convert 'HSN' to string type
    #     self.coverage_df['HSN'] = self.coverage_df['HSN'].astype(str)
    #     self.coverage_df = self.coverage_df[["HSN", "Coverage_10x", "Coverage_100x"]]
           
    
    def merge_dfs(self,runD): 
        #will use this to merge all the different DFs 
        
        self.lims_df['HSN']=self.lims_df['HSN'].astype(int)
        self.coverage_df['HSN'] = self.coverage_df['HSN'].astype(int)
        
        self.gene_df['HSN']=self.gene_df['HSN'].astype(int)
        
        self.temp_df = pd.merge(self.lims_df, self.gene_df, how="inner", on="HSN")

        self.df = pd.merge(self.temp_df, self.coverage_df, how="inner", on="HSN")
        #add summary path
        self.summary_path= self.summary_path+runD
        self.df["PATH_to_Summary"] = self.summary_path
        

# Uncomment this if its not a full run of 16 samples
    # def merge_dfs(self,runD):  #4
    #     #will use this to merge all the different DFs 
    #     self.lims_df['HSN']=self.lims_df['HSN'].astype(int)
    #     # Filter out non-numeric 'HSN' values (Blank1 and Blank2)
    #     self.coverage_df = self.coverage_df[~self.coverage_df['HSN'].isin(['Blank1', 'Blank2'])]

    #     # Convert 'HSN' column to integer type
    #     self.coverage_df['HSN'] = self.coverage_df['HSN'].astype(int)
    #     self.gene_df['HSN']=self.gene_df['HSN'].astype(int)
        
    #     self.temp_df = pd.merge(self.lims_df, self.gene_df, how="inner", on="HSN")
    #     self.df = pd.merge(self.temp_df, self.coverage_df, how="inner", on="HSN")
    #     #add summary path
    #     self.summary_path= self.summary_path+runD
    #     self.df["PATH_to_Summary"] = self.summary_path
        

    def database_push(self): #5
        #self.log.write_log("database_push","Starting")
        self.setup_db()
        
        df_demo_lst = self.df.values.astype(str).tolist()
        
        for i in range(1,self.num_of_columns+1):
            self.write_query_tbl1[0] += f", Lineage_"+str(i)
            #self.write_query_tbl1[1] += f", '{"+str(i+4)+"}' "
        for i in range(1,self.num_of_columns+1):
            self.write_query_tbl1[0]+= f", Abundance_"+str(i)
            #if i == 15:
                #self.write_query_tbl1[1]+= ", '{"+str(i+self.num_of_columns+4)+"}' "
            #else:
                #self.write_query_tbl1[1]+= ", {"+str(i+self.num_of_columns+4)+"} "
                
        self.write_query_tbl1[0] += ", Coverage_10x, Coverage_100x, PATH_to_Summary) VALUES "

        
        # Now build the Values part with conistent quoting
        placeholders = []
        for i in range(len(self.df.columns)):
            placeholders.append(f"'{{{i}}}'")
            
        self.write_query_tbl1[1]= f"({','.join(placeholders)})"
        #self.write_query_tbl1[1]+= ", '{"+str(i+self.num_of_columns+5)+"}', '{"+str(i+self.num_of_columns+6)+"}', '{"+str(i+self.num_of_columns+7)+"}' )" 
        self.write_query_tbl1 = " ".join(self.write_query_tbl1) 
        print("Final query: ", self.write_query_tbl1)

        self.db_handler.lst_ptr_push(df_lst=df_demo_lst, query=self.write_query_tbl1)
 
    

    def setup_db(self):
        self.db_handler = ms_sql_handler(self)
        self.db_handler.establish_db()
    


if __name__ == "__main__":
    
    import_demo = demographics_import("/epi/home/ashita.jawali@kdhe.state.ks.us/Documents/GitHub/Waste-Water")
    sample_hsn = import_demo.get_lims_demographics(['2434975','2445821','2468507','2488768','2492075','2506355','2510743','2527973'],"111323","/epi/home/ssh_user/WGS_Drive/CRAB_WGS_Sequencing")

        
