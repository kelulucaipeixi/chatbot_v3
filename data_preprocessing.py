import csv

def read_data():
	f = open('dataset/tmdb.csv','r')
	reader = csv.reader(f)
	header = next(reader)
	origin_data = [line for line in reader]
	return origin_data

def choose_similar_movies(origin_data):
	genres = [eval(line[1]) for line in origin_data]
	# STEP 1  get filted features
	# -------------------------------------------------------------------------------------
	f_dict = {}
	for line in genres:
		for item in line:
			if item['name'] not in f_dict:
				f_dict[item['name']] = 1
			else:
				f_dict[item['name']] += 1
	filter_f_dict = {}
	for f in f_dict:
		# just choose features which occur more than 100 times
		if f_dict[f] > 100:
			filter_f_dict[f] = f_dict[f]
	# print(len(filter_f_dict)) # 17

	# STEP 2  get popularity threshold
	# -------------------------------------------------------------------------------------
	popularity = [float(line[8]) for line in origin_data]
	sorted_pop = sorted(popularity)
	pop_threshold_1 = sorted_pop[int(len(popularity)*0.8)] # take bottom 50% unpopular movies
	pop_threshold_2 = sorted_pop[int(len(popularity)*0.9)] # take top 5% popular movies
	# print(pop_threshold_1)
	# print(pop_threshold_2)
	# STEP 3  get groups list
	# -------------------------------------------------------------------------------------
	f_comb_list = []
	for line in genres:
		tmp_set = set()
		for item in line:
			# remove the feature tag which occur less than 100 times
			if item['name'] in filter_f_dict:
				tmp_set.add(item['name'])
		# at least 2 feature tags of movie is needed
		if tmp_set not in f_comb_list and len(tmp_set) >= 2:
			f_comb_list.append(tmp_set)
	groups_list = [[] for i in range(len(f_comb_list))]
	for i in range(len(genres)):
		line = genres[i]
		tmp_set = set()
		for item in line:
			if item['name'] in filter_f_dict:
				tmp_set.add(item['name'])
		if len(tmp_set) < 2:
			continue
		for j in range(len(f_comb_list)):
			if f_comb_list[j] == tmp_set:
				groups_list[j].append(i)
	groups_list = [x for x in groups_list if len(x) >= 2]
	# print(len(groups_list))

	# STEP 4  filter groups list with runtime and release_date
	# -------------------------------------------------------------------------------------
	runtime = [0 for i in range(len(origin_data))]
	for i in range(len(origin_data)):
		if origin_data[i][13] != '':
			runtime[i] = int(float(origin_data[i][13]))
		else:
			runtime[i] = 0
	runtimes = ['' for i in range(len(origin_data))]
	runtime_tags = ["longer than 2.5 hour","between 2 hour and 2.5 hour","between 1.5 hour and 2 hour","shorter than 1.5 hour","no data"]
	for i in range(len(runtime)):
		if runtime[i] >= 150:
			runtimes[i] = "longer than 2.5 hour" # 179 movies have the tag
		elif runtime[i] >= 120 and runtime[i] < 150: # 894
			runtimes[i] = "between 2 hour and 2.5 hour" 
		elif runtime[i] >= 90 and runtime[i] < 120: # 3023
			runtimes[i] = "between 1.5 hour and 2 hour"
		elif runtime[i] < 90 and runtime[i] != 0: # 670
			runtimes[i] = "shorter than 1.5 hour"
		else:
			runtimes[i] = "no data" # 37
	# count_runtime_tag = [runtimes[i] for i in range(len(runtimes)) if runtimes[i] == 'no data']
	# print(len(count_runtime_tag))
	groups_list_filted_by_runtime = []
	for group in groups_list:
		runtime_tag_dict = {runtime_tags[i]:[] for i in range(len(runtime_tags))}
		for j in group:
			runtime_tag_dict[runtimes[j]].append(j)
		for tag in runtime_tag_dict:
			if len(runtime_tag_dict[tag]) >= 2:
				groups_list_filted_by_runtime.append(runtime_tag_dict[tag])
	# print(len(groups_list_filted_by_runtime))

	release_date = [line[11] for line in origin_data]
	for i in range(len(release_date)):
		if release_date[i] != '':
			release_date[i] = int(release_date[i][:4])
		else:
			release_date[i] = 0
	release_dates = [0 for i in range(len(release_date))]
	for i in range(len(release_date)):
		if release_date[i] >= 2015:
			release_dates[i] = "after 2015" # 321 movies have this tag
		elif release_date[i] < 2015 and release_date[i] >= 2010:
			release_dates[i] = "after 2010 and before 2015" # 1125
		elif release_date[i] < 2010 and release_date[i] >= 2000:
			release_dates[i] = "after 2000 and before 2010" # 2048
		elif release_date[i] < 2000 and release_date[i] >= 1990:
			release_dates[i] = "after 1990 and before 2000" # 778
		elif release_date[i] < 1990 and release_date[i] > 0:
			release_dates[i] = "before 1990" # 530
		else:
			release_dates[i] = "no data" # 1
	# count_releasedata_tag = [i for i in range(len(release_dates)) if release_dates[i] == "before 1990"]
	# print(len(count_releasedata_tag))
	groups_list_filted_by_release_date = []
	for group in groups_list_filted_by_runtime:
		release_date_tag_dict = {"after 2015":[],"after 2010 and before 2015":[],"after 2000 and before 2010":[],"after 1990 and before 2000":[],"before 1990":[],"no data":[]}
		for j in group:
			release_date_tag_dict[release_dates[j]].append(j)
		for tag in release_date_tag_dict:
			if len(release_date_tag_dict[tag]) >= 2:
				groups_list_filted_by_release_date.append(release_date_tag_dict[tag])
	# print(len(groups_list_filted_by_release_date))

	# STEP 5  choose final pairs based on keywords similarity
	# -------------------------------------------------------------------------------------
	keyword = [eval(line[4]) for line in origin_data]
	keyword_dict = {}
	for line in keyword:
		for f in line:
			if f['name'] not in keyword_dict:
				keyword_dict[f['name']] = 1
			else:
				keyword_dict[f['name']] += 1
	# To avoid there are too many keywords (lots of keywords just occur one time which is not 
	# useful for evaluate wheter people understand themselves better), we filter keywords which
	# occur at least 20 times.
	useful_keyword_list = [x for x in keyword_dict if keyword_dict[x] >= 20]
	groups_list_filted_by_keywords = []
	for group in groups_list_filted_by_release_date:
		max_similarity = 0
		tmp_group = [0,0,0]
		for i in range(len(group)-1):
			for j in range(i+1,len(group),1):
				similarity = 0
				x = group[i]
				y = group[j]
				for f1 in keyword[x]:
					for f2 in keyword[y]:
						if f1['name'] == f2['name'] and f1['name']:
							similarity += 1	
				if similarity > max_similarity:
					max_similarity = similarity
					tmp_group = [x,y,similarity]
		groups_list_filted_by_keywords.append(tmp_group)
	sorted_groups_list_filted_by_keywords = sorted(groups_list_filted_by_keywords, key = lambda x:x[2])
	# print(sorted_groups_list_filted_by_keywords)
	# choose movie pairs which have at least 3 same keywords.
	groups_list_filted_by_keywords_threshold = [[x[0],x[1]] for x in sorted_groups_list_filted_by_keywords if x[2] >= 2]
	# print(groups_list_filted_by_keywords_threshold)
	final_groups_list = []
	keywords = [[] for i in range(len(keyword))]
	for i in range(len(keywords)):
		for f in keyword[i]:
			if f['name'] in useful_keyword_list:
				keywords[i].append(f['name'])
	for pair in groups_list_filted_by_keywords_threshold:
		x = float(origin_data[pair[0]][8])
		y = float(origin_data[pair[1]][8])
		if max(x,y) > pop_threshold_2 and min(x,y) < pop_threshold_1:
			if x > y:
				final_groups_list.append([pair[0],pair[1]])
			else:
				final_groups_list.append([pair[1],pair[0]])
	# print(final_groups_list)
	# best_10_groups = []
	# genres_dict = {}
	# for pair in final_groups_list:
	# 	movie_id = pair[0]
	# 	tmp_genres = eval(origin_data[movie_id][1])
	# 	for f in tmp_genres:
	# 		if f['name'] not in genres_dict:
	# 			genres_dict[f['name']] = 1
	# 		else:
	# 			genres_dict[f['name']] += 1
	# print(genres_dict)
	# for pair in final_groups_list:
	# 	movie_id = pair[0]
	# 	tmp_genres = eval(origin_data[movie_id][1])
	# 	for f in tmp_genres:
	# 		if genres_dict[f['name']] <= 4:
	# 			best_10_groups.append(pair)
	# 			break
	# print(best_10_groups)
	#[[128,201],[3169, 4264], [899, 565],[1119, 911],[1027, 1106],[139, 213],[694, 180]]
	# for pair in final_groups_list:
	# 	print(origin_data[pair[0]][8] + '  ' + origin_data[pair[1]][8])

	# STEP 6  choose final pairs based on feature value balance
	# -------------------------------------------------------------------------------------

	# releaseDate_tags_count = {}
	# runtime_tags_count = {}
	# genre_tags_count = {}
	# groups_filted_by_balance_features = []
	# for group in groups_list_filted_by_release_date:
	# 	x = group[0]
	# 	is_continue = False
	# 	if runtimes[x] in runtime_tags_count and runtime_tags_count[runtimes[x]] == 3:
	# 		continue
	# 	if release_dates[x] in releaseDate_tags_count and releaseDate_tags_count[release_dates[x]] == 3:
	# 		continue
	# 	for f in genres[x]:
	# 		if f['name'] in genre_tags_count and genre_tags_count[f['name']] == 3:
	# 			is_continue = True
	# 	if is_continue == True:
	# 		continue
	# 	else:
	# 		if runtimes[x] not in runtime_tags_count:
	# 			runtime_tags_count[runtimes[x]] = 1
	# 		else:
	# 			runtime_tags_count[runtimes[x]] += 1
	# 		if release_dates[x] not in releaseDate_tags_count:
	# 			releaseDate_tags_count[release_dates[x]] = 1
	# 		else:
	# 			releaseDate_tags_count[release_dates[x]] += 1
	# 		for f in genres[x]:
	# 			if f['name'] not in genre_tags_count:
	# 				genre_tags_count[f['name']] = 1
	# 			else:
	# 				genre_tags_count[f['name']] += 1
	# 	groups_filted_by_balance_features.append(group)
	# # print(groups_list_filted_by_release_date)
	# # print(len(groups_list_filted_by_release_date))
	# print(groups_filted_by_balance_features)
	# print(releaseDate_tags_count)
	# print(runtime_tags_count)
	# print(genre_tags_count)
	final_groups_list = final_groups_list[1:]
	# a = {}
	# b = {}
	# c = {}
	# for i in final_groups_list:
	# 	x = i[0]
	# 	if runtimes[x] not in a:
	# 			a[runtimes[x]] = 1
	# 	else:
	# 		a[runtimes[x]] += 1
	# 	if release_dates[x] not in b:
	# 		b[release_dates[x]] = 1
	# 	else:
	# 		b[release_dates[x]] += 1
	# 	for f in genres[x]:
	# 		if f['name'] not in c:
	# 			c[f['name']] = 1
	# 		else:
	# 			c[f['name']] += 1
	# print(a)
	# print(b)
	# print(c)
	for i in final_groups_list:
		print(origin_data[i[0]][17] + '  ' + origin_data[i[1]][17])

	return final_groups_list[:11], release_dates, runtimes, keywords

if __name__ == '__main__':
	origin_data = read_data()
	choose_similar_movies(origin_data)