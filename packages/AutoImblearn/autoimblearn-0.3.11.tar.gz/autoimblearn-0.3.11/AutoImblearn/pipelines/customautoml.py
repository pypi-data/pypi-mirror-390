import numpy as np
from ..components.automls import RunH2O, RunTPOT, RunAutoSklearn


# AutoML systems - using lazy initialization pattern (lambdas)
# to avoid instantiation errors before data_folder is set
automls = {
    "h2o": lambda data_folder: RunH2O(data_folder=data_folder),
    "tpot": lambda data_folder: RunTPOT(data_folder=data_folder),
    "autosklearn": lambda data_folder: RunAutoSklearn(data_folder=data_folder),
}

class CustomAutoML:
    def __init__(self, args, automl):
        self.args = args
        if automl in automls.keys():
            self.automl = automls[automl]
        else:
            raise ValueError("Model {} not defined in model.py".format(automl))
        self.result = None

    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        # Train classifier
        self.automl.fit(X_train, y_train, args=self.args)

    def predict(self):

        result = self.automl.predict()
        return result


if __name__ == "__main__":
    class Arguments:
        def __init__(self):
            self.dataset = "nhanes.csv"
            self.metric = "auroc"

            self.device = "cpu"
            self.cuda = "0"

            self.val_ratio=0.1,
            self.test_raito=0.1,
    args = Arguments()

    tmp = CustomAutoML(args, 'autosklearn')
    tmp.train(None, None)
    print(tmp.predict(None, None))
