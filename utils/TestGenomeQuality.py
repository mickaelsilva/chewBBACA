#!/usr/bin/env python
import csv
import numpy as np
from numpy import array
import argparse
from collections import OrderedDict
import Counter
import time
import plotly
import plotly.graph_objs as go

def presAbs (d2c):	

	print "generating presence abscence matrix"
	#genelist= d2[:1,1:]
	#print "Warning: all profiles must have same length"
	#for item in d2c:
		#print "genome "+str(item[0])+" has a profile length of "+str(len(item))
	geneslist= d2c[:1,:]
	genomeslist= d2c[1:,:1]
	
	#d2c = d2c[1:,:]
	
	row=1
	while row<d2c.shape[0]:
		column=1
		while column<d2c.shape[1]:
			try:

				aux=int(d2c[row,column])
				if aux>0:
					d2c[row,column]=1
				else :
					d2c[row,column]=0
			except:
				try:
					aux=str((d2c[row,column])).replace ("INF-","")
					aux=int(aux)
					d2c[row,column]=1
				except Exception as e:
					d2c[row,column]=0
				
			column+=1
		row+=1
	print "done"
	
	return d2c

# function to report the most problematic locus/genomes and report the number of good locus by % of genomes
# a list of genomes with a sum of problems higher than the given ythreshold will be returned
def presence3(d2,ythreshold,vector,abscenceMatrix):
	print "checking loci with missing data ..."
	d2d=d2
	
	genomeslist= d2d[1:,:1]
	geneslist = d2d[0]
	
	#d2d = d2d[1:,1:]
	
	column=1
	totals=[]
	allbadgenomes=[]
	reallybadgenomes=[]
	allverygood=[]
	allverybad=[]
	plus95=0
	plus99=0
	plus995=0
	badGenomesScoreDict={}
	listgenes2show=[]
	
	# if a locus has one problematic call, check how many genomes have problem in that call
	
	while column<d2d.shape[1]:
		row=1
		notfound=0
		badgenomes=[]
		while row<d2d.shape[0]:
			
			if not abscenceMatrix:
				
				if  "LNF" in d2d[row,column] or d2d[row,column] =="NIPH" or "LOT" in d2d[row][column]  or "ALM" in d2d[row][column]  or "ASM" in d2d[row][column] or "ABM" in d2d[row][column] or "ERROR" in d2d[row][column] or "undefined" in d2d[row][column] or "small match" in d2d[row][column] or "allele incomplete" in d2d[row][column]:	

				#if d2d[row,column] == "LNF" :
					d2d[row,column]=0
					notfound+=1
					badgenomes.append(row-1)
					
				else:
					d2d[row,column]=1
					pass
			else:
				if int(d2d[row,column]) == 0:
					notfound+=1
					badgenomes.append(row-1)
					
				else:
					d2d[row,column]=1
					pass
				
			
				
			row+=1
		
		value=float(d2d.shape[0]-notfound)/float(d2d.shape[0])
		
		
			
		if len(genomeslist)>500:
			xthreshold=0.95
		elif len(genomeslist)>200:
			xthreshold=0.95
		else:
			xthreshold=0.95

		if value>xthreshold:
			listgenes2show.append(geneslist[column])


		if(value>xthreshold and value<1):
			for badgenome in badgenomes:
				allbadgenomes.append((genomeslist[int(badgenome)])[0])
		elif value==1:
			allverygood.append(geneslist[column])
		elif value==0:
			allverybad.append(geneslist[column])
		if value>=0.95:
			plus95+=1
		if value>=0.99:
			plus99+=1
		if value>=0.995:
			plus995+=1

		totals.append(float(float(d2d.shape[0]-notfound)/float(d2d.shape[0])))
		column+=1
	
	counter=Counter.Counter(allbadgenomes)
	
	
	for elem in counter.most_common():
		if int(elem[1])>ythreshold:
				reallybadgenomes.append((elem)[0])

	print
	print "number genes in 100% genomes: " +str(len(allverygood))
	print "number genes above 99%: " +str(plus99)
	print "number genes above 95%: " +str(plus95)
	print "number genes above 99.5%: " +str(plus995)
	print "number genes in 0% genomes: " +str(len(allverybad))
	print len (totals)
	
	
	
	d2d=d2d.T
	
	
	#number of used genomes
	vector[0].append(len(genomeslist))
	
	#number of loci at 95%
	vector[1].append(plus95)
	
	#number of loci at 99%
	vector[2].append(plus99)
	
	#number of loci at 100%
	vector[6].append(len(allverygood))
	
	#number of loci at 0%
	vector[4].append(len(allverybad))
	
	#number of to be removed genomes%
	try:
		vector[5].append(len(reallybadgenomes)+((vector[5])[-1]))
	except:
		vector[5].append(len(reallybadgenomes))
	
		#number of loci at 99.5%
	vector[3].append(plus995)
	
	print "checked loci with missing data"
	
	return d2d,reallybadgenomes,vector,True,listgenes2show
	#~ return d2d,reallybadgenomes,vector,True
	

	
