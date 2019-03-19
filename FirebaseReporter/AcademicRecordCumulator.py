import pandas as pd
import math

def getActivityAttribute(activityData, attributeName):
    attributeValue = ""
    if attributeName in activityData:
        attributeValue = activityData[attributeName]
    return attributeValue

def gradeIsEmpty(grade):
    return type(grade) == float and math.isnan(grade)

def explodeStudent(studentEntry):
    activityEntries = []
    studentEntryAttrs = studentEntry.to_dict()
    if studentEntryAttrs['qualifier'] == 'guest' or gradeIsEmpty(studentEntryAttrs['grade']):
        return {}
    if 'finished_activities' in studentEntryAttrs and pd.notna(studentEntryAttrs['finished_activities']):
        finishedActivities = studentEntryAttrs.pop('finished_activities')
        for subjectID in finishedActivities:
            activityEntry = studentEntryAttrs
            activityEntry['subject_id'] = subjectID
            for chapterID in finishedActivities[subjectID]:
                activityEntry['chapter_id'] = chapterID
                for activityID in finishedActivities[subjectID][chapterID]:
                    activityEntry['activity_id'] = activityID
                    activityData = finishedActivities[subjectID][chapterID][activityID]
                    activityEntry['data_point'] = getActivityAttribute(activityData, 'data_point')
                    activityEntry['status'] = getActivityAttribute(activityData, 'status')
                    activityEntry['time_stamp'] = getActivityAttribute(activityData, 'time_stamp')
                    activityEntries.append(activityEntry.copy())
    else:
        activityEntries = [studentEntryAttrs]
    return activityEntries

def explodeActivities(classesDF):
    activities = []
    classesDF.rename_axis('student_id').\
        reset_index().\
        apply(lambda studentEntry: activities.extend(explodeStudent(studentEntry)), axis=1)
    return pd.DataFrame(activities)
