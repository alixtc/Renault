import pandas as pd
from renault.get_data import get_pji_with_misssing_fluids_measure
from renault.feature_engineering import feature_engineering

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.neighbors import LocalOutlierFactor


class AnomalyDetection:
    def __init__(self, training_df) -> None:
        self.working_df = training_df
        
    def filter_preprocess_train_data(self, n_fluid=2, n_measure=2):
        """remove pji without required number of fluids and measurements,
        prevent the apparition of NaN values in the next steps.
        List of bad PJI is saved in the instance for further inspection"""
        working_df = self.working_df
        # Removes ActVacuum (specific to UC), can be included in IF statement 
        filtered_df = working_df[working_df['measurement'] != 'ActVacuum']
        train_bad_pji = get_pji_with_misssing_fluids_measure(filtered_df, n_fluid, n_measure)
        filtered_df = filtered_df[~filtered_df.pji.isin(train_bad_pji)]
        self.train_bad_pji = train_bad_pji
        
        # Actually Transform DF to PJI indexed DF with features in the columns
        self.train_df = feature_engineering(filtered_df)
    
        return self
    
    def fit_on_train(self):
        """Scaling and Local Outlier Factor are fit to the training data 
        and stored for later use on prediction """
        
        # Imputer for missing values (due to diff) => input very divergeant value
        pipe = make_pipeline(
            StandardScaler(),
            SimpleImputer(strategy='constant', fill_value=-3)
        )
        self.pipeline = pipe.fit(self.train_df)
        self.X_train = pipe.transform(self.train_df)
        
        self.lof = LocalOutlierFactor(n_neighbors=20, novelty=True).fit(self.X_train)
        return self
    
    def filter_preprocess_test_data(self, test_df, n_fluid=2, n_measure=2):
        """remove pji without required number of fluids and measurements,
        prevent the apparition of NaN values in the next steps.
        List of bad PJI is saved in the instance for further inspection"""

        # Removes ActVacuum (specific to UC), can be included in IF statement 
        filtered_df = test_df[test_df['measurement'] != 'ActVacuum']
        test_bad_pji = get_pji_with_misssing_fluids_measure(filtered_df, n_fluid, n_measure)
        filtered_df = filtered_df[~filtered_df.pji.isin(test_bad_pji)]
        self.test_bad_pji = test_bad_pji
        
        # Actually Transform DF to PJI indexed DF with features in the columns
        self.test_df = feature_engineering(filtered_df)
        self.X_test = self.pipeline.transform(self.test_df)
        self.list_of_pji_test = test_df[['pji']].drop_duplicates()
        return self
    
    def calculate_anomaly_score(self):
        """Returns a DF with PJI, bolean for anomaly, and anomaly score"""
        results_lof = pd.DataFrame(self.lof.predict(self.X_test),
             columns=['anomaly'])
        results_lof.index = self.test_df.index
        results_lof['score'] = self.lof.score_samples(self.X_test)
        results_lof['anomaly'] = (results_lof['anomaly'] == -1)
        results_lof.reset_index(inplace=True)
        return results_lof
    
    def return_predictions(self):
        """Combine list of Bad PJI with anomaly score"""
        # get pji from original test dataset, left join with LOF results
        global_results = pd.merge(
                                self.list_of_pji_test,
                                self.calculate_anomaly_score(),
                                on='pji',
                                how='left')

        # Fill NAs with anomaly (bad_pji with missing recordings)
        global_results.anomaly.fillna(value=True, inplace=True)
        return global_results


    
    
    
        
    