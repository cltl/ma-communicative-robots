import pronoun_extraction_script
import pandas as pd
import numpy as np

# Problem installing pytorch
# https://stackoverflow.com/questions/65191751/error-torch-has-an-invalid-wheel-dist-info-directory-not-found

def system_results(gold, predicted, baseline):
    '''
    Generates the interpretation of the predicted action of the system.
    :param gold: string with gold pronouns (He/him, She/her, They/them)
    :param predicted: string with the predicted result of the system (He/him, She/her, Ask)
    :param baseline: string with the baseline prediction (He/him, She/her)
    :return: The interpretation of the predicted action (Correct, Wrong, Good Ask, Unnescessary Ask)
    '''
    # If the predicted pronouns are the gold pronouns
    if gold==predicted:
        return 'Correct'
    #If our system asks for pronouns and the baseline predicted correctly
    elif predicted=='Ask' and gold==baseline:
        return 'Unnescessary Ask'
    # If our system asks for pronouns and the baseline predicted incorrectly
    elif predicted=='Ask' and gold!=baseline:
        return 'Good Ask'
    else:
        return 'Wrong'

def extend_dataframe(df):
    '''
    Runs the system and baseline on the dataframe with testsdata. The intermediate and final results will be added to the dataframe.
    :param df: Dataframe
    :return: The resulting dataframe
    '''
    #TODO This code is suboptimal, might need to revise the visual gender classifier to get the baseline and system at the same time when dealing with more data
    #Apply the system to the data
    df['Visual Gender']=df.apply(lambda row: pronoun_extraction_script.get_visual_gender(row['Path']), axis=1)
    df['Name Gender']=df.apply(lambda row: pronoun_extraction_script.get_name_gender(row['Name']), axis=1)
    #For the baseline prediction the thresholds for male is set to below 0.5 and for female above 0.5
    df['Baseline Prediction']=df.apply(lambda row: pronoun_extraction_script.get_visual_gender(row['Path'], 0.5, 0.5), axis=1)
    #Transform the Baseline predictions to Pronouns
    df['Baseline Prediction']=df['Baseline Prediction'].replace({0:'He/him', 1:'She/her'})
    #Make System prediction
    df['System Prediction']=np.where(df['Visual Gender']==df['Name Gender'], df['Name Gender'], 2)
    #Interpret System prediction
    df['System Prediction'] =df['System Prediction'].replace({0:'He/him', 1:'She/her', 2:'Ask'})
    #Generate Baseline results
    df['Baseline Results']=np.where(df['Baseline Prediction']==df['Pronouns'], 'Correct', 'Wrong')
    #Generate System results
    df['System Results']= df.apply(lambda row: system_results(row['Pronouns'], row['System Prediction'], row['Baseline Prediction']), axis=1)
    return df


def main(test_csv='data/Combots dataset - sample_data.csv'):
    data=pd.read_csv(test_csv)
    data=extend_dataframe(data)
    print(data.head())
    print('Baseline Results:')
    print(data['Baseline Results'].value_counts())
    print('\nSystem Results:')
    print(data['System Results'].value_counts())




if __name__ == "__main__":
    main()