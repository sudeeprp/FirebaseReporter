import pandas as pd
import numpy as np
import sys
import os
import json
import AcademicRecordCumulator
import ChapterStatusMapper
import io

def df_to_CSV(df, index_label, CSVDir, csvFilename):
    df.to_csv(os.path.join(CSVDir, csvFilename), encoding='utf-8', index_label=index_label)

def json_to_CSV(jsonObject, index_label, CSVDir, csvFilename):
    df = pd.DataFrame(jsonObject).transpose()
    df_to_CSV(df, index_label, CSVDir, csvFilename)

def jsonStr_to_CSV(jsonStr, index_label, CSVDir, csvFilename):
    json_to_CSV(json.loads(jsonStr), index_label, CSVDir, csvFilename)

def latestActivityTime(lastActivityRecord, activityClassID, activityTime):
    lastActivityTime = ""
    if activityClassID in lastActivityRecord:
        lastActivityTime = lastActivityRecord[activityClassID]
    if activityTime > lastActivityTime:
        latestActivityTimestamp = activityTime
    else:
        latestActivityTimestamp = lastActivityTime
    return latestActivityTimestamp

def activityLogJSONstr_to_CSV(jsonString, CSVDir):
    activities = json.loads(jsonString)
    lastActivityRecord = {}
    for activityID in activities:
        activityClassID = activities[activityID]['class_id']
        activityTime = activities[activityID]['timestamp']
        lastActivityRecord[activityClassID] = latestActivityTime(lastActivityRecord, activityClassID, activityTime)
    latestActivities = []
    for activityClassID in lastActivityRecord:
        latestActivities.append({'classroom_id': activityClassID, 'latestAccess': lastActivityRecord[activityClassID]})
    df_to_CSV(pd.DataFrame(latestActivities), "", CSVDir, 'activity_log.csv')

def getClassStudentsDF(classAssets, classroomID):
    studentsDF = pd.DataFrame(classAssets[classroomID]['students']).transpose()
    nStudents = len(studentsDF)
    studentsDF['classroom_id'] = [classroomID for i in range(nStudents)]
    return studentsDF

def emptyAttendanceEntry(classroomID, studentID):
    return {"classroom_id": classroomID, "studentID": studentID}

def getClassAttendanceDF(classAssets, classroomID):
    attendanceAccumulator = []
    for studentID in classAssets[classroomID]['students']:
        if('attendance' in classAssets[classroomID]):
            for date in classAssets[classroomID]['attendance']:
                attendanceEntry = emptyAttendanceEntry(classroomID, studentID)
                attendanceEntry['date'] = date
                attendanceEntry['presence'] = 0
                for ampm in classAssets[classroomID]['attendance'][date]:
                    if studentID in classAssets[classroomID]['attendance'][date][ampm]:
                        attendanceEntry['presence'] += 1
                attendanceAccumulator.append(attendanceEntry)
        else:
            attendanceAccumulator.append(emptyAttendanceEntry(classroomID, studentID))
    attendanceDF = pd.DataFrame(attendanceAccumulator)
    return attendanceDF

def makeAttendancePivot(attendanceDF):
    return pd.pivot_table(attendanceDF, values='presence', index=['classroom_id'], columns=['date'], aggfunc=np.sum)

def classAssetsJSONstr_to_CSV(jsonString, CSVDir):
    classAssets = json.loads(jsonString)
    classesDF = pd.DataFrame()
    attendanceDF = pd.DataFrame()
    classStudentCounts = []

    for classroomID in classAssets:
        studentsDF = getClassStudentsDF(classAssets, classroomID)
        classStudentCounts.append({"classroom_id": classroomID, "student_count": len(studentsDF)})
        classesDF = classesDF.append(studentsDF)
        attendanceDF = attendanceDF.append(getClassAttendanceDF(classAssets, classroomID))

    json_to_CSV(pd.DataFrame(classStudentCounts).transpose(), "", CSVDir, 'student_count.csv')

    explodedAcaDF = AcademicRecordCumulator.explodeActivities(classesDF)
    json_to_CSV(explodedAcaDF.transpose(), "", CSVDir, 'academics.csv')

    chapterStatusMap = ChapterStatusMapper.mapChapterStatus(explodedAcaDF, CSVDir)
    json_to_CSV(chapterStatusMap.transpose(), "", CSVDir, 'chapstat.csv')

    attendancePivot = makeAttendancePivot(attendanceDF).transpose()
    json_to_CSV(attendancePivot, "", CSVDir, 'attendance.csv')


def classroomsJSONstr_to_CSV(jsonString, CSVDir):
    jsonStr_to_CSV(jsonString, "classroom_id", CSVDir, 'classrooms.csv')

def functionForFile(filename):
    firebaseJSONstrFuncs = {
        'activity_log': activityLogJSONstr_to_CSV,
        'classroom_assets': classAssetsJSONstr_to_CSV,
        'classrooms': classroomsJSONstr_to_CSV
    }
    function = None
    for key in firebaseJSONstrFuncs:
        if key in filename:
            function = firebaseJSONstrFuncs[key]
            break
    return function

def jsonFile_to_CSV(jsonDir, jsonFilename, CSVDir):
    firebaseFileProcessor = functionForFile(jsonFilename)
    if firebaseFileProcessor is not None:
        jsonFile = io.open(os.path.join(jsonDir, jsonFilename), mode='r', encoding='utf-8')
        csvFilename = jsonFilename + '.csv'
        firebaseFileProcessor(jsonFile.read(), CSVDir)
        jsonFile.close()

def jsonDir_to_CSVDir(jsonDir, CSVDir):
    for jsonFilename in os.listdir(jsonDir):
        jsonFile_to_CSV(jsonDir, jsonFilename, CSVDir)

if len(sys.argv) == 3:
    jsonDir_to_CSVDir(jsonDir=sys.argv[1], CSVDir=sys.argv[2])
else:
    print("Usage:\n" + sys.argv[0] + " <dir with firebase json files> <output dir>")