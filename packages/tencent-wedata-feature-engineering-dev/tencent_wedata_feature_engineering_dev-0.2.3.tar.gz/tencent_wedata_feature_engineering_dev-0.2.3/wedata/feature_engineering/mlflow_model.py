import mlflow

class _FeatureEngineeringModelWrapper(mlflow.pyfunc.PythonModel):
    def __init__(self, model):
        self.model = model

    def predict(self, context, model_input):
       return self.model.predict(model_input)

