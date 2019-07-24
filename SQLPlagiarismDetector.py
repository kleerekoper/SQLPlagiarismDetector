	# SQL Plagiarism Detector - a program to flag submissions as possibly plagiarised
	# Copyright (C) 2019 Anthony Kleerekoper a.kleerekoper@mmu.ac.uk

	# This program is free software: you can redistribute it and/or modify
	# it under the terms of the GNU General Public License as published by
	# the Free Software Foundation, either version 3 of the License, or
	# (at your option) any later version.

	# This program is distributed in the hope that it will be useful,
	# but WITHOUT ANY WARRANTY; without even the implied warranty of
	# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
	# GNU General Public License for more details.

	# You should have received a copy of the GNU General Public License
	# along with this program.	If not, see <http://www.gnu.org/licenses/>.
	
import pandas as pd
from datetime import datetime
import numpy as np
from scipy import stats
import re
import sys
import SQLPlagiarismDetectorUtilities

def equalityMethod(df, ignoreCase = False, ignoreWhitespace = False, ignoreQuotes = False, ignoreBrackets = False):
	df1 = df.copy()
	df2 = df.copy()
	df1['answers_mod'] = df1.answer
	df2['answers_mod'] = df2.answer
	df1['flagged'] = False
	if ignoreCase:
		df1['answers_mod'] = df1['answers_mod'].str.lower()
		df2['answers_mod'] = df2['answers_mod'].str.lower()
	if ignoreWhitespace:
		df1['answers_mod'] = df1['answers_mod'].str.replace(' ','')
		df2['answers_mod'] = df2['answers_mod'].str.replace(' ','')
	if ignoreQuotes:
		df1['answers_mod'] = df1['answers_mod'].str.replace('\'','')
		df1['answers_mod'] = df1['answers_mod'].str.replace('\"','')
		df2['answers_mod'] = df2['answers_mod'].str.replace('\'','')
		df2['answers_mod'] = df2['answers_mod'].str.replace('\"','')
	if ignoreBrackets:
		df1['answers_mod'] = df1['answers_mod'].str.replace('(','')
		df1['answers_mod'] = df1['answers_mod'].str.replace(')','')
		df2['answers_mod'] = df2['answers_mod'].str.replace('(','')
		df2['answers_mod'] = df2['answers_mod'].str.replace(')','')
	totalMatches = 0
	for index1, row1 in df1.iterrows():
		answerBank = df2['answers_mod'][(df2['ques_num']==row1['ques_num']) & (df2['stu_num']!=row1['stu_num'])].values
		if row1['answers_mod'] in answerBank:
			df1.loc[(df1['ques_num']==row1['ques_num']) & (df1['stu_num']==row1['stu_num']),'flagged'] = True
	filename = "output_"+str(datetime.now().strftime("%Y %m %d %H %M %S"))+".csv"
	df1.to_csv(filename, index=False)
	return filename
	
