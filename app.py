from data_preprocessing import read_data, choose_similar_movies
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from flask import Flask, request
import os
import json
import time
from user_model import userModel
from dialog_system import dialogSystem
from explanation_system import explanationSystem
from quickchart import QuickChart
IS_BASELINE = False
origin_data = read_data()
choiced_pairs, release_dates, runtimes, keywords = choose_similar_movies(origin_data)
movie_list = [x[0] for x in choiced_pairs]
um = userModel()
es = explanationSystem(origin_data, release_dates, runtimes, keywords, movie_list)
ds = dialogSystem()

chatbot_id = 'U01556TH79A'
# chatbot_id = 'U0188FRH2J1'

app = Flask(__name__)
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events",app)

json_file1 = open('json/preference_extractor.json','r')
json_file2 = open('json/recommendation_maker.json','r')
json_file3 = open('json/explanation_header.json','r')
json_file4 = open('json/divider.json','r')
json_file5 = open('json/confirm_button.json','r')
json_file6 = open('json/chart.json','r')
json_file7 = open('json/movie_cover.json','r')
preference_extractor = json.load(json_file1)
recommendation_maker = json.load(json_file2)
explanation_header = json.load(json_file3)
divider = json.load(json_file4)
confirm_button = json.load(json_file5)
chart = json.load(json_file6)
movie_cover = json.load(json_file7)
preference_extractor_pointer = 0
recommendation_maker_pointer = 0
explanation_sender_pointer = 0
# system will send some sentences default.
def send_sentences(sentence):
	slack_web_client.chat_postMessage(
			channel = um.channel_id,
			text = sentence)

def init_preference_extractor():
	movie_id = choiced_pairs[preference_extractor_pointer][0]
	preference_extractor[1]['text']['text'] = es.explain_movie(movie_id)
	preference_extractor[1]['accessory']['image_url'] = movie_cover[preference_extractor_pointer]

# send blocks of movie information to acquire user preference
def get_preference():
	init_preference_extractor()
	slack_web_client.chat_postMessage(
            channel = um.channel_id,
            blocks = preference_extractor)

def init_recommendation_maker():
	movie_id = choiced_pairs[recommendation_maker_pointer][1]
	# recommendation_maker[0]['text']['text'] = es.explain_movie(movie_id)
	recommendation_maker[1]['text']['text'] = es.explain_movie(movie_id)
	recommendation_maker[1]['accessory']['image_url'] = movie_cover[preference_extractor_pointer + 1 + recommendation_maker_pointer]
# send blocks of recommendation to user
def send_recommendation():
	init_recommendation_maker()
	slack_web_client.chat_postMessage(
           	channel = um.channel_id,
           	blocks = recommendation_maker)
def send_divider():
	slack_web_client.chat_postMessage(
           	channel = um.channel_id,
           	blocks = divider)
def send_chart():
	if explanation_sender_pointer == 1:
		url = genre_pic[genre_sender_pointer]
	elif explanation_sender_pointer == 2:
		url = releaseDate_pic[releaseDate_sender_pointer]
	elif explanation_sender_pointer == 3:
		url = runtime_pic[runtime_sender_pointer]
	chart[0]['image_url'] = url
	chart[0]['title']['text'] = "chart"
	slack_web_client.chat_postMessage(
		channel = um.channel_id,
		blocks = chart)
def send_header():
	slack_web_client.chat_postMessage(
			channel = um.channel_id,
			blocks = explanation_header)
def send_confirm_button():
	slack_web_client.chat_postMessage(
			channel = um.channel_id,
			blocks = confirm_button)
genre_sender_pointer = 0
runtime_sender_pointer = 0
releaseDate_sender_pointer = 0
keyword_sender_pointer = 0
import_feat_explanation = []
genre_explanation = []
releaseDate_explanation = []
runtime_explanation = []
keyword_explanation = []
genre_pic = []
releaseDate_pic = []
runtime_pic = []
def get_explanations1():
	global import_feat_explanation
	global genre_explanation
	global genre_pic
	import_feat_explanation = es.explain_important_feat(um.movie_scores)
	genre_explanation, genre_pic = es.explain_genres()
def get_explanations2():
	global releaseDate_explanation
	global runtime_explanation
	global keyword_explanation
	global releaseDate_pic
	global runtime_pic
	releaseDate_explanation, releaseDate_pic = es.explain_releaseDates()
	runtime_explanation, runtime_pic = es.explain_runtimes()
	keyword_explanation = es.explain_keywords()
