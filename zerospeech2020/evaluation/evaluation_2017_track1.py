"""Evaluation of the 2017 track1 part of the Zerospeech2020 challenge"""

import logging
import os

from zerospeech2020.evaluation import abx


_VALID_LANGUAGES = ['english', 'french', 'mandarin', 'LANG1', 'LANG2']
_VALID_DURATIONS = ['1s', '10s', '120s']
_VALID_TASKS = ['across', 'within']
_VALID_DISTANCES = ['cosine', 'KL']


def evaluate(submission, dataset, languages, durations,
             distance, normalize, njobs=1, log=logging.getLogger()):
    """Evaluation of the 2017 track1: ABX score

    Compute the ABX score on the specified languages and durations subsets.

    Parameters
    ----------
    submission (str): the directory of the submission to evaluate

    dataset (str): path to the ZeroSpeech2020 dataset (required for the ABX
        task files).

    languages (list): elements must be 'french', 'english', 'mandarin',
        'LANG1' or 'LANG2'. Note that ABX tasks are not provided to
        participants for 'LANG1' and 'LANG2', evaluation for those languages
        will require an official submission to the challenge.

    duration (list): elements must be '1s', '10s' or '120s'.

    distance (str): the distance to use, must be 'cosine' or 'KL'.

    normalize (bool): when True, normalize the DTW path during distance
        computions.

    njobs (int): the number of CPU cores to use.

    log (logging.Logger): where to send log messages.

    Raises
    ------
    ValueError if the method fails.

    Returns
    -------
    score (dict) : the ABX scores for the specified languages, durations and
        distance in the format score[language][duration][within / across]. An
        ABX score is given as an error rate in %.

    """
    score = {'params': {'distance': distance, 'normalize': normalize}}
    for language in languages:
        score[language] = {}
        for duration in durations:
            score[language][duration] = {}
            for task in _VALID_TASKS:
                score[language][duration][task] = _evaluate_single(
                    submission, dataset, language, duration,
                    task, distance, normalize, njobs, log)
    return {'2017-track1': score}


def _evaluate_single(
        submission, dataset, language, duration, task,
        distance, normalize, njobs, log):
    log.info('evaluating 2017 track1 for %s %s %s', language, duration, task)

    # ensure the language is valid
    if language not in _VALID_LANGUAGES:
        raise ValueError(
            f'invalid language {language}, must be in '
            f'{", ".join(_VALID_LANGUAGES)}')

    # ensure the language is valid
    if duration not in _VALID_DURATIONS:
        raise ValueError(
            f'invalid duration {duration}, must be in '
            f'{", ".join(_VALID_DURATIONS)}')

    # ensure task is valid
    if task not in _VALID_TASKS:
        raise ValueError(
            f'invalid task type {task}, must be in '
            f'{", ".join(_VALID_TASKS)}')

    # ensure the distance is valid
    if distance not in _VALID_DISTANCES:
        raise ValueError(
            f'invalid distance {distance}, must be in '
            f'{", ".join(_VALID_DISTANCES)}')

    if not os.path.isdir(submission):
        raise ValueError('2017 submission not found')

    features_directory = os.path.join(
        submission, '2017', 'track1', language, duration)
    if not os.path.isdir(features_directory):
        raise ValueError(f'directory not found: {features_directory}')

    return abx.abx(
        features_directory,
        '2017',
        abx.get_tasks(dataset, '2017')[(language, duration, task)],
        task,
        distance,
        normalize,
        njobs=njobs,
        log=log)
