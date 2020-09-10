
class dialogSystem():
	def __init__(self):
		self.sentences = []
		self.sentences_trigger = []
		self.add_sentences()
		self.add_sentences_trigger()

	def add_sentences(self):
		self.sentences.append("Thank you! The test is over!")
		

	def add_sentences_trigger(self):
		self.sentences_trigger.append("I want to know your preference. I will show you 10 popular movies and please tell me whether you like it.")
		self.sentences_trigger.append("Thank you for your help! Please wait for me a little bit.")
		self.sentences_trigger.append("Based on your score, I have understood your preference.")
		self.sentences_trigger.append("Now I will explain your preference.")
		self.sentences_trigger.append("And I'll recommend you 10 movies, please give your opinion.")