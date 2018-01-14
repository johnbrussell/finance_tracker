from collections import namedtuple
from datetime import datetime
import pandas as pd


QueueElement = namedtuple("QueueElement", ["category", "category_path", "prior_categories", "prior_amounts"])


class ReportingQueue:
    def __init__(self, transactions, category):
        self.REPORT = list()
        self._DF = transactions.copy()
        self._QUEUE = self._create_queue(category)
        self._TYPE = category

    def run_report(self):
        while self._QUEUE:
            self._add_level_to_report(self._QUEUE[0])
            self._QUEUE = self._QUEUE[1:]
        self.REPORT = pd.DataFrame(self.REPORT)
        self._order_columns()
        self.REPORT.to_csv('./reports/%s_%s.csv' %
                           (self._TYPE, datetime.strftime(datetime.today(), '%Y%m%d')), index=False)

    @staticmethod
    def _create_queue(category):
        return [QueueElement(category=category, category_path=category, prior_categories=list(),
                             prior_amounts=list())]

    def _add_level_to_report(self, qe):
        if self.REPORT:
            self.REPORT.append(dict())

        category, category_path, prior_categories, prior_amounts = \
            qe.category, qe.category_path, qe.prior_categories, qe.prior_amounts
        df = self._determine_subset(prior_categories, category)
        level = len(prior_categories) + 1
        amount = df['Amount'].sum()
        line_dict = {'Category': '%s: $%s' % (category_path, str(amount))}
        self.REPORT.append(line_dict)

        if 'Category%s' % str(level) in df.columns:
            df['Category%s' % str(level)] = df['Category%s' % str(level)].fillna('')
        else:
            df['Category%s' % str(level)] = ''
        sub_categories_full = df['Category%s' % str(level)].unique()
        sub_categories = [c for c in sub_categories_full if c]

        prior_categories = [category] + prior_categories
        prior_amounts = [amount] + prior_amounts

        for sub_cat in sub_categories:
            self._QUEUE.append(QueueElement(category=sub_cat,
                                            category_path='%s | %s' % (category_path, sub_cat),
                                            prior_categories=prior_categories,
                                            prior_amounts=prior_amounts))

            alt_level = 1
            if not prior_categories:
                break
            line_dict = {'Category': sub_cat}
            for prior_cat, prior_amt in zip(prior_categories, prior_amounts):
                sub_amt = df.loc[df['Category%s' % str(level)] == sub_cat, 'Amount'].sum()
                sub_prc = round(float(sub_amt) / float(prior_amt) * float(100), 2)
                line_dict['%s%s' % ('%', str(alt_level))] = '%s%s of %s' % (sub_prc, '%', prior_cat)
                alt_level += 1
            self.REPORT.append(line_dict)

        empty_df = df[df['Category%s' % str(level)] == ''].copy()
        if not empty_df.empty:
            self._analyze_to(prior_categories, prior_amounts, empty_df)

    def _determine_subset(self, prior_categories, new_category):
        df = self._DF.copy()
        prior_categories = [new_category] + prior_categories
        level = len(prior_categories[:-1])
        for category in prior_categories[:-1]:
            df = df[df['Category%s' % level] == category]
            level -= 1
        return df

    def _order_columns(self):
        df = self.REPORT.copy()
        num_columns = len(df.columns)
        output_columns = ['Category']
        for col in range(1, num_columns):
            output_columns.append('%s%s' % ('%', str(col)))
        df = df[output_columns]
        self.REPORT = df.copy()

    def _analyze_to(self, prior_categories, prior_amounts, df):
        df = df.copy()
        sub_categories = list(df["To"].unique())
        for sub_cat in sub_categories:
            alt_level = 1
            line_dict = {'Category':
                         '{} ${}'.format(sub_cat, str(df.loc[df['To'] == sub_cat, 'Amount'].sum()))}
            for prior_cat, prior_amt in zip(prior_categories, prior_amounts):
                sub_amt = df.loc[df['To'] == sub_cat, 'Amount'].sum()
                sub_prc = round(float(sub_amt) / float(prior_amt) * float(100), 2)
                line_dict['%s%s' % ('%', str(alt_level))] = '%s%s of %s' % (sub_prc, '%', prior_cat)
                alt_level += 1
            self.REPORT.append(line_dict)
