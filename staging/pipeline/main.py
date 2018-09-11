import argparse

from basic import filesystem, log
from dataio import fileio, networkio
from ml.feature_extractors.historical_salient_terms import HSTIndicatorFeatureExtractor, \
    HSTGlobalIndicatorFeatureExtractor
from serialization.dataio.networkio import TwitterConnSpecsDeserializer
from staging.pipeline import labelling, modelling, collecting
from utils import argparse_utils

logger = log.create_logger('main')
log.create_logger('collecting')
log.create_logger('labelling')
log.create_logger('modelling')

log.create_logger('dataio.fileio.accessors')
log.create_logger('ml.kfold')
log.create_logger('ml.models.model_utils')


def get_twitter_auth(twitter_conf_file_in):
    conn_spec = fileio.file_to_type(
        twitter_conf_file_in, TwitterConnSpecsDeserializer)
    return networkio.get_twitter_auth(conn_spec)


def main(seed_file_in,
         users_raw_dir, users_labelled_dir,
         stats_dir,
         kfold_dir, k, split_spec,
         twitter_conf_file_in):
    twitter_auth = get_twitter_auth(twitter_conf_file_in)
    seed_uts = collecting.get_active_seed_uids(seed_file_in, twitter_auth)
    collecting.collect_user_hist_tweets(seed_uts, users_raw_dir, 300, twitter_auth)

    labelling.gen_examples_and_vocab(users_raw_dir, users_labelled_dir,
                                     stats_dir, min_ex_per_user=100)
    points, labels = labelling.get_examples(users_labelled_dir,
                                            main_class=1, class_ratio=0.001)
    vocab = labelling.get_vocab(stats_dir)
    kfolds = modelling.gen_kfold(k, points, labels, split_spec, kfold_dir)

    #modelling.train_model(features, labels, kfolds)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sarcasm')
    parser.add_argument('-sf', '--seed_file',
                        help='file with seed tweets',
                        action=filesystem.ReadableFile,
                        required=True)
    parser.add_argument('-urd', '--users_raw_dir',
                        help='directory with unlabelled user data',
                        action=filesystem.EnsureWritableDir,
                        required=True)
    parser.add_argument('-uld', '--users_labelled_dir',
                        help='directory with labelled user data',
                        action=filesystem.EnsureWritableDir,
                        required=True)
    parser.add_argument('-sd', '--stats_dir',
                        help='directory with stats',
                        action=filesystem.EnsureWritableDir,
                        required=True)
    parser.add_argument('-kd', '--kfold_dir',
                        help='directory with kfold splits',
                        action=filesystem.EnsureWritableDir,
                        required=True)
    parser.add_argument('-k', '--k',
                        help='number of folds',
                        type=int,
                        required=True)
    parser.add_argument('-s', '--split_spec',
                        help='kfold split spec (3 floats summing up to 1)',
                        nargs='+',
                        type=float,
                        action=argparse_utils.ValidSplitSpec,
                        required=True)
    parser.add_argument('-tf', '--twitter_conf_file',
                        help='twitter connection specifications file',
                        action=filesystem.ReadableFile,
                        required=True)

    args = parser.parse_args()
    main(args.seed_file,
         args.users_raw_dir, args.users_labelled_dir,
         args.stats_dir,
         args.kfold_dir, args.k, args.split_spec,
         args.twitter_conf_file)
