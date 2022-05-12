import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pathlib
from typing import Union, Tuple


class QuestionnaireAnalysis:
    """
    Reads and analyzes data generated by the questionnaire experiment.
    Should be able to accept strings and pathlib.Path objects.
    """

    def __init__(self, data_fname: Union[pathlib.Path, str]):
        if type(data_fname) != pathlib.Path:
            data_fname = pathlib.Path(data_fname)
        self.data_fname = data_fname
        self.read_data()

    def read_data(self):
        """Reads the json data located in self.data_fname into memory, to
        the attribute self.data.
        """
        self.data = pd.read_json(self.data_fname)


    # 1
    def show_age_distrib(self) -> Tuple[np.ndarray, np.ndarray]:
       """Calculates and plots the age distribution of the participants.

        Returns
        -------
        hist : np.ndarray
            Number of people in a given bin
        bins : np.ndarray
            Bin edges
       """
       ages = pd.Series(self.data["age"])
       fig, ax = plt.subplots()
       ax.set_title('Age Distribution')
       ax.set_xlabel('Bins')
       ax.set_ylabel('Number of People')
       bins = np.linspace(0,100,11)
       hist,_,_ = plt.hist(ages, bins = bins)
       # plt.show()
       return (hist,bins)

    #  2.
    def remove_rows_without_mail(self) -> pd.DataFrame:
        """Checks self.data for rows with invalid emails, and removes them.

        Returns
        -------
        df : pd.DataFrame
        A corrected DataFrame, i.e. the same table but with the erroneous rows removed and
        the (ordinal) index after a reset.
        """
        emails_length = self.data['email'].str.len()
        find_first_dot = self.data['email'].str.find('.')
        find_last_dot = self.data['email'].str.rfind('.')
        find_first_at = self.data['email'].str.find('@')
        find_last_at = self.data['email'].str.rfind('@')
        cond1 = (find_last_at == find_first_at) & (find_first_at > 0) & (find_first_at<emails_length)
        cond2 = (find_first_dot > 0) & (find_last_dot<emails_length)
        cond3 = []
        for email, index in zip(self.data['email'], find_first_at):
            cond3.append(email[index+1] != '.')
        valid_email = cond1 & cond2 & cond3
        df = self.data[valid_email]
        return df.reset_index(drop=True)

    # 3.
    def fill_na_with_mean(self) -> Tuple[pd.DataFrame, np.ndarray]:
        """Finds, in the original DataFrame, the subjects that didn't answer
            all questions, and replaces that missing value with the mean of the
            other grades for that student.

        Returns
        -------
        df : pd.DataFrame
            The corrected DataFrame after insertion of the mean grade
        arr : np.ndarray
            Row indices of the students that their new grades were generated
        """
        all_means_vector = self.data.loc[:,"q1":"q5"].mean(1)
        all_means_matrix = np.transpose(np.broadcast_to(all_means_vector,(5,100)))
        all_means_df = pd.DataFrame(all_means_matrix, columns = ['q1', 'q2', 'q3', 'q4', 'q5'])
        df = self.data.fillna(value = all_means_df)
        arr_bool = self.data.loc[:,"q1":"q5"].isna().sum(1) > 0
        arr = np.arange(len(self.data))[arr_bool]
        return (df, arr)
        
    #4.
    def score_subjects(self, maximal_nans_per_sub: int = 1) -> pd.DataFrame:
       """Calculates the average score of a subject and adds a new "score" column
       with it.

       If the subject has more than "maximal_nans_per_sub" NaN in his grades, the
       score should be NA. Otherwise, the score is simply the mean of the other grades.
       The datatype of score is UInt8, and the floating point raw numbers should be
       rounded down.

       Parameters
       ----------
       maximal_nans_per_sub : int, optional
           Number of allowed NaNs per subject before giving a NA score.

       Returns
       -------
       pd.DataFrame
           A new DF with a new column - "score".
       """
       sum_nan = self.data.loc[:,"q1":"q5"].isna().sum(1)
       mask_nan = sum_nan > maximal_nans_per_sub
       score = self.data.loc[:,"q1":"q5"].mean(1)
       score = score.apply(np.floor).astype('UInt8')
       score[mask_nan] = None
       new_df = self.data.copy()
       new_df["score"] = score
       return new_df 