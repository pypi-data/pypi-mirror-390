################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R, 5737-L65
# (c) Copyright IBM Corp. 2021-2025. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################

import statistics

import gensim
import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.decomposition import PCA

from autoai_libs.detectors.date_time.date_time_detector import DateDatasetDetector

SEED = 33
gensim_major_version = int(gensim.__version__.split(".")[0])


def custom_unique(aux):
    """
        This custom 'unique' function should replace np.unique() as for large text columns we are hitting OOM.
        This implementation is mapped 1:1 to np.unique() in regards to needed functionality.

        For better performance and stable results, 'stable' sorting algorithm is used. The default one
        used in np.unique() is 'quicksort' which is marked as not stable.
        With 'stable' type, numpy will choose between 'mergesort' and 'timsort' appropriate.

        This implementation get rids of unnecessary array copying and computations that are not further used.

        This function is an equivalent to:

        values, counts_1 = np.unique(aux, return_counts=True)
        counts_2 = custom_unique(aux)

        counts_1 == counts_2

    Parameters
    ----------
    aux: np.array, required
        numpy array to be processed

    Returns
    -------
    np.array with counts of the unique values in that array

    """
    aux.sort(kind="stable")
    mask = np.empty(aux.shape, dtype=np.bool_)
    mask[:1] = True
    mask[1:] = aux[1:] != aux[:-1]

    return np.diff(np.concatenate(np.nonzero(mask) + ([mask.size],)))


def replace_nan(column):
    """
    Replaces nan in text columns
    """
    # if text column consist of too much text, we are hitting OOM,
    # it is better to process longer with smaller batches than hit OOM
    batch_size = 10000

    if len(column) < batch_size:
        column = column.astype("str")
        column[column == "nan"] = ""
    else:
        num_batches = _compute_num_batches(column, batch_size)

        for index in range(num_batches):
            start_index = index * batch_size
            end_index = len(column) if index == num_batches - 1 else (index + 1) * batch_size
            column1 = column[start_index:end_index]
            column1 = column1.astype("str")
            column1[column1 == "nan"] = ""
            column[start_index:end_index] = column1
    return column


def _compute_num_batches(column, batch_size):
    return int(np.ceil(len(column) / batch_size))


def _compute_end_index(column, index, num_batches, batch_size):
    return len(column) if index == num_batches - 1 else (index + 1) * batch_size


def replace_unicode(text):
    """
    Replaces special characters in text columns
    """
    return text.encode("ascii", "ignore").decode("utf-8")


class TextTransformersList:
    word2vec = "word2vec"


class SmallDataTextDetector(BaseEstimator, TransformerMixin):

    def __init__(self):
        self.rng = np.random.default_rng(seed=SEED)

    def _is_text(self, column, return_counts=False, max_sentences=10000):
        """
        Returns if a column is of type text. Ignores categorical and id columns
        """

        length = len(column) if len(column) <= max_sentences else max_sentences
        subset_indices = self.rng.choice(len(column), length, replace=False)
        column1 = column[subset_indices]
        column1 = np.where(pd.isna(column1), "", column1)
        column1 = pd.DataFrame(column1, dtype=str)[0].to_numpy()

        try:
            column1.astype("float", copy=False)
        except ValueError:
            text_col = True
        else:
            text_col = False
        if not text_col:
            if return_counts:
                return False, 0
            else:
                return False

        mean_num_words = self.compute_num_words(column1)
        counts = custom_unique(column1)
        # Replace missing values

        # ignore categorical
        if len(counts) < len(column1) / 5:
            if return_counts:
                return False, mean_num_words
            else:
                return False

        # ignore unique id like columns
        if int(mean_num_words) == 1:
            text_col = False if int(counts.mean()) == 1 else True
            if return_counts:
                return text_col, mean_num_words
            else:
                return text_col
        else:
            if return_counts:
                return True, mean_num_words
            else:
                return True

    def _is_sentence(self, column, min_num_words):
        """
        Returns if a column is of type sentence. Ignores categorical and id columns
        If the mean number of words computed on a randomly sampled subset of the column is higher
        than the min_num_words, then the column is a sentence
        """

        is_text, num_words = self._is_text(column, True)
        if not is_text:
            return False

        if round(num_words) >= min_num_words:
            return True
        else:
            return False

    def compute_num_words(self, column, max_sentences=10000):
        if not self._is_text:
            return False
        length = len(column) if len(column) <= max_sentences else max_sentences
        subset_indices = self.rng.choice(len(column), length, replace=False)

        col_subset = column[subset_indices]
        col_subset = col_subset[np.where(~(pd.isna(col_subset)))]

        # ignore empty string to get only sentences.
        num_words = list(map(lambda x: len(str(x).strip().split(" ")), col_subset))
        mean_num_words = statistics.mean(num_words)
        return mean_num_words

    def detect_string_type(self, data):
        """
        Detects all the string columns in the dataset. Ignores categorical and id columns
        """
        result = np.apply_along_axis(self._is_text, 0, data)
        return np.arange(data.shape[1])[result]

    def detect_sentence_type(self, data, min_num_words):
        """
        Returns all the sentence columns in the dataset.
        If the mean number of words computed on a randomly sampled subset of the column is higher
        than the min_num_words, then the column is a sentence
        """

        detector = DateDatasetDetector(X=data[:10])
        detector.detect()
        result = [
            self._is_sentence(data[:, col], min_num_words) if col not in detector.date_columns_indices else False
            for col in range(data.shape[1])
        ]
        return np.arange(data.shape[1])[result]

    def fit(self, X, y=None):
        self.text_columns = self.detect_string_type(X)
        return self


