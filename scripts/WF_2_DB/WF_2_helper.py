import sys
sys.path.insert(0,'/home/ssh_user/Documents/GitHub/CRAB_Analysis/scripts')
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
        

    
    def get_lims_demographics(self,hsn,date): #1

        self.wgs_run_date = date[:2]+"/"+date[2:4]+"/20"+date[4:]
        unfound_hsn=[]
        conn = co.connect(self.lims_connection)
                
        query="select * from WWPCR_DEMO where HSN in ("+",".join(hsn)+")"
        
        self.lims_df = pd.read_sql(query,conn)   
        
        print(self.lims_df.to_string())

        conn.close()

        #format LIMS DF
        self.lims_df = self.lims_df.rename(columns = self.demo_names)
        
        return hsn
    
    
    def create_genes_df(self,found_genes_dict):
        #read in result files from Freya
        #parse results file
        #place each gene into a corresponding column in DATA FRAME


        self.genes_df = pd.DataFrame.from_dict(found_genes_dict, orient='index',columns=['hsn','gene','coverage','identity','db_used','accession_seq','gene_product','resistance'])

        self.genes_df['hsn']=self.genes_df['hsn'].astype(int)

        #print(len(self.genes_df))

        #print(self.genes_df.head())

    def parse_gene_output(samples,path_to_res):
        pass        

    def merge_dfs(self): #3
        #will use this to merge all the different DFs 
        #Demographics
        #Run Stats
        #MLST typing

        #self.log.write_log("merge_dfs","Merging dataframes")
        self.lims_df['hsn']=self.lims_df['hsn'].astype(int)
        
        self.df = pd.merge(self.lims_df, self.mlst_df, how="inner", on="hsn")

        self.df = pd.merge(self.df, self.metrics_df, how="inner", on="hsn")

       #self.log.write_log("merge_dfs","Done")
    
    def format_dfs(self): #4
        self.df = self.df.rename(columns = self.demo_names)
        #self.log.write_log("format_dfs","Starting")
        # format columns, insert necessary values
        #self.log.write_log("format_dfs","Adding/Formatting/Sorting columns")
        #print(self.df.columns.to_list())
        self.df = add_cols(obj=self, \
            df=self.df, \
            col_lst=self.add_col_lst, \
            col_func_map=self.col_func_map)

        # sort/remove columns to match list
        self.df = self.df[self.sample_data_col_order]

        #self.log.write_log("format_dfs","Done")
    

    def database_push(self, excel_path,runD): #5
        #self.log.write_log("database_push","Starting")
        self.setup_db()

        df_demo_lst = self.df.values.astype(str).tolist()
       
        i=0
        while i < len(df_demo_lst):
        
            t= df_demo_lst[i][-1].split("%")[0][2:]
            
            df_demo_lst[i]= df_demo_lst[i][:-1]+[t]

            i+=1
    

        self.write_query_tbl1 = (" ").join(self.write_query_tbl1)

        self.create_ncbi_csv(excel_path,runD,df_demo_lst)

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
        