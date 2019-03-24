
def splitGradeAndSubject(dfWithGradeSub):
    grade_subject = dfWithGradeSub['grade_subject'].str.split('_', n=1, expand=True)
    dfWithGradeSub['grade'] = grade_subject[0]
    dfWithGradeSub['subject'] = grade_subject[1]
    dfWithGradeSub.drop(columns=['grade_subject'], inplace=True)
    return dfWithGradeSub