class TextTransformer(BaseEstimator, TransformerMixin):
    """
    TextTransformer is the point of entry from autoai_core. The output is transforming the text columns
    """

    def __init__(
        self,
        text_processing_options,
        column_headers_list=[],
        drop_columns=False,
        min_num_words=3,
        columns_to_be_deleted=[],
        text_columns=None,
        activate_flag=True,
    ):
        """
        text_processing_options: A map of the transformers to be applied and the hyper parameters of the transformers.
             {TextTransformersList.word2vec:{'output_dim':vocab_size}}
        column_headers_list: The list of columns generated by autoai_core's processing.
               The column headers of the generated features will be appended to this and returned.
        drop_columns: If the original text columns need to be dropped.
        min_num_words: The minimum numbers of words a column must have in order to be considered as a text column.
        columns_to_be_deleted: List of columns that autoai_core wants to be deleted.
        text_columns: If text columns are sent, then text detection is not done again.
        activate_flag: Required by autoai_core to avoid regenerating these features for every iteration.
        """

        self.text_processing_options = text_processing_options
        self.column_headers_list = column_headers_list
        self.drop_columns = drop_columns
        self.is_first = True
        self.text_columns = text_columns
        self.columns_added_flag = False
        self.min_num_words = min_num_words
        self.columns_to_be_deleted = columns_to_be_deleted
        self.activate_flag = activate_flag

        self.transformer_map = {
            TextTransformersList.word2vec: Word2VecTransformer,
        }
        self.transformer_objs = []
        self.text_detector = SmallDataTextDetector()

    def replace_special_chars(self, X):
        batch_size = 10000
        X = np.apply_along_axis(replace_nan, 0, X)
        vec = np.vectorize(replace_unicode)
        for col_num in range(X.shape[1]):
            num_batches = _compute_num_batches(X[:, col_num], batch_size)
            for index in range(num_batches):
                start_index = index * batch_size
                end_index = _compute_end_index(X[:, col_num], index, num_batches, batch_size)
                X[start_index:end_index, col_num] = vec(X[start_index:end_index, col_num])
        return X

    def fit(self, X, y=None):
        # clear transformer_obj list for a fit call
        self.transformer_objs = []
        if self.text_columns is None:
            self.text_columns = self.text_detector.detect_sentence_type(X, self.min_num_words)

            # If no text columns are detected, then return
            if len(self.text_columns) == 0:
                return self

        if self.columns_to_be_deleted is not None and self.drop_columns is True:
            columns_to_be_deleted = set(self.columns_to_be_deleted).union(set(self.text_columns))
            columns_to_be_deleted = list(columns_to_be_deleted)
        elif self.drop_columns is True:
            columns_to_be_deleted = self.text_columns
        else:
            columns_to_be_deleted = self.columns_to_be_deleted

        self.columns_to_be_deleted = columns_to_be_deleted

        X[:, self.text_columns] = self.replace_special_chars(X[:, self.text_columns])

        for text_transformer in self.text_processing_options.keys():
            trans_obj = self.transformer_map[text_transformer](
                text_processing_options={
                    **self.text_processing_options[text_transformer],
                    "text_columns": self.text_columns,
                    "column_headers_list": self.column_headers_list,
                    "drop_columns": False,
                }
            )

            trans_obj.fit(X)
            self.transformer_objs.append(trans_obj)

        return self

    def transform(self, X, y=None):
        if self.is_first:
            text_col_headers = []
        if self.activate_flag and len(self.text_columns) > 0:
            X[:, self.text_columns] = self.replace_special_chars(X[:, self.text_columns])
            transformed_data = X
            for trans_obj in self.transformer_objs:
                data = trans_obj.transform(X)
                transformed_data = np.hstack((transformed_data, data[:, X.shape[1] :]))
                if self.is_first:
                    text_col_headers += trans_obj.column_headers_list[X.shape[1] :].copy()

            if self.is_first:
                self.is_first = False
                if len(self.text_columns) > 0:
                    self.columns_added_flag = True
                column_headers_list = self.column_headers_list.copy() + text_col_headers

                if len(self.columns_to_be_deleted) > 0:
                    for col in sorted(self.columns_to_be_deleted, reverse=True):
                        column_headers_list.remove(column_headers_list[col])

                self.column_headers_list = column_headers_list

            if len(self.columns_to_be_deleted) > 0:
                transformed_data = np.delete(transformed_data, np.s_[self.columns_to_be_deleted], axis=1)

        else:
            transformed_data = X
        return transformed_data