def removegenomes(d2a,bagenomeslist):
	
	rowid=1
	deleted=0
	genomesList= (d2a[1:,:1]).tolist()
	
	print len(genomesList)
	print len(bagenomeslist)
	print "removing genomes..."
	badgenomeslist2=[]
	for elem in bagenomeslist:
		badgenomeslist2.append(elem)
	
	if len(bagenomeslist)>0:
		i=0
		for genome in genomesList:
			i+=1
			if genome[0] in badgenomeslist2:
				d2a=np.delete(d2a, i, axis=0)
				deleted+=1
				i-=1

	print "genomes removed"
	print d2a.shape
	return d2a


def clean (d2,iterations,ythreshold):
	
	
	abscencematrix=True	
	
	i=0
	removedlistgenomes=[]
	toremovegenomes=[]
	
	statsvector=[[] for x in range(7)]
	
	#run a function that gives information about the usable locus and the possible bad genomes
	lastremovedgenomesCount=0
	iterationStabilizedat=None
	isStable=False
	listgenes2show=[]
	listgenes2showtotal=[]
	
	while i<=iterations:
		
		
		for elem in toremovegenomes:
			removedlistgenomes.append(elem)

		if len(removedlistgenomes)>lastremovedgenomesCount and i >0:
			lastremovedgenomesCount=len(removedlistgenomes)
		elif iterationStabilizedat is None and i >0:
			iterationStabilizedat=i
			print "stabilized at "+str(i)
			isStable=True
			listgenes2showtotal.append(listgenes2show)
		if not isStable:
			print "\n########## ITERATION NUMBER %s  ##########  \n" % str(i)
			print "total removed genomes :" +str(len(removedlistgenomes))
			d2=removegenomes(d2,toremovegenomes)
			matrix3,toremovegenomes,statsvector,abscencematrix,listgenes2show=presence3(d2,ythreshold,statsvector,abscencematrix)
			#~ matrix3,toremovegenomes,statsvector,abscencematrix=presence3(d2,ythreshold,statsvector,abscencematrix)
		
		else:
			for vector in statsvector:
				vector.append(vector[-1])
		
		i+=1
		
		
	with open("removedGenomes.txt", "a") as f:
		f.write("using a threshold of "+ str(ythreshold)+" at iteration number " +str(i)+"\n")
		
		for x in removedlistgenomes:
			f.write(x+"\n")
	
	with open("Genes_95%.txt", "a") as f:
		f.write("using a threshold of "+ str(ythreshold)+"\n")
		
		for x in listgenes2showtotal:
				
			#~ f.write(str(x)+"\n")
			f.write(('\t'.join(map(str,x)))+"\n")
	
	return statsvector,iterationStabilizedat

