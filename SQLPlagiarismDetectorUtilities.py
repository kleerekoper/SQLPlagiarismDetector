	# SQL Plagiarism Detector - a program to flag submissions as possibly plagiarised
	# This file contains utility functions
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

import re

def removeAliasFromString(queryString):
	queryParts = queryString.split('from') # select list always ends with the keyword 'from'
	secondPart = queryParts[1]
	selectClause = queryParts[0].replace('select ', '')
	selectList = re.split(',(?![\'\"a-z0-9.,\s]*\))', selectClause)	 # split on commas not inside brackets
	newList = []
	for column in selectList:
		column = column.strip()
		isDistinct = False
		isUnique = False
		if "distinct" in column:
			isDistinct = True
			column = column.replace('distinct', '')
		if "unique" in column:
			isUnique = True
			column = column.replace('unique', '')
		column = re.sub('as [\'"a-z0-9 ]+$', '', column).strip()	 ## as alias in quotes
		column = re.sub('["\'][a-z0-9 ]+["\'][\s]*$', '', column).strip()	  ## alias in quote marks
		column = re.sub('[ ]+[a-z0-9]+[\s]*$', '', column)	   ## alias without quote marks
		if isDistinct:
			column = 'distinct '+column
		if isUnique:
			column = 'unique '+column
		newList.append(column.strip())
	reformedQuery = 'select ' +	 ", ".join(newList) + ' from' + secondPart
	return reformedQuery
	
	
def dealWithEquals(queryString, swapTables = False):
	queryString = queryString.lower()
	## if queryString contains one or more equals signs, create new queryStrings with the comparisons swapped ie a=b becomes b=a
	if re.search('[a-z.\s]+=', queryString):
		# match multiple times:
		matches = re.findall('[ ][a-z.\'\"_]+[ ]?=[ ]?[a-z.\'\"_]+[\n ]?', queryString)
		newQueries = []
		newQueries.append(queryString)
		for match in matches:
			firstPart = match.split("=")[0]
			secondPart = match.split("=")[1]
			newComp = secondPart + '=' + firstPart
			for query in newQueries.copy():
				newQuery = query.replace(match, newComp)
				newQueries.append(newQuery)
		if swapTables:
			## also swap from tables - only FROM A JOIN B		 
			moreNewQueries = []
			for query in newQueries:
#				 if "join" in query:
				matches = re.findall('(from [a-z]+([ ][a-z]+)? (inner )?join [a-z]+ ([a-z]+)?)', query)
				if matches is not None:
					for match in matches:
						match = match[0]
						parts = match.split(' ')
						moreNewQueries.append(query)
						newqueryparts = query.split(match)
						if len(parts) == 4: # from tbla join tblb				
							newquery = newqueryparts[0] + ' from ' + parts[-1] + ' join ' + parts[1] + ' ' + newqueryparts[1]
							moreNewQueries.append(newquery)
						else:
							newquery = newqueryparts[0] + ' from '
							if parts[-1] == 'on':
								newquery = newquery + parts[-2]
							else:
								newquery = newquery + parts[-2] + ' ' + parts[-1]
							if parts[2] == 'inner':
								newquery = newquery + ' inner join' + parts[1]
							elif parts[2] == 'join':
								newquery = newquery + ' join' + parts[1]
							elif parts[3] == 'join':
								newquery = newquery + ' join' + parts[1] + ' ' + parts[2]
							elif parts[3] == 'inner':
								newquery = newquery + ' inner join' + parts[1] + ' ' + parts[2]
							newquery = newquery + ' ' + newqueryparts[1]
							moreNewQueries.append(newquery)
				else:
					moreNewQueries.append(query)
			return moreNewQueries
		else:
			return newQueries
	else:
		return [queryString]


def shuffleWHEREpredicates(queryString):
	if len(re.findall('where(?![`\'\"a-z0-9.,\s_]*\))', queryString)) > 0:
		firstpart = re.split('where(?![`\'\"a-z0-9.,\s_]*\))', queryString)[0] 
		secondpart = re.split('where(?![`\'\"a-z0-9.,\s_]*\))', queryString)[1]
		whereclause = secondpart
		try:
			if len(re.findall('group by(?![`\'\"a-z0-9.,\s_]*\))', queryString)) > 0:
				whereclause = re.split('group by(?![`\'\"a-z0-9.,\s_]*\))', secondpart)[0]
				secondpart = ' group by ' + re.split('group by(?![`\'\"a-z0-9.,\s_]*\))', secondpart)[1]
			elif len(re.findall('order by(?![`\'\"a-z0-9.,\s_]*\))', queryString)) > 0:
				whereclause = re.split('order by(?![`\'\"a-z0-9.,\s_]*\))', secondpart)[0]
				secondpart = ' order by ' + re.split('order by(?![`\'\"a-z0-9.,\s_]*\))', secondpart)[1]
			else:
				secondpart = ''
		except:
			print(queryString)
			print("***********")
		newQueries = []
		newQueries.append(queryString)
		newWhereClause = ''
		if 'between' in whereclause and whereclause.count(' and ') == 2:  ## split on second 'and'
			newWhereClause = 'where' + whereclause.split('and')[-1] + ' and '+ whereclause.split('and')[0] + 'and' + whereclause.split('and')[1]
			newQuery = firstpart + newWhereClause + secondpart
			newQueries.append(newQuery)
		elif 'between' not in whereclause and whereclause.count('and') > 0:
			newWhereClause = 'where' + whereclause.split('and')[-1] + ' and '+ whereclause.split('and')[0]
			newQuery = firstpart + newWhereClause + secondpart
			newQueries.append(newQuery)
		return newQueries
	else:
		return [queryString]		