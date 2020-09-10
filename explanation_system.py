from quickchart import QuickChart
class explanationSystem():
	def __init__(self, origin_data, release_dates, runtimes, keywords, movie_list):
		self.origin_data = origin_data
		self.release_dates = release_dates
		self.runtimes = runtimes
		self.keywords = keywords
		self.movie_list = movie_list
		self.genres_score = {}
		self.runtimes_score = {}
		self.releaseDate_score = {}
		self.movie_scores = []
		self.HIGH_SCORE = 0
		self.LOW_SCORE = 0
		self.define_vote_scores()
	def define_vote_scores(self):
		vote_scores = sorted([self.origin_data[i][18] for i in range(len(self.origin_data))])
		self.HIGH_SCORE = vote_scores[int(len(vote_scores)*9/10)]
		self.LOW_SCORE = vote_scores[int(len(vote_scores)/10)]
	def explain_important_feat(self, movie_scores):
		self.movie_scores = movie_scores
		genres_dict = {}
		runtimes_dict = {}
		releaseDate_dict = {}
		genres_count = {}
		runtimes_count = {}
		releaseDate_count = {}
		score_pointer = 0
		for movie_id in self.movie_list:
			tmp_score = movie_scores[score_pointer]
			tmp_genres = eval(self.origin_data[movie_id][1])
			for f in tmp_genres:
				if f['name'] not in genres_dict:
					genres_dict[f['name']] = 1
					genres_count[f['name']] = tmp_score - 3
				else:
					genres_dict[f['name']] += 1
					genres_count[f['name']] += tmp_score - 3
			if self.runtimes[movie_id] not in runtimes_dict:
				runtimes_dict[self.runtimes[movie_id]] = 1
				runtimes_count[self.runtimes[movie_id]] = tmp_score - 3
			else:
				runtimes_dict[self.runtimes[movie_id]] += 1
				runtimes_count[self.runtimes[movie_id]] += tmp_score - 3
			if self.release_dates[movie_id] not in releaseDate_dict:
				releaseDate_dict[self.release_dates[movie_id]] = 1
				releaseDate_count[self.release_dates[movie_id]] = tmp_score - 3
			else:
				releaseDate_dict[self.release_dates[movie_id]] += 1
				releaseDate_count[self.release_dates[movie_id]] += tmp_score - 3
			score_pointer += 1
		def calc_variance(dict_total, dict_user):
			# print(dict_total)
			# print(dict_user)
			values = []
			for item in dict_total:
				if item in dict_user:
					value_i = dict_user[item]/dict_total[item]
				else:
					value_i = 0
				values.append(value_i)
			value_sum = sum(values)
			# print(value_sum)
			# print(values)
			average = value_sum/len(values)
			variance = 0
			for i in values:
				variance += pow((i-average),2)
			variance /= len(values)
			# print(variance)
			return variance
		max_variance = 0
		ans = ''
		if calc_variance(genres_dict,genres_count) > max_variance:
			max_variance = calc_variance(genres_dict, genres_count)
			ans = 'genres of movie'
		if calc_variance(runtimes_dict,runtimes_count) > max_variance:
			max_variance = calc_variance(runtimes_dict,runtimes_count)
			ans = 'runtimes of movie'
		if calc_variance(releaseDate_dict,releaseDate_count) > max_variance:
			max_variance = calc_variance(releaseDate_dict,releaseDate_count)
			ans = 'release year of movie'
		if ans == '':
			return ''
		self.genres_score = genres_count
		self.runtimes_score = runtimes_count
		self.releaseDate_score = releaseDate_count
		ans = "You care the feature: " + ans + " most, because your movie preference is influented by this feature most."
		return ans
		# for movie_id in self.movie_list:
		# 	print(str(movie_id) + '   ' + self.origin_data[movie_id][1])
	def get_chart(self, high, low):
		qc = QuickChart()
		qc.width = 500
		qc.height = 300
		qc.device_pixel_ratio = 2.0
		qc.config = {
		  "type": 'pie',
		  "data": {
		    "labels": ['movies get a low score','movies get a high score'],
		    "datasets": [{
		      "data": [low,high]
		    }]
		  },
		  "options": {
		    "plugins": {
		      "datalabels": {
		        "display": True,
		        "align": 'bottom',
		        "backgroundColor": '#ccc',
		        "borderRadius": 3,
		        "font": {
		          "size": 18,
		        }
		      },
		    }
		  }
		}
		return qc.get_url()
	def explain_genres(self):
		ans_list = []
		pic_list = []
		def explan_from_dataset(ans):
			sum1 = 0
			sum2 = 0
			sum3 = 0
			for i in range(len(self.origin_data)):
				for f in eval(self.origin_data[i][1]):
					if f['name'] == genre:
						sum1 += 1
						if self.origin_data[i][18] >= self.HIGH_SCORE:
							sum2 += 1
						elif self.origin_data[i][18] <= self.LOW_SCORE:
							sum3 += 1
			percent1 = round(sum1 / len(self.origin_data) * 100,1)
			percent2 = round(sum2 / sum1 * 100,1)
			percent3 = round(sum3 / sum1 * 100,1)
			ans = ans[:-2] + " And " + str(percent1) + "% of movies have the genre " + genre \
			 + ". In these movies, " + str(percent2) + "% have a high vote score while " + \
			 str(percent3) + "% have a low vote score.\n\n"
			pic = self.get_chart(percent2, percent3)
			return ans,pic
		for genre in self.genres_score:
			has_accident = False
			if self.genres_score[genre] <= -3:
				ans2 = 'You dislike the genre: ' + genre + ', because the movie you dislike: '
				for i in range(len(self.movie_list)):
					movie_id = self.movie_list[i]
					for f in eval(self.origin_data[movie_id][1]):
						if f['name'] == genre and self.movie_scores[i] < 3:
							ans2 = ans2 + self.origin_data[movie_id][17] + ', '
						elif f['name'] == genre and self.movie_scores[i] > 3:
							has_accident = True
				ans2 = ans2[:-2] + ' have this genre.\n\n'
				if has_accident == True:
					ans2 = ans2[:-1] + " But the movie: "
					for i in range(len(self.movie_list)):
						movie_id = self.movie_list[i]
						for f in eval(self.origin_data[movie_id][1]):
							if f['name'] == genre and self.movie_scores[i] > 3:
								ans2 = ans2 + f['name'] + ', '
					ans2 = ans2 + "which you like also have the genre " + genre + '\n\n'
				ans2, pic = explan_from_dataset(ans2)
				ans_list.append(ans2)
				pic_list.append(pic)
			elif self.genres_score[genre] >= 3:
				ans1 = 'You like the genre: ' + genre + ', because the movie you like: '
				has_accident = False
				for i in range(len(self.movie_list)):
					movie_id = self.movie_list[i]
					for f in eval(self.origin_data[movie_id][1]):
						if f['name'] == genre and self.movie_scores[i] > 3:
							ans1 = ans1 + self.origin_data[movie_id][17] + ', '
						elif f['name'] == genre and self.movie_scores[i] < 3:
							has_accident = True
				ans1 = ans1[:-2] + ' have this genre.\n\n'
				if has_accident == True:
					ans1 = ans1[:-1] + " But the movie: "
					for i in range(len(self.movie_list)):
						movie_id = self.movie_list[i]
						for f in eval(self.origin_data[movie_id][1]):
							if f['name'] == genre and self.movie_scores[i] < 3:
								ans1 = ans1 + self.origin_data[movie_id][17]+ ', '
					ans1 = ans1 + "which you dislike also have the genre " + genre + '\n\n'
				ans1, pic = explan_from_dataset(ans1)
				ans_list.append(ans1)
				pic_list.append(pic)
		return ans_list, pic_list
	def explain_releaseDates(self):
		ans_list = []
		pic_list = []
		# print(self.releaseDate_score)
		def explan_from_dataset(ans):
			percent1 = round(sum([1 for x in self.release_dates if x == tag])/len(self.release_dates) * 100, 1)
			percent2 = round(sum([1 for x in range(len(self.origin_data)) if self.origin_data[x][18] >= self.HIGH_SCORE \
				and self.release_dates[x] == tag])/sum([1 for x in self.release_dates if x == tag]) * 100, 1)
			percent3 = round(sum([1 for x in range(len(self.origin_data)) if self.origin_data[x][18] <= self.LOW_SCORE \
				and self.release_dates[x] == tag])/sum([1 for x in self.release_dates if x == tag]) * 100, 1)
			ans = ans[:-2] + ". And " + str(percent1) + "% of movies is released " + tag \
			 + ". In these movies, " + str(percent2) + "% have a high vote score while " + \
			 str(percent3) + "% have a low vote score.\n\n"
			pic = self.get_chart(percent2, percent3)
			return ans, pic
		for tag in self.releaseDate_score:
			if self.releaseDate_score[tag] >= 3:
				ans1 = 'You like the movie released ' + tag + '. Because the movie you like: '
				has_accident = False
				for i in range(len(self.movie_list)):
					movie_id = self.movie_list[i]
					movie_score = self.movie_scores[i]	
					if movie_score > 3 and self.release_dates[movie_id] == tag: 
						ans1 = ans1 + self.origin_data[movie_id][17] + ', ' 
					if movie_score < 3 and self.release_dates[movie_id] == tag:
						has_accident = True
				ans1 = ans1[:-2] + ' is released '+ tag + '.\n'
				if has_accident == True:
					ans1 = ans1[:-2] + ". But the movie: " 
					for i in range(len(self.movie_list)):
						movie_id = self.movie_list[i]
						movie_score = self.movie_scores[i]
						if movie_score < 3 and self.release_dates[movie_id] == tag:
							ans1 = ans1 + self.origin_data[movie_id][17] + ', '
					ans1 = ans1 + "which you dislike is also released " + tag + '\n\n'
				ans1, pic = explan_from_dataset(ans1)
				ans_list.append(ans1)
				pic_list.append(pic)
			if self.releaseDate_score[tag] <= -3:
				ans2 = 'You dislike the movie released ' + tag + '. Because the movie you dislike: '
				has_accident = False
				for i in range(len(self.movie_list)):
					movie_id = self.movie_list[i]
					movie_score = self.movie_scores[i]	
					if movie_score < 3 and self.release_dates[movie_id] == tag: 
						ans2 = ans2 + self.origin_data[movie_id][17] + ', '
					if movie_score > 3 and self.release_dates[movie_id] == tag:
						has_accident = True
				ans2 = ans2[:-2] + ' is released '+ tag + '.\n'
				if has_accident == True:
					ans2 = ans2[:-2] + ". But the movie: "
					for i in range(len(self.movie_list)):
						movie_id = self.movie_list[i]
						movie_score = self.movie_scores[i]	
						if movie_score > 3 and self.release_dates[movie_id] == tag:
							ans2 = ans2 + self.origin_data[movie_id][17] + ', '
					ans2 = ans2 + "which you like is also released " + tag + '\n\n'
				ans2, pic = explan_from_dataset(ans2)
				ans_list.append(ans2)
				pic_list.append(pic)
		return ans_list, pic_list
	def explain_runtimes(self):
		ans_list = []
		pic_list = []
		def explan_from_dataset(ans):
			percent1 = round(sum([1 for time in self.runtimes if time == tag])/len(self.runtimes) * 100, 1)
			percent2 = round(sum([1 for x in range(len(self.origin_data)) if self.origin_data[x][18] >= self.HIGH_SCORE \
				and self.runtimes[x] == tag])/sum([1 for time in self.runtimes if time == tag]) * 100, 1)
			percent3 = round(sum([1 for x in range(len(self.origin_data)) if self.origin_data[x][18] <= self.LOW_SCORE \
				and self.runtimes[x] == tag])/sum([1 for time in self.runtimes if time == tag]) * 100, 1)
			ans = ans + "And " + str(percent1) + "% of movies lasts " + tag \
			 + ". In these movies, " + str(percent2) + "% have a high vote score while " + \
			 str(percent3) + "% have a low vote score.\n"
			pic = self.get_chart(percent2, percent3)
			return ans, pic
		for tag in self.runtimes_score:
			if self.runtimes_score[tag] >= 3:
				has_accident = False
				ans1 = 'You like the movie lasts ' + tag + ' very much. Because the movie you like: '
				for i in range(len(self.movie_list)):
					movie_id = self.movie_list[i]
					movie_score = self.movie_scores[i]	
					if movie_score > 3 and self.runtimes[movie_id] == tag: 
						ans1 = ans1 + self.origin_data[movie_id][17] + ', '
					if movie_score < 3 and self.runtimes[movie_id] == tag:
						has_accident = True
				ans1 = ans1[:-2] + ' last '+ tag + '\n'
				if has_accident == True:
					ans1 = ans1[:-1] + ". But the movie: "
					for i in range(len(self.movie_list)):
						movie_id = self.movie_list[i]
						movie_score = self.movie_scores[i]
						if movie_score < 3 and self.runtimes[movie_id] == tag:
							ans1 = ans1 + self.origin_data[movie_id][17] + ', '
					ans1 = ans1 + "which you dislike also lasts " + tag + '\n'
				ans1, pic = explan_from_dataset(ans1)
				ans_list.append(ans1)
				pic_list.append(pic)
			if self.runtimes_score[tag] <= -3:
				has_accident = False
				ans2 = 'You dislike the movie lasts ' + tag + ' very much. Because the movie you dislike: '
				for i in range(len(self.movie_list)):
					movie_id = self.movie_list[i]
					movie_score = self.movie_scores[i]	
					if movie_score < 3 and self.runtimes[movie_id] == tag: 
						ans2 = ans2 + self.origin_data[movie_id][17] + ', '
					if movie_score > 3 and self.runtimes[movie_id] == tag:
						has_accident = True
				ans2 = ans2[:-2] + ' last '+ tag + '\n'
				if has_accident == True:
					ans2 = ans2 + ". But the movie: "
					for i in range(len(self.movie_list)):
						movie_id = self.movie_list[i]
						movie_score = self.movie_scores[i]
						if movie_score > 3 and self.runtimes[movie_id] == tag:
							ans2 = ans2 + self.origin_data[movie_id][17] + ', '
					ans2 = ans2 + "which you like also lasts " + tag + '\n'
				ans2, pic = explan_from_dataset(ans2)
				ans_list.append(ans1)
				pic_list.append(pic)
		return ans_list, pic_list
	def explain_keywords(self):
		ans1 = ''
		ans2 = ''
		ans_list = []
		keywords_score = {}
		for i in range(len(self.movie_list)):
			movie_id = self.movie_list[i]
			movie_score = self.movie_scores[i]
			for f in eval(self.origin_data[movie_id][4]):
				if f['name'] not in keywords_score:
					keywords_score[f['name']] = movie_score - 3
				else:
					keywords_score[f['name']] += movie_score - 3 
		for keyword in keywords_score:
			if keywords_score[keyword] >= 4:
				ans1 = 'Maybe you like keyword: ' + keyword + ', because the movie you liked: '
				for i in range(len(self.movie_list)):
					movie_id = self.movie_list[i]
					movie_score = self.movie_scores[i]
					if movie_score > 3:
						for f in eval(self.origin_data[movie_id][4]):
							if f['name'] == keyword:
								ans1 = ans1 + self.origin_data[movie_id][17] + ', '
				ans1 = ans1[:-2] + ' have the keyword.\n'
				ans_list.append(ans1)
			elif keywords_score[keyword] <= -4:
				ans2 = 'Maybe you dislike keyword: ' + keyword + ', because the movie you disliked: '
				for i in range(len(self.movie_list)):
					movie_id = self.movie_list[i]
					movie_score = self.movie_scores[i]
					if movie_score < 3:
						for f in eval(self.origin_data[movie_id][4]):
							if f['name'] == keyword:
								ans2 = ans2 + self.origin_data[movie_id][17] + ', '
				ans2 = ans2[:-2] + ' have the keyword.\n'
				ans_list.append(ans2)
		return ans_list

	def explain_movie(self, movie_id):
		ans = '*' + self.origin_data[movie_id][17] + " :* \n" \
			+ "*genre*: "
		for f in eval(self.origin_data[movie_id][1]):
			ans = ans + f['name'] + ', '
		if self.runtimes[movie_id] != []:
			ans = ans + "\n*runtime:* " + self.origin_data[movie_id][13] + " minutes, "
		if self.release_dates[movie_id] != []:
			ans = ans + "\n*released date:* " + self.origin_data[movie_id][11] 
		if self.keywords[movie_id] != []:
			ans = ans + "\n*keywords:* "
			for f in self.keywords[movie_id]:
				ans = ans + f + ', '
		if self.origin_data[movie_id][7] != []:
			ans = ans + "\n*overview:*\n" + self.origin_data[movie_id][7]
		if self.origin_data[movie_id][16] != []:
			ans = ans + "\n*tagline:*\n" + self.origin_data[movie_id][16]
		return ans