def shuffleMethod(df, removeAlias = False, swapEquals = False, swapTables = False, shuffleWhere = False):
	df1 = df.copy()
	df2 = df.copy()
	# only retain three columns
	df1 = df1[['stu_num','ques_num','answer']]
	df2 = df2[['stu_num','ques_num','answer']]
	df1['answers_mod'] = df1.answer
	df2['answers_mod'] = df2.answer
	df1['answers_mod'] = df1['answers_mod'].str.lower()
	df2['answers_mod'] = df2['answers_mod'].str.lower()
	if removeAlias:	   ## must be done before removing brackets, whitespace and quotes
		df1['answers_mod'] = df1['answers_mod'].apply(SQLPlagiarismDetectorUtilities.removeAliasFromString)
		df2['answers_mod'] = df2['answers_mod'].apply(SQLPlagiarismDetectorUtilities.removeAliasFromString)
	if swapEquals:
		for index2, row2 in df2.copy().iterrows():
			newQueries = SQLPlagiarismDetectorUtilities.dealWithEquals(row2['answers_mod'], swapTables)
			newDF = pd.DataFrame(columns = ['stu_num', 'ques_num', 'answer', 'answers_mod'])
			for i in range(0,len(newQueries)):
				newDF.loc[i] = [row2['stu_num'], row2['ques_num'], row2['answer'], newQueries[i]]
			df2 = df2.append(newDF)
		df2 = df2.drop_duplicates()
	if shuffleWhere:
		for index2, row2 in df2.copy().iterrows():
			newQueries = SQLPlagiarismDetectorUtilities.shuffleWHEREpredicates(row2['answers_mod'])
			newDF = pd.DataFrame(columns = ['stu_num', 'ques_num', 'answer', 'answers_mod'])
			for i in range(0,len(newQueries)):
				newDF.loc[i] = [row2['stu_num'], row2['ques_num'], row2['answer'], newQueries[i]]
			df2 = df2.append(newDF)
		df2 = df2.drop_duplicates()		   
	df1['answers_mod'] = df1['answers_mod'].str.replace(' ','')
	df2['answers_mod'] = df2['answers_mod'].str.replace(' ','')
	df1['answers_mod'] = df1['answers_mod'].str.replace('\'','')
	df1['answers_mod'] = df1['answers_mod'].str.replace('\"','')
	df2['answers_mod'] = df2['answers_mod'].str.replace('\'','')
	df2['answers_mod'] = df2['answers_mod'].str.replace('\"','')
	df1['answers_mod'] = df1['answers_mod'].str.replace('(','')
	df1['answers_mod'] = df1['answers_mod'].str.replace(')','')
	df2['answers_mod'] = df2['answers_mod'].str.replace('(','')
	df2['answers_mod'] = df2['answers_mod'].str.replace(')','')
	for index1, row1 in df1.iterrows():
		answerBank = df2['answers_mod'][(df2['ques_num']==row1['ques_num']) & (df2['stu_num']!=row1['stu_num'])].values
		if row1['answers_mod'] in answerBank:
			df1.loc[(df1['ques_num']==row1['ques_num']) & (df1['stu_num']==row1['stu_num']),'flagged'] = True
		else:
			df1.loc[(df1['ques_num']==row1['ques_num']) & (df1['stu_num']==row1['stu_num']),'flagged'] = False			  
	filename = "output_"+str(datetime.now().strftime("%Y %m %d %H %M %S"))+".csv"
	df1.to_csv(filename, index=False)
	return filename
	

if len(sys.argv) != 2:
	print("Please specify the file containing the submitted answers")
	sys.exit()

	
## NB: Expected format is a CSV containing (at least) the following columns: stu_num, ques_num, answer
try:	
	df = pd.read_csv(sys.argv[1])
except:
	print("Something went wrong reading the input file. Please check that it is a CSV formatted file")
	sys.exit()
	
if not "stu_num" in df.columns or not "ques_num" in df.columns or not "answer" in df.columns:
	print("The CSV containing the submitted answers must have the following columns (with these exact headers, case-sensitive): \"stu_num\", \"ques_num\", \"answer\"")
	sys.exit()	
	
while True:
	choice = input("Please choose a detection method. Your options are:\n \
		1. Strict Equality Method \n \
		2. Equality Method ignoring case \n \
		3. Equality Method ignoring whitespace \n \
		4. Equality Method ignoring quotation marks \n \
		5. Equality Method ignoring brackets \n \
		6. Equality Method ignoring all \n \
		7. Shuffle Method \n \
		8. Shuffle Method ignoring aliases \n \
		9. Shuffle Method swapping equality operands \n \
		10. Shuffle Method swapping equality operands and table names \n \
		11. Shuffle Method shuffling WHERE clauses \n \
		12 Shuffle Method with all swaps and shuffles \n \
		Enter q to quit \n\n \
		Enter choice > ")
	if choice == 'q':
		sys.exit()
	else:
		choice = int(choice)
	if choice < 7:
		ignoreCase = (choice == 2 or choice == 6)
		ignoreWhitespace = (choice == 3 or choice == 6)
		ignoreQuotes = (choice == 4 or choice == 6)
		ignoreBrackets = (choice == 5 or choice == 6)
		loc = equalityMethod(df, ignoreCase, ignoreWhitespace, ignoreQuotes, ignoreBrackets)
		print("\nResults saved to "+loc+"\n")
	else:
		removeAlias = (choice == 8 or choice == 12)
		swapEquals = (choice == 9 or choice == 12)
		swapTables = (choice == 10 or choice == 12)
		shuffleWhere = (choice == 11 or choice == 12)
		loc = shuffleMethod(df, removeAlias, swapEquals, swapTables, shuffleWhere)
		print("\nResults saved to "+loc+"\n")