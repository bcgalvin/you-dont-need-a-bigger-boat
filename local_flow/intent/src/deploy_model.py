"""

Deploy a tensorflow model onto SageMaker

"""
import os
import time
import shutil
import tarfile
import numpy as np
import tensorflow as tf
from sagemaker.tensorflow import TensorFlowModel


def tf_model_to_tar(tf_model, run_id: int, ):
    """
    Saves tensorflow model as compressed file

    :param run_id: current Metaflow run id
    :param tf_model: tensorflow model
    :return:
    """

    model_name = f"intent-model-{run_id}/1"
    local_tar_name = f'model-{run_id}.tar.gz'

    # save model locally
    tf_model.save(filepath=model_name)
    # save model as .tar.gz
    with tarfile.open(local_tar_name, mode="w:gz") as _tar:
        _tar.add(model_name, recursive=True)
    # remove local model
    shutil.rmtree(model_name.split('/')[0])

    return local_tar_name


def deploy_model(model_s3_path: str):
    """
    Entry point for deploy step

    :param model_s3_path: S3 path of model to deploy
    :return: name of endpoint
    """

    # generate a signature for the endpoint using timestamp
    endpoint_name = f'intent-{int(round(time.time() * 1000))}-endpoint'

    # print out the name, so that we can use it when deploying our lambda
    print(f"\n\n================\nEndpoint name is: {endpoint_name}\n\n")

    # create sagemaker tf model
    model = TensorFlowModel(
        model_data=model_s3_path,
        image_uri=os.getenv('DOCKER_IMAGE'),
        role=os.getenv('IAM_SAGEMAKER_ROLE'))

    # deploy sagemaker model
    predictor = model.deploy(
        initial_instance_count=1,
        instance_type=os.getenv('SAGEMAKER_INSTANCE'),
        endpoint_name=endpoint_name)

    # prepare a test input and check response
    test_inp = {'instances': tf.one_hot(np.array([[0, 1, 1, 3, 4, 5]]),
                                        on_value=1,
                                        off_value=0,
                                        depth=7).numpy()}
    result = predictor.predict(test_inp)
    print(test_inp, result)
    assert result['predictions'][0][0] > 0

    # return endpoint name for downstream use
    return endpoint_name
