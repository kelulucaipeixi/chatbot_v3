from quickchart import QuickChart

qc = QuickChart()
qc.config = {
    "type": 'bar',
		  "data": {
		    "labels": ['movies get a low score','movies get a high score'],
		    "datasets": [{
		      "label": "movies have the feature mentioned above",
		      "data": [1, 79, 100]
		    }]
		  },
		  "options": {
		    "plugins": {
		      "datalabels": {
		        "display": True,
		        "backgroundColor": '#ccc',
		        "borderRadius": 3,
		        "font": {
		          "size": 18,
		        }
		      },
		    }
		  }
}

print(qc.get_short_url())