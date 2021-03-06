Defined parameters (per moses.ini or switch):
	config: moses.0.d.ini 
	distortion-limit: 4 
	feature: PhrasePenalty UnknownWordPenalty WordPenalty Distortion PhraseDictionaryMemoryPerSentenceOnDemand name=DynamicPT0 num-features=4 tuneable=true input-factor=0 output-factor=0 table-limit=20 valuesAreProbabilities=false InMemoryPerSentenceOnDemandLM name=DynamicLM0 
	input-factors: 0 
	mapping: 0 T 0 
	server: 
	server-port: 8090 
	verbose: 1 
	weight: PhrasePenalty0= 1 UnknownWordPenalty0= 1 WordPenalty0= -1 Distortion0= 0.2 DynamicLM0= 0.5 DynamicPT0= 1 1 1 1 
line=PhrasePenalty
FeatureFunction: PhrasePenalty0 start: 0 end: 0
line=UnknownWordPenalty
FeatureFunction: UnknownWordPenalty0 start: 1 end: 1
line=WordPenalty
FeatureFunction: WordPenalty0 start: 2 end: 2
line=Distortion
FeatureFunction: Distortion0 start: 3 end: 3
line=PhraseDictionaryMemoryPerSentenceOnDemand name=DynamicPT0 num-features=4 tuneable=true input-factor=0 output-factor=0 table-limit=20 valuesAreProbabilities=false
FeatureFunction: DynamicPT0 start: 4 end: 7
line=InMemoryPerSentenceOnDemandLM name=DynamicLM0
FeatureFunction: DynamicLM0 start: 8 end: 8
Loading PhrasePenalty0
Loading UnknownWordPenalty0
Loading WordPenalty0
Loading Distortion0
Loading DynamicLM0
Loading DynamicPT0
RUN SERVER at pid 0
[moses/server/Server.cpp:49] Listening on port 8090
[moses/server/TranslationRequest.cpp:291] Input: ich kaufe sie eine katze
Translating: ich kaufe sie eine katze 
Loading the LM will be faster if you build a binary file.
Reading /tmp/file8113ez
----5---10---15---20---25---30---35---40---45---50---55---60---65---70---75---80---85---90---95--100
****************************************************************************************************
0x2931ac0	LM initialized
Line 0: Collecting options took 0.000 seconds at moses/Manager.cpp Line 141
Line 0: Search took 0.000 seconds
[moses/server/TranslationRequest.cpp:465] BEST TRANSLATION: i buy you a cat [11111]  [total=-1429.843] core=(-1386.761,0.000,-5.000,0.000,-1.153,-21.674,-3.519,-21.736,0.000)  
Signal of Class 15 received.  Exiting
