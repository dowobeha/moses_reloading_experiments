Defined parameters (per moses.ini or switch):
	config: moses.0.d.ini 
	distortion-limit: 4 
	feature: PhrasePenalty UnknownWordPenalty WordPenalty Distortion PhraseDictionaryMemoryPerSentenceOnDemand name=reloading.0.pt num-features=4 tuneable=true input-factor=0 output-factor=0 table-limit=20 valuesAreProbabilities=false InMemoryPerSentenceOnDemandLM name=reloading.0.lm 
	input-factors: 0 
	mapping: 0 T 0 
	server: 
	server-port: 8090 
	verbose: 1 
	weight: PhrasePenalty0= 1 UnknownWordPenalty0= 1 WordPenalty0= -1 Distortion0= 0.2 reloading.0.lm= 0.5 reloading.0.pt= 1 1 1 1 
line=PhrasePenalty
FeatureFunction: PhrasePenalty0 start: 0 end: 0
line=UnknownWordPenalty
FeatureFunction: UnknownWordPenalty0 start: 1 end: 1
line=WordPenalty
FeatureFunction: WordPenalty0 start: 2 end: 2
line=Distortion
FeatureFunction: Distortion0 start: 3 end: 3
line=PhraseDictionaryMemoryPerSentenceOnDemand name=reloading.0.pt num-features=4 tuneable=true input-factor=0 output-factor=0 table-limit=20 valuesAreProbabilities=false
FeatureFunction: reloading.0.pt start: 4 end: 7
line=InMemoryPerSentenceOnDemandLM name=reloading.0.lm
FeatureFunction: reloading.0.lm start: 8 end: 8
Loading PhrasePenalty0
Loading UnknownWordPenalty0
Loading WordPenalty0
Loading Distortion0
Loading reloading.0.lm
Loading reloading.0.pt
RUN SERVER at pid 0
[moses/server/Server.cpp:49] Listening on port 8090
[moses/server/TranslationRequest.cpp:292] Input: ich kaufe sie eine katze
Translating: ich kaufe sie eine katze 
Loading the LM will be faster if you build a binary file.
Reading /tmp/fileoH0Re1
----5---10---15---20---25---30---35---40---45---50---55---60---65---70---75---80---85---90---95--100
****************************************************************************************************
0x1743bc0	LM initialized
Line 0: Collecting options took 0.000 seconds at moses/Manager.cpp Line 141
Line 0: Search took 0.000 seconds
[moses/server/TranslationRequest.cpp:472] BEST TRANSLATION: i buy you a cat [11111]  [total=-67.403] core=(-24.322,0.000,-5.000,0.000,-1.153,-21.674,-3.519,-21.736,0.000)  
[moses/server/TranslationRequest.cpp:292] Input: ich kaufe sie eine katze
Translating: ich kaufe sie eine katze 
Loading the LM will be faster if you build a binary file.
Reading /tmp/file3FUR3r
----5---10---15---20---25---30---35---40---45---50---55---60---65---70---75---80---85---90---95--100
****************************************************************************************************
0x1743b20	LM initialized
Line 0: Collecting options took 0.000 seconds at moses/Manager.cpp Line 141
Line 0: Search took 0.000 seconds
[moses/server/TranslationRequest.cpp:472] BEST TRANSLATION: i buy you a cat [11111]  [total=-81.564] core=(-38.483,0.000,-5.000,0.000,-1.153,-21.674,-3.519,-21.736,0.000)  
[moses/server/TranslationRequest.cpp:292] Input: ich kaufe sie eine katze
Translating: ich kaufe sie eine katze 
Loading the LM will be faster if you build a binary file.
Reading /tmp/fileZsb1VS
----5---10---15---20---25---30---35---40---45---50---55---60---65---70---75---80---85---90---95--100
****************************************************************************************************
0x17edc00	LM initialized
Line 0: Collecting options took 0.000 seconds at moses/Manager.cpp Line 141
Line 0: Search took 0.000 seconds
[moses/server/TranslationRequest.cpp:472] BEST TRANSLATION: i buy you a cat [11111]  [total=-95.725] core=(-52.644,0.000,-5.000,0.000,-1.153,-21.674,-3.519,-21.736,0.000)  
[moses/server/TranslationRequest.cpp:292] Input: ich kaufe sie eine katze
Translating: ich kaufe sie eine katze 
Loading the LM will be faster if you build a binary file.
Reading /tmp/fileq0MwRj
----5---10---15---20---25---30---35---40---45---50---55---60---65---70---75---80---85---90---95--100
****************************************************************************************************
0x1743540	LM initialized
Line 0: Collecting options took 0.000 seconds at moses/Manager.cpp Line 141
Line 0: Search took 0.000 seconds
[moses/server/TranslationRequest.cpp:472] BEST TRANSLATION: i buy you an kitty [11111]  [total=-109.628] core=(-62.351,0.000,-5.000,0.000,1.609,-23.887,-5.493,-24.507,0.000)  
Signal of Class 15 received.  Exiting
