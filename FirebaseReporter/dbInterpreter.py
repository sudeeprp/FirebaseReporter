
def splitGradeAndSubject(dfWithGradeSub, grade_key='grade', subject_key='subject'):
    grade_subject = dfWithGradeSub['grade_subject'].str.split('_', n=1, expand=True)
    dfWithGradeSub[grade_key] = grade_subject[0]
    dfWithGradeSub[subject_key] = grade_subject[1]
    dfWithGradeSub.drop(columns=['grade_subject'], inplace=True)
    return dfWithGradeSub

def joinGradeAndSubject(df, grade_key='grade', subject_key='subject'):
    df['grade_subject'] = df[grade_key].astype(str) + '_' + df[subject_key].str.lower()
    pass
