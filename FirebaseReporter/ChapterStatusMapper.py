import pandas as pd
import json
import os
import io
import numpy as np
import dbInterpreter

def getChapterStatusRules(rulesDir):
    STATUS_RULES_FILE = "status_rules.json"
    statusRulesFile = io.open(os.path.join(rulesDir, STATUS_RULES_FILE), mode='r', encoding='utf-8')
    chapterStatusRulesJsonstr = statusRulesFile.read()
    statusRulesFile.close()
    chapterStatusRules = json.loads(chapterStatusRulesJsonstr)
    return chapterStatusRules

chapterRecordIndex = ['chapter_id','classroom_id','subject_id','grade','student_id']

def markStatus(df, chapter_id, chapter_name, status, aggregator):
    statusGrid = pd.pivot_table(df, values='time_stamp', index=chapterRecordIndex, aggfunc=aggregator)
    nRows = len(statusGrid)
    statusGrid['status'] = [status for _ in range(nRows)]
    statusGrid['chapter_id'] = [chapter_id for _ in range(nRows)]
    statusGrid['chapter_name'] = [chapter_name for _ in range(nRows)]
    return statusGrid

def applyChapterStatusRule(acaDF, chapter_id, chapter_name, statusRule):
    STATUS_REQUIRED_KEY = "status_required"
    filterValuesKey = acaFilterKey = "no_id"
    if "chapter_ids" in statusRule:
        acaFilterKey = "chapter_id"
        filterValuesKey = "chapter_ids"
    elif "activity_ids" in statusRule:
        acaFilterKey = "activity_id"
        filterValuesKey = "activity_ids"
    chapterMergeIndex = chapterRecordIndex + ['time_stamp']
    filteredAcaDF = acaDF[chapterMergeIndex]
    aggregator = None
    for filterValue in statusRule[filterValuesKey]:
        if statusRule[STATUS_REQUIRED_KEY] == "_present":
            filter = (acaDF[acaFilterKey] == filterValue)
            aggregator = np.min
        elif statusRule[STATUS_REQUIRED_KEY] == "approved":
            filter = (acaDF[acaFilterKey] == filterValue) & (acaDF["status"] == "approved")
            aggregator = np.max
        else:
            print("status rule not understood: " + filterValue)
            filter = pd.DataFrame()
        filteredAcaForThisRule = acaDF.loc[filter][chapterMergeIndex]
        filteredAcaDF = filteredAcaDF.merge(
            filteredAcaForThisRule, on=chapterMergeIndex, how='inner')
    return markStatus(filteredAcaDF, chapter_id, chapter_name, statusRule["chapter_status"], aggregator)

def emptyChapterEntry(grade_subject, chapter_id, chapter_name):
    return {'chap_completion_ref': '', 'classroom_id': '', 'student_id': '', 'status': '', 'time_stamp': '',
            'grade_subject': grade_subject,
            'chapter_id': chapter_id,
            'chapter_name': chapter_name}

def mapChapterStatus(acaDF, rulesDir):
    STATUS_RULE_KEY = "status_rules"
    statusOfChapters = pd.DataFrame()
    subjectsStatusRules = getChapterStatusRules(rulesDir)
    dbInterpreter.joinGradeAndSubject(acaDF, subject_key='subject_id')
    emptyChapterEntries = []
    for grade_subject in subjectsStatusRules:
        for chapterStatusRule in subjectsStatusRules[grade_subject]:
            for statusRule in chapterStatusRule[STATUS_RULE_KEY]:
                chapterStatusDF = applyChapterStatusRule(acaDF.loc[acaDF['grade_subject'] == grade_subject],
                                                       chapterStatusRule['chapter_id'],
                                                       chapterStatusRule['chapter_name'],
                                                       statusRule)
                statusOfChapters = statusOfChapters.append(chapterStatusDF)
                if len(chapterStatusDF) == 0:
                    emptyChapterEntries.append(emptyChapterEntry(grade_subject, chapterStatusRule['chapter_id'], chapterStatusRule['chapter_name']))
    return statusOfChapters, emptyChapterEntries
