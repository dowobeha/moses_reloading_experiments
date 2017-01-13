Defined parameters (per moses.ini or switch):
	config: moses.1.d.ini 
	distortion-limit: 4 
	feature: PhrasePenalty UnknownWordPenalty WordPenalty Distortion PhraseDictionaryMemoryPerSentenceOnDemand name=DynamicPT1 num-features=4 tuneable=true input-factor=0 output-factor=0 table-limit=20 valuesAreProbabilities=false InMemoryPerSentenceOnDemandLM name=DynamicLM1 
	input-factors: 0 
	mapping: 0 T 0 
	server: 
	server-port: 8084 
	verbose: 1 
	weight: PhrasePenalty0= 1 UnknownWordPenalty0= 1 WordPenalty0= -1 Distortion0= 0.2 DynamicLM1= 0.5 DynamicPT1= 1 1 1 1 
line=PhrasePenalty
FeatureFunction: PhrasePenalty0 start: 0 end: 0
line=UnknownWordPenalty
FeatureFunction: UnknownWordPenalty0 start: 1 end: 1
line=WordPenalty
FeatureFunction: WordPenalty0 start: 2 end: 2
line=Distortion
FeatureFunction: Distortion0 start: 3 end: 3
line=PhraseDictionaryMemoryPerSentenceOnDemand name=DynamicPT1 num-features=4 tuneable=true input-factor=0 output-factor=0 table-limit=20 valuesAreProbabilities=false
FeatureFunction: DynamicPT1 start: 4 end: 7
line=InMemoryPerSentenceOnDemandLM name=DynamicLM1
FeatureFunction: DynamicLM1 start: 8 end: 8
Loading PhrasePenalty0
Loading UnknownWordPenalty0
Loading WordPenalty0
Loading Distortion0
Loading DynamicLM1
Loading DynamicPT1
RUN SERVER at pid 0
[moses/server/Server.cpp:49] Listening on port 8084
Signal of Class 15 received.  Exiting
