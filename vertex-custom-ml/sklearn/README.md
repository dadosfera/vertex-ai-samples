How to?

There are different ways to have training-predictions on Vertex; using containers, local-python-file, python distribution package, [run.py](./run.py) has all the steps to fire training and predictions using those different ways.

## Create the Training Image

- go to [training folder](./training) and run the following command:

*snippet below creates a docker image and push it into the repository, remember to use {YOUR_PROJECT_ID}*

```bash
gcloud builds submit -t gcr.io/{YOUR_PROJECT_ID}/sklearn-train .
```

## Create the Prediction Image

- go to [prediction folder](./prediction) and run the following command:

```bash
gcloud builds submit -t gcr.io/{YOUR_PROJECT_ID}/ecommerce:fast-onnx .
```

## Fire up! Use [run.py](./run.py)

*Remember to change variables*

## or use Notebooks:

- [container/customJob](./container.ipynb)


Happy coding!
