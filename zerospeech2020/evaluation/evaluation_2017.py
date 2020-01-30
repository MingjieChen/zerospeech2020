
import pkg_resources 
import logging


from utils import *
from tdev2.measures.ned import *
from tdev2.measures.boundary import *
from tdev2.measures.grouping import *
from tdev2.measures.coverage import *
from tdev2.measures.token_type import *
from tdev2.readers.gold_reader import *
from tdev2.readers.disc_reader import Disc as Track2Reader

class Evaluation2017:
    def __init__(self, submission,
                 njobs=1, log=logging.getLogger()):
        self._log = log
        self._njobs = njobs

        if not os.path.isdir(submission):
            raise ValueError('2017 submission not found')
        self._submission = submission


class Evaluation2017_track2():
    def __init__(self, submission,
                 log=logging.getLogger(),
                 language_choice=None):
        self._log = log

        ## TODO change output ?

        if not os.path.isdir(submission):
            raise ValueError('2017 submission not found')
        self._submission = submission

        self.gold = None
        self.disc = None
        if language_choice is not None:
            self.language_choice = language_choice
        else:
            self.language_choice = ['english', 'french', 'mandarin', 'LANG1', 'LANG2']

    def _read_gold(self, language):
        self._log.info('reading track2 '
                       'gold for {}'.format(language))
        wrd_path = pkg_resources.resource_filename(
                pkg_resources.Requirement.parse('tdev2'),
                'tdev2/share/{}.wrd'.format(language))
        phn_path = pkg_resources.resource_filename(
                pkg_resources.Requirement.parse('tdev2'),
                'tdev2/share/{}.phn'.format(language))
        self.gold = Gold(wrd_path=wrd_path, 
                    phn_path=phn_path)

    def _read_discovered(self, class_file, language):
        self._log.info('reading discovered '
                        'classes for {}'.format(language))
        if not self.gold:
            raise ValueError('Trying to evaluate track2 without reading the gold')

        self.disc = Track2Reader(class_file, self.gold)
 
    def _evaluate_lang(self):
        """Compute all metrics on requested language"""
        try:
            self._log.info('Computing Boundary...')
            boundary = Boundary(self.gold, self.disc, self.output)
            boundary.compute_boundary()
            boundary.write_score()
        except:
            self._log.warning('Was unable to compute boundary')

        try:
            self._log.info('Computing Grouping...')
            grouping = Grouping(self.disc, self.output)
            grouping.compute_grouping()
            grouping.write_score()
        except:
            self._log.warning('Was unable to compute grouping')

        try:
            self._log.info('Computing Token and Type...')
            token_type = TokenType(self.gold, self.disc, self.output)
            token_type.compute_token_type()
            token_type.write_score()
        except:
            self._log.warning('Was unable to compute Token/Type')

        try:
            self._log.info('Computing Coverage...')
            coverage = Coverage(self.gold, self.disc, self.output)
            coverage.compute_coverage()
            coverage.write_score()
        except:
            self._log.warning('Was unable to compute coverage')

        try:
            self._log.info('Computing ned...')
            ned = Ned(self.disc, self.output)
            ned.compute_ned()
            ned.write_score()
        except:
            self._log.warning('Was unable to compute ned')


    def evaluate(self):
        """Compute metrics on all languages"""
        self._log.info('evaluating track2')
        self.language_choice = ['english', 'french', 'mandarin', 'LANG1', 'LANG2']

        for language in self.language_choice:
            class_file = os.path.join(self._submission, "2017",
                         "track2",
                         "{}.txt".format(language))
            self._log.info('evaluating {}'.format(class_file))


            # check if class  file exists and evaluate it
            if os.path.isfile(class_file):
                self.output = os.path.join(self._submission, "2017",
                         "track2", language)
                if not os.path.isdir(self.output):
                    os.makedirs(self.output)
                self._read_gold(language)
                self._read_discovered(class_file, language)
                self._evaluate_lang()


class Evaluation2017_track1():
    def __init__(self, submission,
                 log=logging.getLogger(),
                 language_choice=None,
                 tasks=None,
                 n_cpu=1,
                 normalize=1,
                 distance="default"):
        self._log = log
        self.distance = distance
        self.normalize = normalize
        self.n_cpu = n_cpu
        if not os.path.isdir(submission):
            raise ValueError('2017 submission not found')
        self.tasks = tasks
        self._submission = submission
        if language_choice is not None:
            self.language_choice = language_choice
        else:
            self.language_choice = ['english', 'french', 'mandarin', 'LANG1', 'LANG2']
        self.durations_choice = ["1s", "10s", "120s"]

    def _make_temp(self):
        return tempfile.mkdtemp()
    
    #def __del__(self):
    #    # delete the temporary folder
    #    if self._is_zipfile:
    #        shutil.rmtree(self._submission)

    def evaluate(self):
        """Run ABX evaluation on selected languages, on selected durations"""
       
        tmp = self._make_temp()
        self._log.info('temp dir {}'.format(tmp))
        tasks = get_tasks(self.tasks, "2017")
        for language in self.language_choice:
            self._log.info('evaluating {}'.format(language))
            for duration in self.durations_choice:
                feature_folder = os.path.join(self._submission, "2017",
                                              "track1", language, duration)
                task_across = tasks[(language, duration, "across")]
                task_within = tasks[(language, duration, "within")]
                if os.path.isdir(feature_folder):
                    self._log.info('across')
                    run_abx(feature_folder, task_across, tmp, load_feat_2017, self.n_cpu, self.normalize, 'across')
                    empty_tmp_dir(tmp)
                    self._log.info('within')
                    run_abx(feature_folder, task_within, tmp, load_feat_2017, self.n_cpu, self.normalize, 'within')
                else:
                    raise ValueError("Trying to evaluate feature that doesn't exist for 2017 corpus, {}, {}".format(language, duration))
