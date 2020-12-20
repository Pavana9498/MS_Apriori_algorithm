# ------------------------------------
# Author: Pavana Doddi
# UIN: 676352041
# ------------------------------------


import sys
import re
import itertools

F_item_sets = []

class Main():

	# Main function.
	def main(self, data_file_path, parameter_file_path):
		obj1 = MSApriori()
		support_count, n, transactionList = obj1.read_transaction(data_file_path)
		items = set(support_count.keys())
		M, sdc = obj1.read_parameters(parameter_file_path, items)
		L, F = obj1.init_pass(M, support_count, n)
		C2 = obj1.C2_gen(L, n, sdc, support_count, M)
		obj1.Fk_gen(C2, transactionList, support_count, n, M, sdc)
		output_file_path = "/Users/pavanadoddi/Desktop/FALL2020/DMTM/Assignment-1/1_2_result.txt"
		obj1.writeOutput(output_file_path)


class MSApriori():

	# Reads the data file and returns the transactions list.
	def read_transaction(self, data_file_path):
		support_count = {}
		transactionList = []
		with open(data_file_path, 'r', encoding = 'utf-8-sig') as data_file:
			transactions = data_file.readlines()
			n = len(transactions)
			for transaction in transactions:
				tID_list = re.sub('[\{\}\s\']', '', transaction).split(',')
				transactionList.append(tID_list)
				for tID in tID_list:
					support_count[tID] = support_count.get(tID,0) + 1
		return support_count, n, transactionList

	# Reads the parameters file and returns the M and sdc
	def read_parameters(self, parameter_file_path, items):
		M = {}
		sdc = 0.0

		with open(parameter_file_path, 'r') as parameter_file:
			parameters = parameter_file.readlines()
			for parameter in parameters:
				if 'MIS' in parameter:
					temp = re.sub('\s','',parameter).split('=')
					ID = re.search('MIS\((.*)\)', temp[0]).group(1)
					if ID in items:
						M[ID] = temp[1]
						items.remove(ID)
					elif ID == 'rest':
						for i in items:
							M[i] = temp[1]
				elif 'SDC' in parameter:
					temp = re.sub('\s','',parameter).split('=')
					sdc = temp[1]
		M = {k:v for k, v in sorted(M.items(), key=lambda item: item[1])}
		return M, sdc,

	# Initial pass to calculate L and F 
	def init_pass(self, M, support_count, n):
		L = []
		F = []
		global F_item_sets
		threshold = next(iter(M.values()))
		for key in M:
			if support_count[key]/n >= float(threshold):
				L.append(key)
			if support_count[key]/n >= float(M[key]):
				F.append(tuple([key]))
				F_item_sets.append(tuple([key]))
		return L, F


	# Generates all the k-level frequent item sets.
	def Fk_gen(self, Ck, transactionList, support_count, n, M, sdc):
		Fk = []
		if len(Ck) != 0:
			for t in transactionList:
				for c in Ck:
					if set(c).issubset(set(t)):
						support_count[c] = support_count.get(c, 0)+1
			for c in Ck:
				if c in support_count and support_count[c]/n >= float(M[c[0]]):
					Fk.append(tuple(c))
					F_item_sets.append(tuple(c))
			Ck = self.Ck_gen(Fk, transactionList, M, support_count, n, sdc)
			self.Fk_gen(Ck, transactionList, support_count, n, M, sdc)


	# Generates all the k-level candidate item sets.
	def Ck_gen(self, Fk_1, transactionList, M, support_count, n, sdc):
		Ck = []
		for l in range(len(Fk_1)-1):
			for h in range(l+1, len(Fk_1)):
				i = 0
				while i < len(Fk_1[l])-1 and Fk_1[l][i] == Fk_1[h][i]:
					i = i+1
				if i == len(Fk_1[l])-1 and abs((support_count[Fk_1[l][i]]/n)-(support_count[Fk_1[h][i]]/n)) <= float(sdc):
					c = Fk_1[l] + tuple([Fk_1[h][-1]])
					subsets = set(itertools.combinations(c, len(c)-1))
					flag = True
					for subset in subsets:
						if c[0] in subset or M[c[0]] == M[c[1]]:
							if tuple(subset) not in Fk_1:
								flag = False
					if flag == True:
						Ck.append(c)
		return Ck

	# Generates 2nd level candidate item sets.
	def C2_gen(self, L, n, sdc, support_count, M):
		C2 = []
		for l in range(len(L)-1):
			if (support_count[L[l]]/n) >= float(M[L[l]]):
				for h in range(l+1, len(L)):
					if (support_count[L[h]]/n) >= float(M[L[l]]) and abs((support_count[L[h]]/n)-(support_count[L[l]]/n)) <= float(sdc):
						C2.append(tuple([L[l], L[h]]))
		return C2

	# Writes the results to output file
	def writeOutput(self, output_file_path):
		global F_item_sets
		output = {}
		if len(F_item_sets) > 0:
			for item_set in F_item_sets:
				if len(item_set) in output:
					l = output[len(item_set)]
					l.append(item_set)
					output[len(item_set)] = l
				else:
					l = [item_set]
					output[len(item_set)] = l
			with open(output_file_path, 'w') as o_file:
				o_file.write("( 76 \n")
				for key in output:
					o_file.write("( Length-{} ".format(key))
					o_file.write("{}\n".format(len(output[key])))
					for item in output[key]:
						o_file.write("\t")
						o_file.write("( ")
						for i in item:
							o_file.write(i)
							o_file.write(" ")
						o_file.write(")")
						o_file.write("\n")
					o_file.write(")\n")
				o_file.write(")\n")
		elif len(F_item_sets) == 0:
			print("There are no frequent itemsets\n")
			with open(output_file_path, 'w') as o_file:
				o_file.write("There are no frequent itemsets\n")		


obj = Main()
data_file_path = sys.argv[1]
parameter_file_path = sys.argv[2]
obj.main(data_file_path, parameter_file_path)