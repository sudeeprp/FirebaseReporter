import json
import os
import io
import sys

def nextChapterID(chaptersArray, currentChapterIndex):
    nextChapterIndex = currentChapterIndex + 1
    if nextChapterIndex < len(chaptersArray):
        return chaptersArray[nextChapterIndex]["chapter_id"]
    else:
        return "_never_completes"

def deriveChapterRules(grade_chapter, subjectDescriptorJsonstr):
    chapterRules = {}
    chaptersActivities = json.loads(subjectDescriptorJsonstr)
    statusRulesOfChapters = []
    for chapterIndex, chapterDescr in enumerate(chaptersActivities):
        chapterRule = {}
        chapterRule["chapter_name"] = chapterDescr["chapter_name"]
        chapterRule["chapter_id"] = chapterDescr["chapter_id"]
        activitiesForCompletion = []
        for activityDescr in chapterDescr["activities"]:
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
    chapterRules[grade_chapter.lower()] = statusRulesOfChapters
    return chapterRules

def deriveRules(curriculumDir, outputDir):
    CHAPTER_DESCRIPTOR_FILE = "chapter_activities.json"
    STATUS_RULES_FILE = "status_rules.json"
    subdirPaths = [entry for entry in os.listdir(curriculumDir) if os.path.isdir(os.path.join(curriculumDir, entry))]
    chapterStatusRules = {}
    for subdir in subdirPaths:
        subjectDescrFile = os.path.join(os.path.join(curriculumDir, subdir), CHAPTER_DESCRIPTOR_FILE)
        if os.path.exists(subjectDescrFile):
            subjectJsonFile = io.open(subjectDescrFile, mode='r', encoding='utf-8')
            subjectDescriptorJsonstr = subjectJsonFile.read()
            subjectJsonFile.close()
            chapterStatusRules.update(deriveChapterRules(subdir, subjectDescriptorJsonstr))
    chapterStatusRulesJsonstr = json.dumps(chapterStatusRules, indent=2)
    statusRulesFile = io.open(os.path.join(outputDir, STATUS_RULES_FILE), mode='w', encoding='utf-8')
    statusRulesFile.write(chapterStatusRulesJsonstr)
    statusRulesFile.close()

if len(sys.argv) == 3:
    deriveRules(curriculumDir=sys.argv[1], outputDir=sys.argv[2])
else:
    print("Usage:\n" + sys.argv[0] + " <LearningGrid curriculum dir> <output dir>")