class SmallDataTextTransformer(BaseEstimator, TransformerMixin):
    """
    Every text transformer must extend from this class.
    """

    def __init__(self, transformer_name):
        """
        Name of the child transformer for which fit and transform is being run
        """
        self.drop_columns = False
        self.transformer_name = transformer_name
        self.additional_columns = {}
        self.first_time = True
        self.columns_added_flag = False

    @property
    def column_headers_list(self):
        return self._column_headers_list

    @column_headers_list.setter
    def column_headers_list(self, value):
        self._column_headers_list = value if value else []

    @property
    def text_columns(self):
        return self._text_columns

    @text_columns.setter
    def text_columns(self, value):
        self._text_columns = value
        if self.text_columns is not None and not len(self.text_columns) == 0:
            self.columns_added_flag = True

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        new_data = X

        prev_col_list = self.column_headers_list.copy()
        if not prev_col_list:
            prev_col_list = ["" for item in self.text_columns]
        if self.first_time:
            column_headers_list = []

        for index, col in enumerate(self.text_columns):
            last_col = new_data.shape[1]
            feature = self.generate_feature(index, X[:, col])
            col_index = col if col < len(prev_col_list) else index

            new_data = np.hstack((new_data, feature))
            if self.drop_columns:
                self.additional_columns[
                    "{}_{}_{}({})".format("NewTextFeature", col, self.transformer_name, prev_col_list[col_index])
                ] = list(
                    range(
                        last_col - len(self.text_columns),
                        new_data.shape[1] - len(self.text_columns),
                    )
                )
            else:
                self.additional_columns[
                    "{}_{}_{}({})".format("NewTextFeature", col, self.transformer_name, prev_col_list[col_index])
                ] = list(range(last_col - X.shape[1], new_data.shape[1] - X.shape[1]))

            if self.first_time:
                column_headers_list += list(
                    map(
                        lambda x: "{}_{}_{}({})_{}".format(
                            "NewTextFeature", x, self.transformer_name, prev_col_list[col_index], x
                        ),
                        self.additional_columns[
                            "{}_{}_{}({})".format(
                                "NewTextFeature", col, self.transformer_name, prev_col_list[col_index]
                            )
                        ],
                    )
                )

        if self.first_time:
            self.column_headers_list = prev_col_list + column_headers_list
            self.first_time = False

        if self.drop_columns:
            new_data = np.delete(new_data, np.s_[self.text_columns], axis=1)

        return new_data

    def generate_feature(self, index, column):
        raise NotImplementedError("Please Implement this method")


