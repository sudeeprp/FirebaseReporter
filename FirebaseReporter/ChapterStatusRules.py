import json
import os
import io
import sys
import pandas as pd
import dbInterpreter

def nextChapterID(chaptersArray, currentChapterIndex):
    nextChapterIndex = currentChapterIndex + 1
    if nextChapterIndex < len(chaptersArray):
        return chaptersArray[nextChapterIndex]["chapter_id"]
    else:
        return "_never_completes"

def deriveChapterRulesAndActivities(grade_subject, subjectDescriptorJsonstr):
    chapterRules = {}
    activityList = []
    chaptersActivities = json.loads(subjectDescriptorJsonstr)
    statusRulesOfChapters = []
    for chapterIndex, chapterDescr in enumerate(chaptersActivities):
        chapterRule = {}
        singleLineChapName = chapterDescr["chapter_name"].replace('\n', ' ')
        chapterRule["chapter_name"] = singleLineChapName
        chapterRule["chapter_id"] = chapterDescr["chapter_id"]
        activitiesForCompletion = []
        for activityDescr in chapterDescr["activities"]:
            activityList.append({"grade_subject": grade_subject, "chapter_name": singleLineChapName, "chapter_id": chapterDescr["chapter_id"], "activity_id": activityDescr})
            if chapterDescr["activities"][activityDescr]["mandatory"] == True:
                activitiesForCompletion.append(activityDescr.replace('.', '^'))
        rulesToDetermineStatus = []
        statusRule = {"chapter_status": "complete"}
        if len(activitiesForCompletion) > 0:
            statusRule["activity_ids"] = activitiesForCompletion
            statusRule["status_required"] = "approved"
        else:
            statusRule["chapter_ids"] = [nextChapterID(chaptersActivities, chapterIndex)]
            statusRule["status_required"] = "_present"
        rulesToDetermineStatus.append(statusRule)
        chapterRule["status_rules"] = rulesToDetermineStatus
        statusRulesOfChapters.append(chapterRule)
    chapterRules[grade_subject.lower()] = statusRulesOfChapters
    return chapterRules, activityList

def writeChapterActivities(activitiesDF, outputDir):
    dbInterpreter.splitGradeAndSubject(activitiesDF).to_csv(os.path.join(outputDir, 'activities_list.csv'))

def deriveRules(curriculumDir, outputDir):
    CHAPTER_DESCRIPTOR_FILE = "chapter_activities.json"
    subdirPaths = [entry for entry in os.listdir(curriculumDir) if os.path.isdir(os.path.join(curriculumDir, entry))]
    chapterStatusRules = {}
    activities = []
    for subdir in subdirPaths:
        subjectDescrFile = os.path.join(os.path.join(curriculumDir, subdir), CHAPTER_DESCRIPTOR_FILE)
        if os.path.exists(subjectDescrFile):
            subjectJsonFile = io.open(subjectDescrFile, mode='r', encoding='utf-8')
            subjectDescriptorJsonstr = subjectJsonFile.read()
            subjectJsonFile.close()
            chapterRules, subjectActivities = deriveChapterRulesAndActivities(subdir, subjectDescriptorJsonstr)
            activities.extend(subjectActivities)
            chapterStatusRules.update(chapterRules)
    chapterStatusRulesJsonstr = json.dumps(chapterStatusRules, indent=2)
    statusRulesFile = io.open(os.path.join(outputDir, "status_rules.json"), mode='w', encoding='utf-8')
    statusRulesFile.write(chapterStatusRulesJsonstr)
    statusRulesFile.close()
    writeChapterActivities(pd.DataFrame(activities), outputDir)

def writeGradeNames(curriculumDir, outputDir):
    gradeNamesFile = io.open(os.path.join(curriculumDir, 'display names of grades.json'), mode='r', encoding='utf-8')
    gradeNamesJson = gradeNamesFile.read()
    gradeNamesFile.close()
    gradeNames = json.loads(gradeNamesJson)
    gradeMap = []
    for grade in gradeNames:
        gradeMap.append({"grade": grade, "display": gradeNames[grade]})
    gradeMapDF = pd.DataFrame(gradeMap)
    gradeMapDF.to_csv(os.path.join(outputDir, 'grade_map.csv'))

if len(sys.argv) == 3:
    deriveRules(curriculumDir=sys.argv[1], outputDir=sys.argv[2])
    writeGradeNames(curriculumDir=sys.argv[1], outputDir=sys.argv[2])
else:
    print("Usage:\n" + sys.argv[0] + " <LearningGrid curriculum dir> <output dir>")
