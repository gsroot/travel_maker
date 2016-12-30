from pprint import pprint
from statistics import mean

import nltk
import pickle
from konlpy.tag import Twitter

from travel_maker.blog_data_collector.models import BlogData


class Analizer:
    def run(self):
        print("{} running...".format(self.__class__.__name__))


class BlogDataAnalizer(Analizer):
    train_rating_path = 'travel_maker/data_analysis/ratings_train.txt'
    test_rating_path = 'travel_maker/data_analysis/ratings_test.txt'
    selected_words_path = 'travel_maker/data_analysis/selected_words.pickle'
    words_and_ox_set = None

    def __init__(self):
        self.pos_tagger = Twitter()

    def get_rating_filepath(self, target):
        filepath_dict = {
            'train': self.train_rating_path,
            'test': self.test_rating_path
        }

        return filepath_dict[target]

    def read_data(self, filepath):
        with open(filepath, 'r') as f:
            data = [line.split('\t') for line in f.read().splitlines()]
            data = data[1:]  # header 제외
        return data

    def tokenize(self, sentence):
        return ['/'.join(res) for res in self.pos_tagger.pos(sentence, norm=True, stem=True)]

    def text_features(self, words):
        selected_words = self.load_selected_words()
        return {'include({})'.format(sel_word): True for sel_word in selected_words if sel_word in words}

    def save_classifier(self, classifier):
        with open('travel_maker/data_analysis/classifier.pickle', 'wb') as f:
            pickle.dump(classifier, f, -1)

    def load_classifier(self):
        with open('travel_maker/data_analysis/classifier.pickle', 'rb') as f:
            classifier = pickle.load(f)

        return classifier

    def save_selected_words(self, selected_words):
        filepath = self.selected_words_path
        with open(filepath, 'wb') as f:
            pickle.dump(selected_words, f, -1)

    def load_selected_words(self):
        filepath = self.selected_words_path
        try:
            with open(filepath, 'rb') as f:
                selected_words = pickle.load(f)
        except IOError:
            words_and_ox_set = self.get_words_and_ox_set('train')
            text = nltk.Text([t for feature in words_and_ox_set for t in feature[0]], name='NMSC')
            selected_words = [f[0] for f in text.vocab().most_common(2000)]
            self.save_selected_words(selected_words)

        return selected_words

    def get_words_and_ox_set(self, target):
        if not self.words_and_ox_set:
            filepath = self.get_rating_filepath(target)
            self.words_and_ox_set = [(self.tokenize(row[1]), row[2]) for row in self.read_data(filepath)]

        return self.words_and_ox_set

    def get_featureset(self, target):
        words_and_ox_set = self.get_words_and_ox_set(target)

        words_and_ox_set = words_and_ox_set[:10000]
        featureset = [
            (self.text_features(words_and_ox[0]), words_and_ox[1])
            for words_and_ox in words_and_ox_set
            ]

        return featureset

    def get_trainset(self):
        return self.get_featureset('train')

    def get_testset(self):
        return self.get_featureset('test')

    def get_train_classifier(self):
        train_set = self.get_trainset()
        classifier = nltk.NaiveBayesClassifier.train(train_set)
        test_set = self.get_testset()
        print('트레이닝된 classfier의 정확도는 {}% 입니다'.format(100 * nltk.classify.accuracy(classifier, test_set)))
        classifier.show_most_informative_features(1000)

        self.save_classifier(classifier)

        return classifier

    def run(self):
        super().run()

        try:
            classifier = self.load_classifier()
        except IOError:
            classifier = self.get_train_classifier()

        # TODO: 블로그별 점수 저장, 여행지 점수 산정
        blogs = BlogData.objects.filter(travel_info__title__contains='함덕')[:30]

        points = []
        for blog in blogs:
            print(blog.title)
            score = [0, 0]

            words = self.tokenize(blog.text)
            if classifier.classify(self.text_features(words)) == '1':
                score[0] += 1
            elif classifier.classify(self.text_features(words)) == '0':
                score[1] += 1

            print(score)
            point = (score[0] / (score[0] + score[1]))
            points.append(point)
        print(mean(points))
