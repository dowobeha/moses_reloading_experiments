Defined parameters (per moses.ini or switch):
	config: moses.1.s.ini 
	distortion-limit: 4 
	feature: PhrasePenalty UnknownWordPenalty WordPenalty Distortion KENLM name=static.1.lm factor=0 path=static.lm PhraseDictionaryMemory name=static.1.pt num-features=4 tuneable=true input-factor=0 output-factor=0 path=static.1.pt table-limit=20 
	input-factors: 0 
	mapping: 0 T 0 
	server: 
	server-port: 8081 
	verbose: 1 
	weight: PhrasePenalty0= 1 UnknownWordPenalty0= 1 WordPenalty0= -1 Distortion0= 0.2 static.1.lm= 0.5 static.1.pt= 1 1 1 1 
line=PhrasePenalty
FeatureFunction: PhrasePenalty0 start: 0 end: 0
line=UnknownWordPenalty
FeatureFunction: UnknownWordPenalty0 start: 1 end: 1
line=WordPenalty
FeatureFunction: WordPenalty0 start: 2 end: 2
line=Distortion
FeatureFunction: Distortion0 start: 3 end: 3
line=KENLM name=static.1.lm factor=0 path=static.lm
Loading the LM will be faster if you build a binary file.
Reading static.lm
----5---10---15---20---25---30---35---40---45---50---55---60---65---70---75---80---85---90---95--100
The ARPA file is missing <unk>.  Substituting log10 probability -100.000.
****************************************************************************************************
FeatureFunction: static.1.lm start: 4 end: 4
line=PhraseDictionaryMemory name=static.1.pt num-features=4 tuneable=true input-factor=0 output-factor=0 path=static.1.pt table-limit=20
FeatureFunction: static.1.pt start: 5 end: 8
Loading PhrasePenalty0
Loading UnknownWordPenalty0
Loading WordPenalty0
Loading Distortion0
Loading static.1.lm
Loading static.1.pt
Start loading text phrase table. Moses format : [0.001] seconds
Reading static.1.pt
----5---10---15---20---25---30---35---40---45---50---55---60---65---70---75---80---85---90---95--100
****************************************************************************************************
RUN SERVER at pid 0
[moses/server/Server.cpp:49] Listening on port 8081
[moses/server/TranslationRequest.cpp:292] Input: je vous achète un chat
Translating: je vous achète un chat 
Line 0: Collecting options took 0.000 seconds at moses/Manager.cpp Line 141
Line 0: Search took 0.000 seconds
[moses/server/TranslationRequest.cpp:472] BEST TRANSLATION: i buy you an kitty [11111]  [total=-6.009] core=(3.000,0.000,-5.000,0.000,-9.210,6.802,-7.611,-1.099,-7.497)  
Signal of Class 15 received.  Exiting