class Word2VecTransformer(SmallDataTextTransformer):
    def __init__(
        self,
        output_dim=30,
        column_headers_list=[],
        svd_num_iter=5,
        drop_columns=False,
        activate_flag=True,
        min_count=5,
        text_columns=None,
        text_processing_options={},
    ):
        """
        column_headers_list: Column headers passed from autoai_core. The new feature's column headers are
            appended to this.
        drop_columns: If true, drops text columns
        activate_flag: If False, the features are not generated.
        output_dim: The dimensions of every generated feature.
        svd_num_iter: Number of iterations for which svd was run
        min_count: Word2vec model ignores all the words whose frequency is less than this
        text_columns: If passed, then word2vec features are applied to these columns
        text_processing_options: The parameter values to initialize this transformer are passed through this dictionary
        """
        super(Word2VecTransformer, self).__init__("word2vec")

        self.output_dim = output_dim
        self.svd_num_iter = svd_num_iter
        self.text_columns = text_columns
        self.activate_flag = activate_flag
        self.w2v_models = []
        self.truncated_svd = []
        self.min_count = min_count
        self.column_headers_list = column_headers_list
        self.is_svd_fit = []
        self.prev_fit_size = []
        self.drop_columns = drop_columns
        self.rng = np.random.default_rng(seed=SEED)

        if len(text_processing_options.keys()) > 0:
            if "output_dim" in text_processing_options:
                self.output_dim = text_processing_options["output_dim"]
            if "column_headers_list" in text_processing_options:
                self.column_headers_list = text_processing_options["column_headers_list"]
            if "svm_num_iter" in text_processing_options:
                self.svd_num_iter = text_processing_options["svm_num_iter"]
            if "drop_columns" in text_processing_options:
                self.drop_columns = text_processing_options["drop_columns"]
            if "text_columns" in text_processing_options:
                self.text_columns = text_processing_options["text_columns"]

        self.pca_max_size = 50000

    def fit(self, X, y=None):
        if self.text_columns is None:
            small_data_detector = SmallDataTextDetector()
            self.text_columns = small_data_detector.detect_string_type(X)

        self.w2v_models = [None] * len(self.text_columns)
        self.truncated_svd = [None] * len(self.text_columns)
        self.is_svd_fit = [False] * len(self.text_columns)
        self.prev_fit_size = [0] * len(self.text_columns)

        for index, col in enumerate(self.text_columns):
            self.truncated_svd[index] = PCA(n_components=self.output_dim)

        for index, col in enumerate(self.text_columns):
            words = list(map(lambda x: [word for word in x.split()], X[:, col]))
            if gensim_major_version >= 4:
                self.w2v_models[index] = Word2Vec(words, min_count=self.min_count, vector_size=50, workers=4)
            else:
                self.w2v_models[index] = Word2Vec(words, min_count=self.min_count, size=50, workers=4)
        return self

    def generate_feature(self, index, column_val):
        reduced_embeddings = np.zeros((len(column_val), self.output_dim))
        w2v_embeddings = np.zeros((len(column_val), 50))

        batch_size = 8000
        num_batches = _compute_num_batches(column_val, batch_size)
        for batch_num in range(num_batches):
            end_index = _compute_end_index(column_val, batch_num, num_batches, batch_size)

            words = list(
                map(
                    lambda x: [word for word in x.split()],
                    column_val[batch_num * batch_size : end_index],
                )
            )
            embeddings = list(map(lambda x: self.w2v_for_sentence(self.w2v_models[index], x), words))
            w2v_embeddings[batch_num * batch_size : end_index] = np.nan_to_num(embeddings)

        if self.prev_fit_size[index] < len(w2v_embeddings) and not self.prev_fit_size[index] == self.pca_max_size:
            if len(w2v_embeddings) < self.pca_max_size:
                subset_data = w2v_embeddings
            else:
                subset_indices = self.rng.choice(len(w2v_embeddings), self.pca_max_size, replace=False)
                subset_data = w2v_embeddings[subset_indices]

            self.truncated_svd[index].fit(subset_data)
            self.is_svd_fit[index] = True
            self.prev_fit_size[index] = len(subset_data)

        for batch_num in range(num_batches):
            end_index = _compute_end_index(column_val, batch_num, num_batches, batch_size)
            reduced_embeddings[batch_num * batch_size : end_index] = self.truncated_svd[index].transform(
                w2v_embeddings[batch_num * batch_size : end_index]
            )
        return reduced_embeddings

    def w2v_for_sentence(self, train_w2v, words):
        vec = np.zeros(50)
        count = 0
        for word in words:
            try:
                if word in train_w2v.wv:
                    vec += train_w2v.wv[word]
                    count += 1
            except BaseException:
                pass
        if count == 0:
            count = 1
        return vec / count