def send_explanations():
	global explanation_sender_pointer
	if IS_BASELINE == False:
		def send(x):
			if x != '' and x != '\n':
				send_sentences(x)
		def send_genre(x):
			global genre_sender_pointer
			global explanation_sender_pointer
			if genre_sender_pointer < len(genre_explanation):
				send(x[genre_sender_pointer])
				send_chart()
				genre_sender_pointer += 1
				send_confirm_button()	
			else:	
				explanation_sender_pointer = 2
		def send_releaseDate(x):
			global releaseDate_sender_pointer
			global explanation_sender_pointer
			if releaseDate_sender_pointer < len(releaseDate_explanation):
				send(x[releaseDate_sender_pointer])
				send_chart()
				releaseDate_sender_pointer += 1
				send_confirm_button()
			else:
				explanation_sender_pointer = 3
		def send_runtime(x):
			global runtime_sender_pointer
			global explanation_sender_pointer
			if runtime_sender_pointer < len(runtime_explanation):
				send(x[runtime_sender_pointer])
				send_chart()
				runtime_sender_pointer += 1
				send_confirm_button()
			else:
				explanation_sender_pointer = 4
		def send_keyword(x):
			global keyword_sender_pointer
			global explanation_sender_pointer
			if keyword_sender_pointer < len(keyword_explanation):
				send(x[keyword_sender_pointer])
				keyword_sender_pointer += 1
				send_confirm_button()
			else:
				explanation_sender_pointer = 5

		if explanation_sender_pointer == 0:
			global import_feat_explanation
			if import_feat_explanation != '':
				send(import_feat_explanation)
				explanation_sender_pointer = 1
				send_confirm_button()
				return
			else:
				explanation_sender_pointer = 1

		if explanation_sender_pointer == 1:
			global genre_explanation
			send_genre(genre_explanation)

		if explanation_sender_pointer == 2:
			global releaseDate_explanation
			send_releaseDate(releaseDate_explanation)

		if explanation_sender_pointer == 3:
			global runtime_explanation
			send_runtime(runtime_explanation)

		if explanation_sender_pointer == 4:
			global keyword_explanation
			send_keyword(keyword_explanation)

		if explanation_sender_pointer == 5:
			send_sentences(ds.sentences_trigger[4])
	else:
		send_sentences("Good sense! Actually my preference is similar to you. \nAnd I'm very happy to know you. \nAlright I have analysed your preference and have a basic understand of you.")
		send_sentences(ds.sentences_trigger[4])

@slack_events_adapter.on("message")
def handle_message(event_data):
	message = event_data["event"]
	text = message.get('text')
	if um.user_id == '':
		um.user_id = message.get('user')
		um.channel_id = message.get('channel')

	if text in ds.sentences:
		pass
	elif text in ds.sentences_trigger:
		if text == ds.sentences_trigger[0]:
			get_preference()
		elif text == ds.sentences_trigger[1]:
			get_explanations1()
			send_sentences(ds.sentences_trigger[2])
		elif text == ds.sentences_trigger[2]:
			get_explanations2()
			send_sentences(ds.sentences_trigger[3])
		elif text == ds.sentences_trigger[3]:
			send_explanations()
		elif text == ds.sentences_trigger[4]:
			send_recommendation()
	elif message.get("subtype") is None and message['user'] == um.user_id:
		send_sentences(ds.sentences_trigger[0])
		

@app.route("/slack/message_actions",methods=['POST'])
def message_actions():
	global preference_extractor_pointer
	global recommendation_maker_pointer
	form_json = json.loads(request.form['payload'])
	# if 'callback_id' in form_json and form_json['callback_id'] == 'preference_extractor':
	# 	value = form_json['actions'][0]['value']
	# 	movie_id = choiced_pairs[preference_extractor_pointer][0]
	# 	movie_name = origin_data[movie_id][17]
	# 	ans = movie_name + " : " + form_json['original_message']['attachments'][0]['actions'][int(value)-1]['text']
	# 	um.movie_scores.append(int(form_json['original_message']['attachments'][0]['actions'][int(value)-1]['value']))
	# 	if preference_extractor_pointer < 2:
	# 		preference_extractor_pointer += 1
	# 		get_preference()
	# 	else:
	# 		send_sentences(ds.sentences_trigger[1])
	# 	print(um.movie_scores)
	# 	return ans
	# elif 'callback_id' in form_json and form_json['callback_id'] == 'recommendation_maker':
	# 	value = form_json['actions'][0]['selected_options'][0]['value']
	# 	value_int = int(value[0])
	# 	um.movie_scores_2.append(value_int)
	# 	movie_id = choiced_pairs[recommendation_maker_pointer][1]
	# 	movie_name = origin_data[movie_id][17]
	# 	ans = movie_name + ':  ' + value
	# 	if recommendation_maker_pointer < 2:
	# 		recommendation_maker_pointer += 1
	# 		send_recommendation()
	# 	else:
	# 		send_sentences(ds.sentences[-1])
	# 	print("score2: ",um.movie_scores_2)
	# 	return ans
	if 'actions' in form_json and form_json['actions'][0]['action_id'][:20] == 'preference_extractor':
		ans = form_json['actions'][0]['value']
		um.movie_scores.append(int(ans))
		if preference_extractor_pointer < 10:
			preference_extractor_pointer += 1
			get_preference()
		else:
			send_sentences(ds.sentences_trigger[1])
		print("score: ",um.movie_scores)
		return ans
	elif 'actions' in form_json and form_json['actions'][0]['action_id'][:20] == 'recommendation_maker':
		ans = form_json['actions'][0]['value']
		um.movie_scores_2.append(int(ans))
		if recommendation_maker_pointer < 10:
			recommendation_maker_pointer += 1
			send_recommendation()
		else:
			send_sentences(ds.sentences[-1])
		print("score2: ",um.movie_scores_2)
		return ans
	elif 'actions' in form_json and form_json['actions'][0]['action_id'] == 'confirm_button':
		ans = form_json['actions'][0]['value']
		send_explanations()
		return ans
	else:
		print(form_json)
		print(form_json.keys())
		print(form_json[elements])


if __name__ == '__main__':
	app.run(port = 3000)
	# print(um.movie_scores)
	# es.explain_important_feat(um.movie_scores)
	# print(es.explain_genres())