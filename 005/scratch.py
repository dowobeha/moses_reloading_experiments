#!/usr/bin/python3

d={'fvals': ' Distortion0= 0 LM0= -4.60517 PhrasePenalty0= 2 WordPenalty0= -5 TranslationModel0= 1.84305 -6.90162 -0.223144 -5.53713'}

for key, value in d.items():

    if key=='fvals':

        parts=value.strip().split()

        feature=None
        size=0

        for part in parts:

            if part.endswith("="):
                if feature != None:
                    print("{}{}".format(feature,size), end=" ")
                feature=part
                size=0

            else:
                size += 1

                
        if feature != None:
            print("{}{}".format(feature,size))


