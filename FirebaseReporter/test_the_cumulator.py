import pandas as pd
import AcademicRecordCumulator

def makeClassesDF():
    return pd.DataFrame(data=[('stid1', '', '1', float('nan')),
                              ('stid2', '', '1', {'English': {'UNIT_9_CHAPTER_DETAILING': {'tab_9^3': {'data_point': '{"timeTakenInSeconds": 95, "maxScore": 7,"score": 7,"questions":[0,0]}', 'status': 'approved', 'time_stamp': '2019-02-21T09:06:26GMT+05:30'}}}}),
                              ('stid3', '', '1', {'English': {'UNIT_9_CHAPTER_DETAILING': {'tab assessment_9^5': {'data_point': '{"timeTakenInSeconds": 164, "MaximumScore": 7,"Actualscore": 0,"No. of errors": 0,"Correct (1),wrong (0),not attempted (n)":[n,n,n,n,n,n,n],"No. of error prompts":0}', 'status': 'assessment_ready', 'time_stamp': '2019-02-19T11:00:42GMT+05:30'}, 'tab_9^3': {'data_point': '{"timeTakenInSeconds": 112, "maxScore": 7,"score": 7,"questions":[0,0]}', 'time_stamp': '2019-02-19T11:16:11GMT+05:30'}}, 'UNIT_9_POEM_DETAILING': {'tab_9^1^1': {'data_point': '{"timeTakenInSeconds": 56,  "maxScore": 0,"score": 0,"questions":[ ]}', 'time_stamp': '2019-02-19T10:52:30GMT+05:30'}}},
                                         'math': {'mathchap1': {'tab 10^1': {'data_point': 'done'}}}
                                        })
                             ],
                        columns=['StudentID', 'qualifier', 'grade', 'finished_activities'])

def givenDF_whenActivityPresent_thenExplodeActivities():
    classesDF = makeClassesDF()
    explodedDF = AcademicRecordCumulator.explodeActivities(classesDF)
    assert(len(explodedDF) >= len(classesDF))


givenDF_whenActivityPresent_thenExplodeActivities()
