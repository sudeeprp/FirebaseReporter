import pandas as pd
import json
import os
import io
import numpy as np

def getChapterStatusRules(rulesDir):
    STATUS_RULES_FILE = "status_rules.json"
    statusRulesFile = io.open(os.path.join(rulesDir, STATUS_RULES_FILE), mode='r', encoding='utf-8')
    chapterStatusRulesJsonstr = statusRulesFile.read()
    chapterStatusRules = json.loads(chapterStatusRulesJsonstr)
    statusRulesFile.close()
    return chapterStatusRules

chapterRecordIndex = ['chapter_id','classroom_id','subject_id','grade','student_id']

def markStatus(df, chapter_id, status, aggregator):
    statusGrid = pd.pivot_table(df, values='time_stamp', index=chapterRecordIndex, aggfunc=aggregator)
    nRows = len(statusGrid)
    statusGrid['status'] = [status for _ in range(nRows)]
    statusGrid['chapter_id'] = [chapter_id for _ in range(nRows)]
    return statusGrid

def applyChapterStatusRule(acaDF, chapter_id, statusRule):
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
    return markStatus(filteredAcaDF, chapter_id, statusRule["chapter_status"], aggregator)

def mapChapterStatus(acaDF, rulesDir):
    STATUS_RULE_KEY = "status_rules"
    statusOfChapters = pd.DataFrame()
    subjectsStatusRules = getChapterStatusRules(rulesDir)
    acaDF['grade_subject'] = acaDF['grade'] + '_' + acaDF['subject_id'].str.lower()
    for grade_subject in subjectsStatusRules:
        for chapterStatusRule in subjectsStatusRules[grade_subject]:
            for statusRule in chapterStatusRule[STATUS_RULE_KEY]:
                chapterStatus = applyChapterStatusRule(acaDF.loc[acaDF['grade_subject'] == grade_subject],
                                                       chapterStatusRule['chapter_id'], statusRule)
                statusOfChapters = statusOfChapters.append(chapterStatus)
    return statusOfChapters