def main():

	parser = argparse.ArgumentParser(description="This program analyze an allele call raw output matrix, returning info on which genomes are responsible for cgMLST loci loss")
	parser.add_argument('-i', nargs='?', type=str, help='raw allele call matrix file', required=True)
	parser.add_argument('-n', nargs='?', type=int, help='maximum number of iterations', required=True)
	parser.add_argument('-t', nargs='?', type=int, help='maximum threshold of bad calls above 99%', required=True)
	parser.add_argument('-s', nargs='?', type=int, help='step between each threshold analysis', required=True)
	
	args = parser.parse_args()

	
	pathOutputfile = args.i
	iterationNumber=int(args.n)
	thresholdBadCalls=int(args.t)
	step=int(args.s)
	
	starttime="\nStarting Script at : "+time.strftime("%H:%M:%S-%d/%m/%Y")
		
	allresults=[]
	threshold=0
	thresholdlist=[]
	listStableIter=[]
	
	#for each threshold run a clean function on the dataset, using the previous run output (to be removed genomes) as input for the new one
	
	print "will try to open file..."
	#d2=np.loadtxt(inputfile, delimiter='\t')
	d2original = np.genfromtxt(pathOutputfile, delimiter='\t', dtype=None)
	d2copy=np.copy(d2original)
	#create abscence/presence matrix for easier processing
	d2copy=presAbs(d2copy)
	print "file was read"
	
	
	while threshold<thresholdBadCalls:
		
		thresholdlist.append(threshold)
		print "########## USING A THRESHOLD AT " +str(threshold) + " ########"
		result,stabilizedIter=clean(d2copy,iterationNumber,threshold)
		listStableIter.append(stabilizedIter)
		allresults.append(result)
		
		threshold+=step
		
	
	x=list(range(0,len(allresults)))
	

	i=0
	
	
	labels=["number of genomes",
	"Number of Loci present in 95% genomes",
	"Number of Loci present in 99% genomes",
	"Number of Loci present in 99.5% genomes",
	#"Number of Loci present in 0% genomes",
	#"Selected genomes to be removed",
	"Number of Loci present in 100% genomes"]
		
	i=iterationNumber
	while i<=iterationNumber:
		threshindex=0
		
		aux2=[]
		for resultPerThresh in allresults:
			aux=[]
			
			for result in resultPerThresh:
				aux.append(result[i])
			aux2.append(aux)
			
		d2=np.asarray(aux2)
			
		d2=d2.T
		linenmbr=0

		d2 = np.delete (d2,(4), axis=0)
		d2 = np.delete (d2,(4), axis=0)
		
		
		listtraces=[]
		for line in d2:
			
			if(linenmbr==0):
				trace = go.Scatter(
							x = thresholdlist,
							y = line,
							name = "Number of genomes used",
							mode = 'lines+markers',
							yaxis='y2',
							marker = dict(symbol = 'diamond-dot',size = 10)
							
						)
				
				
			else:	
				trace = go.Scatter(
							x = thresholdlist,
							name = labels[linenmbr],
							mode = 'lines+markers',
							y = line,
							marker = dict(symbol = 'star-dot',size = 10),
							line = dict(dash = 'dash')
						)
				
			listtraces.append(trace)	
			linenmbr+=1
		
		layout = go.Layout(
					title='Test genomes quality',
					xaxis=dict(
						title='Threshold'
					),
					yaxis=dict(
						title='Number of loci'
					),
					yaxis2=dict(
						title='Number of genomes',
						#~ titlefont=dict(
							#~ color='rgb(148, 103, 189)'
						#~ ),
						#~ tickfont=dict(
							#~ color='rgb(148, 103, 189)'
						#~ ),
						overlaying='y',
						side='right'
					)
				)
		
		
		fig = go.Figure({"data":listtraces,"layout":layout})
		plot_url = plotly.offline.plot(fig, filename='GenomeQualityPlot')

		i+=1
		
	
	i=0
	for stableiter in listStableIter:
		
		print "At threshold "+str(thresholdlist[i]) + " it stabilized at the iteration number "+str(stableiter)
		i+=1
		
	print (starttime)
	print ("Finished Script at : "+time.strftime("%H:%M:%S-%d/%m/%Y"))
	
	
		
if __name__ == "__main__":
	main()
