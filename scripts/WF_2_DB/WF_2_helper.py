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
        demo_cahce= json.load(open(cache_path+"/data/private_var.json"))
        for item in [*demo_cahce] :
            setattr(self,item, demo_cahce[item])
        

    
    def get_lims_demographics(self,hsn,date,csv_path): #1

        self.wgs_run_date = date[:2]+"/"+date[2:4]+"/20"+date[4:]
        unfound_hsn=[]
        conn = co.connect(self.lims_connection)
                
        query="select * from WWPCR_DEMO where HSN in ("+",".join(hsn)+")"
        
        self.lims_df = pd.read_sql(query,conn)   
        
        print(self.lims_df.to_string())

        conn.close()

        return hsn
    
    def format_lims_df(self): #2
        # manipulate sql database to format accepted by the master EXCEL worksheet
        #self.log.write_log("format_lims_DF","Manipulating demographics to database format")

        self.lims_df = self.lims_df.rename(columns = self.demo_names)
        #print(self.lims_df.head().to_string())
        
        self.no_lims_hsn = self.no_lims_hsn.loc[:, ~self.no_lims_hsn.columns.str.contains('^Unnamed')]
        self.no_lims_hsn['name']=self.no_lims_hsn['First Name'] + " " + self.no_lims_hsn['Last Name']
        self.no_lims_hsn['HSN']=self.no_lims_hsn['HSN'].astype(int)
        self.no_lims_hsn = self.no_lims_hsn.rename(columns={"Rec'd":"date_recd","WGS Rec'd": "pcr_run_date","HSN": "hsn","Collected": "doc","DOB": "dob","Sex": "sex","State": "state","Source Site": "source","CO":"county"})
        self.no_lims_hsn['pcr_run_date']= pd.to_datetime(self.no_lims_hsn['pcr_run_date'])
        self.no_lims_hsn['date_recd']= pd.to_datetime(self.no_lims_hsn['date_recd'])
        self.no_lims_hsn['dob']= pd.to_datetime(self.no_lims_hsn['dob'])
        self.no_lims_hsn['doc']= pd.to_datetime(self.no_lims_hsn['doc'])
        self.no_lims_hsn.drop(columns=['Extracted','Sequenced','Last Name','First Name','Age','Source Type','Country','Comment','WGS serotype','coverage (calculated from workbook)','#total reads','Clusters passing filter',"HAI WGS ID"], axis=1, inplace=True)

        self.lims_df= pd.concat([self.lims_df,self.no_lims_hsn])

        #self.log.write_log("format_lims_DF","Done!")


    def create_mlst_df(self,mlst_dict):
    #mlst  DICT {HSN:[HSN,species,overallType]}
        #{'2296669_manualy': ['2296669_manualy', 'abaumannii_2', '2']}

        self.mlst_df = pd.DataFrame.from_dict(mlst_dict,orient='index',columns=['hsn','species','mlst'])
        self.mlst_df['hsn']=self.mlst_df['hsn'].astype(int)
        #print(len(self.mlst_df))
        #print(self.mlst_df.head())

    def create_metrics_df(self,assembly_m,pipeline):
        #res[sample]=sample_buso_res["results"]["one_line_summary"]
        #assemblys  DICT {HSN:"C:98.4%[S:98.4%,D:0.0%],F:1.6%,M:0.0%,n:124"}
        # meaning of output "Complete": 98.4, "Single copy": 98.4,"Multi copy": 0.0,"Fragmented": 1.6, "Missing": 0.0, "n_markers": 124,
        for h in [*assembly_m]:
            if pipeline:
                assembly_m[h] =  assembly_m[h]
            else:
                assembly_m[h] =  assembly_m[h][2:6]
            
        self.metrics_df = pd.DataFrame.from_dict(assembly_m,orient='index',columns=['busco_out'])
        self.metrics_df['hsn']=self.metrics_df.index.astype(int)
        #print(len(self.metrics_df))
        #print(self.metrics_df.head())
    
    def create_genes_df(self,found_genes_dict):
        #found_genes DICT {HSN:[[GENE,%COV,%IDENT,DB_Used,Accession_Seq,Gene_Product,Resistance],[GENE2....]]}

        self.genes_df = pd.DataFrame.from_dict(found_genes_dict, orient='index',columns=['hsn','gene','coverage','identity','db_used','accession_seq','gene_product','resistance'])

        self.genes_df['hsn']=self.genes_df['hsn'].astype(int)
        #print(len(self.genes_df))
        #print(self.genes_df.head())

        

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
        