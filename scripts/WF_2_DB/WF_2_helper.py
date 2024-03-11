import sys
sys.path.insert(0,'/home/ssh_user/Documents/GitHub/Waste-Water/scripts')
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
        #print(self.lims_df.to_string())

        conn.close()

        #format LIMS DF
        self.lims_df = self.lims_df.rename(columns = self.demo_names)
        self.lims_df["WGS_RunDate"] = self.wgs_run_date
        return hsn
    

    def create_genes_df(self,path_to_res,runD):
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
        #print(self.gene_df)
        print("GENE DF created")
        
    def create_coverage_df(self,run_data):
        
        self.coverage_df = pd.DataFrame.from_dict(run_data, orient="index",columns=["Position","HSN","Machine_ID","Avg_Q_Score","Coverage_10x"])
        self.coverage_df = self.coverage_df[["HSN","Coverage_10x"]]

        #print(self.coverage_df)
           
    
    def merge_dfs(self,runD): #3
        #will use this to merge all the different DFs 

        self.lims_df['HSN']=self.lims_df['HSN'].astype(int)
        self.coverage_df['HSN']=self.coverage_df['HSN'].astype(int)
        
        self.gene_df['HSN']=self.gene_df['HSN'].astype(int)
        
        self.temp_df = pd.merge(self.lims_df, self.gene_df, how="inner", on="HSN")

        self.df = pd.merge(self.temp_df, self.coverage_df, how="inner", on="HSN")
        #add summary path
        self.summary_path= self.summary_path+runD
        self.df["PATH_to_Summary"] = self.summary_path
        #self.df = self.df['HSN', 'Facility', 'Date_Collected', 'Date_Received', 'WGS_RunDate','Lineages_1', 'Lineages_2', 'Lineages_3', 'Lineages_4', 'Lineages_5','Lineages_6', 'Lineages_7', 'Lineages_8', 'Lineages_9', 'Lineages_10','Lineages_11', 'Lineages_12', 'Lineages_13', 'Lineages_14','Lineages_15', 'Abundance_1', 'Abundance_2', 'Abundance_3', 'Abundance_4', 'Abundance_5', 'Abundance_6', 'Abundance_7', 'Abundance_8', 'Abundance_9', 'Abundance_10', 'Abundance_11', 'Abundance_12', 'Abundance_13', 'Abundance_14', 'Abundance_15','Coverage_10x']
        
        
        #print(self.df)
        #print(self.df.columns)


    def database_push(self): #5
        #self.log.write_log("database_push","Starting")
        self.setup_db()
        
        df_demo_lst = self.df.values.astype(str).tolist()
        
        for i in range(1,self.num_of_columns+1):
            self.write_query_tbl1[0]+= ", Lineage_"+str(i)
            self.write_query_tbl1[1]+= ", '{"+str(i+4)+"}' "
        for i in range(1,self.num_of_columns+1):
            self.write_query_tbl1[0]+= ", Abundance_"+str(i)
            if i == 15:
                self.write_query_tbl1[1]+= ", '{"+str(i+self.num_of_columns+4)+"}' "
            else:
                self.write_query_tbl1[1]+= ", {"+str(i+self.num_of_columns+4)+"} "
        
        self.write_query_tbl1[0]+= ", Coverage_10x, PATH_to_Summary) VALUES"
        self.write_query_tbl1[1]+= ", '{"+str(i+self.num_of_columns+5)+"}', '{"+str(i+self.num_of_columns+6)+"}' )" 
        self.write_query_tbl1 = (" ").join(self.write_query_tbl1) 
        print(self.write_query_tbl1)

        self.db_handler.lst_ptr_push(df_lst=df_demo_lst, query=self.write_query_tbl1)
 
    

    def setup_db(self):
        self.db_handler = ms_sql_handler(self)
        self.db_handler.establish_db()
    


if __name__ == "__main__":
    
    import_demo = demographics_import("/home/ssh_user/Documents/GitHub/CRAB_Analysis")
    sample_hsn = import_demo.get_lims_demographics(['2434975','2445821','2468507','2488768','2492075','2506355','2510743','2527973'],"111323","/home/ssh_user/WGS_Drive/CRAB_WGS_Sequencing")
    
    #import_demo.database_push()
    #import_demo.get_lims_demographics(["1"],'020323','PATH')
    #import_demo.create_genes_df("{'2296669': [['2296669', 'blaADC-30', '100.00', '100.00', 'ncbi', 'NG_048652.1', 'class C extended-spectrum beta-lactamase ADC-30', 'CEPHALOSPORIN'], ['2296669', 'tet(B)', '99.50', '100.00', 'ncbi', 'NG_048161.1', 'tetracycline efflux MFS transporter Tet(B)', 'TETRACYCLINE'], ['2296669', 'aph(6)-Id', '100.00', '100.00', 'ncbi', 'NG_047464.1', 'aminoglycoside O-phosphotransferase APH(6)-Id', 'STREPTOMYCIN'], ['2296669', 'aph(3'')-Ib', '98.31', '99.88', 'ncbi', 'NG_056002.2', 'aminoglycoside O-phosphotransferase APH(3'')-Ib', 'STREPTOMYCIN'], ['2296669', 'blaOXA-66', '100.00', '100.00', 'ncbi', 'NG_049806.1', 'OXA-51 family carbapenem-hydrolyzing class D beta-lactamase OXA-66', 'CARBAPENEM'], ['2296669', 'sul2', '100.00', '100.00', 'ncbi', 'NG_051852.1', 'sulfonamide-resistant dihydropteroate synthase Sul2', 'SULFONAMIDE'], ['2296669', 'ant(3'')-IIa', '100.00', '98.61', 'ncbi', 'NG_054646.1', 'aminoglycoside nucleotidyltransferase ANT(3'')-IIa', 'SPECTINOMYCIN;STREPTOMYCIN'], ['2296669', 'mph(E)', '100.00', '100.00', 'ncbi', 'NG_064660.1', 'Mph(E) family macrolide 2'-phosphotransferase', 'MACROLIDE'], ['2296669', 'msr(E)', '100.00', '100.00', 'ncbi', 'NG_048007.1', 'ABC-F type ribosomal protection protein Msr(E)', 'MACROLIDE'], ['2296669', 'aac(6')-Ip', '100.00', '99.66', 'ncbi', 'NG_047307.2', 'aminoglycoside 6'-N-acetyltransferase AAC(6')-Ip', 'AMINOGLYCOSIDE'], ['2296669', 'aac(3)-Ia', '100.00', '100.00', 'ncbi', 'NG_047234.1', 'aminoglycoside N-acetyltransferase AAC(3)-Ia', 'GENTAMICIN'], ['2296669', 'blaOXA-72', '100.00', '100.00', 'ncbi', 'NG_049813.1', 'OXA-24 family carbapenem-hydrolyzing class D beta-lactamase OXA-72', 'CARBAPENEM']]}")
    #Desktop/CRAB_OUT/2296669_manualy/scaffolds.fasta 
        