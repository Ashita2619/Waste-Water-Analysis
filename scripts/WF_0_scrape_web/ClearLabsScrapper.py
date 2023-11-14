import json
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import  datetime
import time 
import sys
import os
from pathlib import Path
import re


class ClearLabsApi():

	def __init__(self, DLoad_Path,resource_p):
		self.DLoad_Path = DLoad_Path
		opt = Options()
		opt.add_experimental_option("prefs", {
		  "download.default_directory": DLoad_Path,
		  "download.prompt_for_download": False,
		  "download.directory_upgrade": True,
		  "safebrowsing_for_trusted_sources_enabled": False,
		  "safebrowsing.enabled": False})
		opt.add_argument ("headless")
		#opt.headless= True
		#chrome must be install on device runing this
		ChromeDriverPathSer=Service(resource_p+"/resources/chromedriver-linux64/chromedriver")

		self.driver = webdriver.Chrome(service=ChromeDriverPathSer,options=opt)
		self.driver.implicitly_wait(15)


	def login(self,LoginUrl,email, password): #logs you into the website

		self.driver.get(LoginUrl)
	
		self.driver.find_element(By.ID,"cl-field-login-email").send_keys(email)
		self.driver.find_element(By.ID,"cl-field-password-email").send_keys(password)	
		self.driver.find_element(By.ID,"cl-button-login-submit").click()

		print("Login Done")

	def find_runs(self,runIDs):
		#change page to list of run pages
		#//*[@id="app"]/div/div[3]/div[1]/div[1]/nav/ul/li[5]/a/span
		self.driver.find_element(By.XPATH,"//a[@href='/lab/runs']").click() 

		#for run in runIDs:
			
		self.driver.find_element(By.XPATH,'//h2[contains(.,"'+runIDs+'")]').click()
		print("Found Run")
		time.sleep(5)

		run_sample_info=parse_run_data(self.driver.page_source)

		print("Run Data Captured")
		
		self.download_fasta()

		return run_sample_info



	def download_fasta(self):

		print("Starting Download")
		time.sleep(2)
		self.driver.find_element(By.ID,"cl-button-menu-toggle-icon-assets--file--download").click() # clikc on download

		
		#selecting download all fasta and fastaq files
		self.driver.find_element(By.XPATH,"//*[@id=\"app\"]/div/div[3]/div[1]/div[1]/div/header/div/section/div/div[3]/div/div[2]").click()


		self.driver.find_element(By.ID,"cl-button-download-fastq-files-submit").click() # this triggers the ok button after you selected it
		
		print("Download Started")

		
		
	def  close_conns(self):
		self.driver.quit()

def parse_run_data(run_html):

	run_page= bs(run_html,"html.parser")
	
	#finds all samples

	#run_samples= bs.find_all("div", class_="sc-i7x0dw-0 fFrize sc-10cusfd-0 fTCUMn")
	
	sample_info={}
	#for item in run_page.find_all("div", class_="sc-4fik4j-0 kvrlUi sc-1d58pfg-0 zGyGo"):
	#for item in run_page.find_all("div", class_="sc-4fik4j-0 eKzxwl sc-1d58pfg-0 somVH"):
	for item in run_page.find_all("div", class_="sc-9p7gfl-0 sc-4fik4j-1 sc-9bmcrn-0 GBEIg cNTRpz ggueUW"):

	#[position,sampleID, type of analysis, se_coverage,assembly_coverage]
		#if item.find(class_=sc-1ydgn5o-0 mvkvd sc-1d58pfg-1 jYKIos").text != "—":
		if item.find(class_="sc-1tsmysq-0 sc-1ydgn5o-3 bLIfxQ dMUdxZ sc-9bmcrn-1 gMRTTh").text != "—":
			#print(item.find(class_="sc-1ydgn5o-0 ixOnpe sc-1cxzq9f-1 ajslC").text)
			#hsn: postion,hsn,analysus_type, SEQUENCER_AVG_QSCORE, COVERAGE 10X
			sample_info[item.find(class_="sc-1tsmysq-0 sc-1ydgn5o-3 bLIfxQ dMUdxZ sc-9bmcrn-1 gMRTTh").text] = [ item.find(class_="sc-1tsmysq-0 sc-1ydgn5o-3 bLIfxK dMUdxZ sc-9bmcrn-1 gMRTTh").text , \
												       															 item.find(class_="sc-1tsmysq-0 sc-1ydgn5o-3 bLIfxQ dMUdxZ sc-9bmcrn-1 gMRTTh").text, \
																												 item.find(id= re.compile("sequencer")).text, \
																												 item.find(id= re.compile("avg-q-score")).text, \
																											     item.find(class_="sc-1tsmysq-0 sc-1ydgn5o-3 bLIfxL dMUdxZ sc-9bmcrn-1 gMRTTh").text]


	#print(sample_info)
	return sample_info




if __name__ == "__main__":

	s = ClearLabsApi("/home/adrianlimagaray/Downloads","/home/adrianlimagaray/Documents/GitHub/Waste-Water") 				
	#username #PW
	s.login("https://wgs.app.stage.clearlabs.com/","","")
	time.sleep(10)
	q= s.find_runs("BHRL11.2023-11-07.01")

	s.driver.close()

	print(q)


