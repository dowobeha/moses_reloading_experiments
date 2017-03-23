Defined parameters (per moses.ini or switch):
	config: moses.1.d.ini 
	distortion-limit: 4 
	feature: PhrasePenalty UnknownWordPenalty WordPenalty Distortion PhraseDictionaryMemoryPerSentenceOnDemand name=reloading.1.pt num-features=4 tuneable=true input-factor=0 output-factor=0 table-limit=20 valuesAreProbabilities=false InMemoryPerSentenceOnDemandLM name=reloading.1.lm 
	input-factors: 0 
	mapping: 0 T 0 
	server: 
	server-port: 8091 
	verbose: 1 
	weight: PhrasePenalty0= 1 UnknownWordPenalty0= 1 WordPenalty0= -1 Distortion0= 0.2 reloading.1.lm= 0.5 reloading.1.pt= 1 1 1 1 
line=PhrasePenalty
FeatureFunction: PhrasePenalty0 start: 0 end: 0
line=UnknownWordPenalty
FeatureFunction: UnknownWordPenalty0 start: 1 end: 1
line=WordPenalty
FeatureFunction: WordPenalty0 start: 2 end: 2
line=Distortion
FeatureFunction: Distortion0 start: 3 end: 3
line=PhraseDictionaryMemoryPerSentenceOnDemand name=reloading.1.pt num-features=4 tuneable=true input-factor=0 output-factor=0 table-limit=20 valuesAreProbabilities=false
FeatureFunction: reloading.1.pt start: 4 end: 7
line=InMemoryPerSentenceOnDemandLM name=reloading.1.lm
FeatureFunction: reloading.1.lm start: 8 end: 8
Loading PhrasePenalty0
Loading UnknownWordPenalty0
Loading WordPenalty0
Loading Distortion0
Loading reloading.1.lm
Loading reloading.1.pt
RUN SERVER at pid 0
[moses/server/Server.cpp:49] Listening on port 8091
[moses/server/TranslationRequest.cpp:292] Input: je vous achète un chat
Translating: je vous achète un chat 
Loading the LM will be faster if you build a binary file.
Reading /tmp/filecS6NVh
----5---10---15---20---25---30---35---40---45---50---55---60---65---70---75---80---85---90---95--100
****************************************************************************************************
0x1f1baa0	LM initialized
Line 0: Collecting options took 0.000 seconds at moses/Manager.cpp Line 141
Line 0: Search took 0.000 seconds
[moses/server/TranslationRequest.cpp:472] BEST TRANSLATION: i buy you an kitty [11111]  [total=-24.430] core=(-20.026,0.000,-5.000,0.000,6.802,-7.611,-1.099,-7.497,0.000)  
[moses/server/TranslationRequest.cpp:292] Input: je vous achète un chat
Translating: je vous achète un chat 
Loading the LM will be faster if you build a binary file.
Reading /tmp/filer7eajf
----5---10---15---20---25---30---35---40---45---50---55---60---65---70---75---80---85---90---95--100
****************************************************************************************************
0x1f9e0a0	LM initialized
Line 0: Collecting options took 0.000 seconds at moses/Manager.cpp Line 141
Line 0: Search took 0.000 seconds
[moses/server/TranslationRequest.cpp:472] BEST TRANSLATION: i buy you an kitty [11111]  [total=-35.943] core=(-31.539,0.000,-5.000,0.000,6.802,-7.611,-1.099,-7.497,0.000)  
[moses/server/TranslationRequest.cpp:292] Input: je vous achète un chat
Translating: je vous achète un chat 
Loading the LM will be faster if you build a binary file.
Reading /tmp/filez46zJc
----5---10---15---20---25---30---35---40---45---50---55---60---65---70---75---80---85---90---95--100
****************************************************************************************************
0x1fa1960	LM initialized
Line 0: Collecting options took 0.000 seconds at moses/Manager.cpp Line 141
Line 0: Search took 0.000 seconds
[moses/server/TranslationRequest.cpp:472] BEST TRANSLATION: i buy you an kitty [11111]  [total=-47.456] core=(-43.052,0.000,-5.000,0.000,6.802,-7.611,-1.099,-7.497,0.000)  
[moses/server/TranslationRequest.cpp:292] Input: je vous achète un chat
Translating: je vous achète un chat 
Loading the LM will be faster if you build a binary file.
Reading /tmp/filetaCoda
----5---10---15---20---25---30---35---40---45---50---55---60---65---70---75---80---85---90---95--100
****************************************************************************************************
0x1f9e360	LM initialized
Line 0: Collecting options took 0.000 seconds at moses/Manager.cpp Line 141
Line 0: Search took 0.000 seconds
[moses/server/TranslationRequest.cpp:472] BEST TRANSLATION: i buy you an kitty [11111]  [total=-58.969] core=(-54.565,0.000,-5.000,0.000,6.802,-7.611,-1.099,-7.497,0.000)  
Signal of Class 15 received.  Exiting
