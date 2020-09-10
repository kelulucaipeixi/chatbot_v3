import csv

reader = csv.reader(open('tmdb.csv','r'))
header = next(reader)
data = [line for line in reader]
keywords = [eval(line[4]) for line in data]
my_dict = {}
for line in keywords:
	for f in line:
		if f['name'] not in my_dict:
			my_dict[f['name']] = 1
		else:
			my_dict[f['name']] += 1
sorted_my_dict = sorted(my_dict.items(), key = lambda x:x[1])
# print(sorted_my_dict)
# print(my_dict)
final_dict = {}
for pair in sorted_my_dict:
	if pair[1] >= 20 and pair[1] <= 150:
		final_dict[pair[0]] = pair[1]
lines = []
for line in keywords:
	count = 0
	for f in line:
		if f['name'] in final_dict:
			count += 1
	if count >= 9:
		lines.append(line)
print(len(lines))



















