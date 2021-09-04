import re
import stanza
import copy
import json
import pickle

from urlextract import URLExtract
from patterns_bag import get_patterns, sklearn_patterns, brew_patterns, emberjs_patterns, atom_patterns, bitcoin_patterns

from sklearn.metrics import f1_score, matthews_corrcoef, accuracy_score, precision_score, recall_score


GT_HEADER = 'label'


class PatternMatcher(object):

    def __init__(self, voc_dict=None, gnl_patterns_dict=None, spc_patterns_dict=None, split_vunit_flag=True, use_gpu=False, max_dist=3):
        self.nlp = stanza.Pipeline(processors='tokenize,pos,lemma', verbose=(1 if use_gpu else 0), use_gpu=use_gpu)
        
        default_voc_dict, default_gnl_patterns_dict, default_spc_patterns_dict = get_patterns()

        self.voc_dict = default_voc_dict if voc_dict is None else copy.deepcopy(voc_dict)
        self.spc_patterns_dict = default_spc_patterns_dict if spc_patterns_dict is None else copy.deepcopy(spc_patterns_dict)
        self.check_pattern_dict(self.spc_patterns_dict)


        self.split_vunit_flag = split_vunit_flag
        self.gnl_patterns_dict = default_gnl_patterns_dict if gnl_patterns_dict is None else copy.deepcopy(gnl_patterns_dict)
        if self.split_vunit_flag:
            self.gnl_patterns_dict = self.split_vunit(self.gnl_patterns_dict, self.voc_dict)
        else:
            self.check_pattern_dict(self.gnl_patterns_dict)
        
        self.url_extractor = URLExtract()
        self.MAX_DIST = max_dist


    @staticmethod
    def check_pattern_dict(patterns_dict):
        pattern_names = list(patterns_dict.keys())
        for i in range(len(pattern_names)):
            curr_pattern_name = pattern_names[i]
            for j in range(i + 1, len(pattern_names)):
                diff_pattern_name = pattern_names[j]
                for curr_pattern in patterns_dict[curr_pattern_name]:
                    if type(curr_pattern) != str:
                        temp_curr_pattern = [((item[0], 'wl') if item[1] in ['w', 'l'] else item) for item in curr_pattern]
                    else:
                        temp_curr_pattern = curr_pattern
                    for diff_pattern in patterns_dict[diff_pattern_name]:
                        if type(diff_pattern) != str:
                            temp_diff_pattern = [((item[0], 'wl') if item[1] in ['w', 'l'] else item) for item in diff_pattern]
                        else:
                            temp_diff_pattern = diff_pattern
                        
                        if temp_curr_pattern == temp_diff_pattern:
                            print('pattern conflict')
                            print ((curr_pattern_name, diff_pattern_name))
                            print (curr_pattern)


    @staticmethod
    def split_vunit(gnl_patterns_dict, voc_dict):
        tar_gnl_patterns_dict = {}
        for pattern_name in gnl_patterns_dict:
            if pattern_name not in tar_gnl_patterns_dict:
                tar_gnl_patterns_dict[pattern_name] = []
            for pattern_mode in gnl_patterns_dict[pattern_name]:
                patterns = []
                for unit_idx in range(len(pattern_mode)):
                    pattern_unit = pattern_mode[unit_idx]
                    unit0 = pattern_unit[0].split('|')
                    unit1 = pattern_unit[1].split('|')

                    next_node_list = []
                    for tar, tp in zip(unit0, unit1):
                        if tp != 'v':
                            next_node_list.append([(tar, tp)])
                        else:
                            voc = voc_dict[tar]
                            for voc_word in voc:
                                next_node_list.append([(voc_word, 'wl')])

                    if unit_idx == 0:
                        patterns.extend(next_node_list)
                    else:
                        while len(patterns[0]) <= unit_idx:
                            curr_node = patterns.pop(0)
                            for next_node in next_node_list:
                                node = copy.deepcopy(curr_node)
                                node.append(next_node[0])
                                patterns.append(node)

                    for diff_pattern_name in tar_gnl_patterns_dict:
                        if diff_pattern_name == pattern_name:
                            continue
                        for diff_patterns_tuple in tar_gnl_patterns_dict[diff_pattern_name]:
                            for curr_pattern in patterns:
                                temp_curr_pattern = [((item[0], 'wl') if item[1] in ['w', 'l'] else item) for item in curr_pattern]
                                for diff_pattern in diff_patterns_tuple[1]:
                                    temp_diff_pattern = [((item[0], 'wl') if item[1] in ['w', 'l'] else item) for item in diff_pattern]
                                    if temp_curr_pattern == temp_diff_pattern:
                                        print('pattern conflict')
                                        print ((pattern_name, diff_pattern_name))
                                        print (curr_pattern)

                tar_gnl_patterns_dict[pattern_name].append((pattern_mode, patterns))
        return tar_gnl_patterns_dict


    def spc_match(self, content, retain_list=None):
        content = re.sub(r' +', ' ', content)
        match = {}
        for pattern_name in self.spc_patterns_dict:
            for pattern in self.spc_patterns_dict[pattern_name]:
                
                if retain_list is not None and pattern not in retain_list:
                    continue

                text = content
                if '<URL>' in pattern:
                    urls = self.url_extractor.find_urls(text)
                    for url in urls:
                        text = text.replace(url, '<URL>')

                if re.search(pattern, text, re.I):
                    if pattern_name not in match:
                        match[pattern_name] = []
                    if pattern not in match[pattern_name]:
                        match[pattern_name].append(pattern)

        if len(match) > 0:
            label = list(match.keys())
            label.sort()
            label = ','.join(label)
        else:
            label = 'N'
        return match, label


    def unit_match(self, pattern_units, words):
        phrase = ' '.join([word.text for word in words])
        lemma = ' '.join([word.lemma for word in words])
        upos = words[0].upos if len(words) == 1 else None

        match_list = []
        for unit_tuple in pattern_units:
            unit_0 = unit_tuple[0].split('|')
            unit_1 = unit_tuple[1].split('|')
            if len(unit_0) != len(unit_1):
                raise Exception(print('pattern error'))
            for tar, tp in zip(unit_0, unit_1):
                if tp == 'v':
                    flag = phrase in self.voc_dict[tar] or lemma in self.voc_dict[tar] or phrase.lower() in self.voc_dict[tar] or lemma.lower() in self.voc_dict[tar]
                elif tp == 'w':
                    flag = phrase == tar or phrase.lower() == tar.lower()
                elif tp == 'p':
                    flag = upos in tar.split('|')
                elif tp == 'l':
                    flag = lemma == tar or lemma.lower() == tar.lower()
                elif tp == 'wl':
                    flag = phrase == tar or lemma == tar or phrase.lower() == tar.lower() or lemma.lower() == tar.lower()

                if flag:
                    match_list.append(unit_tuple)
                    break
        return match_list


    def pattern_match_check(self, idx_path, pattern, pattern_match, path_list):
        if pattern == []:
            path_list.append(idx_path)
        else:
            match_unit = pattern[0]
            if match_unit not in pattern_match:
                return
            match_list = pattern_match[match_unit]
            for idx_tuple in match_list:
                if len(idx_path) == 0 or (idx_tuple[0] > idx_path[-1][1] and idx_tuple[0] - idx_path[-1][1] <= self.MAX_DIST):
                    self.pattern_match_check(idx_path + [idx_tuple], pattern[1:], pattern_match, path_list)


    def get_match_texts(self, sentence, path_list):
        texts = []
        for idx_path in path_list:
            words = []
            for idx_tuple in idx_path:
                words.extend(sentence.words[idx_tuple[0] - 1:idx_tuple[1]])
            words_text = [word.text.lower() for word in words]
            words_lemma = [word.lemma.lower() for word in words]
            text = ' '.join(words_text)
            lemma = ' '.join(words_lemma)
            texts.append((text, lemma))
        return texts
        

    def gnl_match(self, content, retain_list=None):
        doc = self.nlp(content)
        match = {}
        match_content = {}
        for sentence in doc.sentences:
            for pattern_name in self.gnl_patterns_dict:
                for pattern_mode in self.gnl_patterns_dict[pattern_name]:
                    
                    if self.split_vunit_flag:
                        patterns = pattern_mode[1]
                        pattern_mode = pattern_mode[0]
                    else:
                        patterns = [pattern_mode]

                    for pattern in patterns:

                        if retain_list is not None and pattern not in retain_list:
                            continue

                        last_word_idx = -1
                        end_units = []
                        if pattern[-1][1] == 'e':
                            end_idx = -1
                            while abs(end_idx) <= len(sentence.words) and sentence.words[end_idx].upos != 'PUNCT':
                                end_idx -= 1
                            if abs(end_idx) <= len(sentence.words) and sentence.words[end_idx].text == pattern[-1][0]:
                                last_word_idx = sentence.words[end_idx].id
                                end_units = [pattern[-1]]
                                pattern = pattern[:-1]
                            else:
                                continue
                        
                        pattern_match = {}
                        for i in range(len(sentence.words)):
                            curr_match_idx = len(pattern_match)
                            word = sentence.words[i]
                            match_list = self.unit_match(pattern_units=pattern[:curr_match_idx + 1], words=[word])
                            for match_unit in match_list:
                                if match_unit not in pattern_match:
                                    pattern_match[match_unit] = []
                                start_id = sentence.words[i].id
                                end_id = sentence.words[i].id
                                pattern_match[match_unit].append((start_id, end_id))

                            if i + 1 < len(sentence.words):
                                match_list = self.unit_match(pattern_units=pattern[:curr_match_idx + 1], words=sentence.words[i:i + 2])
                                for match_unit in match_list:
                                    if match_unit not in pattern_match:
                                        pattern_match[match_unit] = []
                                    start_id = sentence.words[i].id
                                    end_id = sentence.words[i + 1].id
                                    pattern_match[match_unit].append((start_id, end_id))

                            if i + 2 < len(sentence.words):
                                match_list = self.unit_match(pattern_units=pattern[:curr_match_idx + 1], words=sentence.words[i:i + 3])
                                for match_unit in match_list:
                                    if match_unit not in pattern_match:
                                        pattern_match[match_unit] = []
                                    start_id = sentence.words[i].id
                                    end_id = sentence.words[i + 2].id
                                    pattern_match[match_unit].append((start_id, end_id))
                        
                        path_list = []
                        self.pattern_match_check([], pattern, pattern_match, path_list)
                        if last_word_idx != -1:
                            pattern.extend(end_units)
                            path_list = [idx_path + [(last_word_idx, last_word_idx)] for idx_path in path_list if idx_path[-1][1] < last_word_idx]
                        if len(path_list) > 0:
                            match_texts = self.get_match_texts(sentence, path_list)
                            if pattern_name not in match:
                                match[pattern_name] = []
                                match_content[pattern_name] = []
                            if pattern not in match[pattern_name]:
                                match[pattern_name].append(pattern)
                            if self.split_vunit_flag:
                                match_content[pattern_name].append((pattern_mode, pattern, match_texts))
                            else:
                                match_content[pattern_name].append((pattern_mode, match_texts))

        if len(match) > 0:
            label = list(match.keys())
            label.sort()
            label = ','.join(label)
        else:
            label = 'N'
        return match, label, match_content


import os
import tqdm
import pandas as pd
import numpy as np
from multiprocessing import Pool


def get_repo_name(filename):
    if 'bitcoin' in filename:
        return 'bitcoin'
    elif 'atom' in filename:
        return 'atom'
    elif 'brew' in filename:
        return 'brew'
    elif 'scikit-learn' in filename or 'sklearn' in filename:
        return 'sklearn'
    elif 'ember.js' in filename:
        return 'ember.js'
    elif 'bokeh' in filename:
        return 'bokeh'
    elif 'efcore' in filename:
        return 'efcore'
    elif 'knex' in filename:
        return 'knex'
    elif 'roslyn' in filename:
        return 'roslyn'
    elif 'solidity' in filename:
        return 'solidity'


def make_global(voc_dict=None, gnl_patterns_dict=None, spc_patterns_dict=None, split_vunit_flag=True, use_gpu=False, retain_list=None):
    global matcher
    matcher = PatternMatcher(voc_dict, gnl_patterns_dict, spc_patterns_dict, split_vunit_flag, use_gpu)
    global g_retain_list
    g_retain_list = retain_list
    # if g_retain_list is not None:
    #     print(len(g_retain_list))


def pred_unit(content):
    content = content.strip()
    if content == '':
        return {}, 'N', {}, 'N', {}
    gnl_match, gnl_label, match_content = matcher.gnl_match(content, g_retain_list)
    spc_match, spc_label = matcher.spc_match(content, g_retain_list)
    return gnl_match, gnl_label, spc_match, spc_label, match_content


def get_hits(true_labels, pred_labels):
    hit = []
    # pred_labels = [it if it != '' else 'N' for it in pred_labels]
    for y_true, y_pred in zip(true_labels, pred_labels):
        if y_true != '':
            # if y_true == y_pred:
            if y_true in y_pred or (y_true == 'N' and y_pred == ''):
                hit.append('Y')
            else:
                hit.append('N')
        else:
            hit.append('')
    return hit


def get_gs_hits(true_labels, gnl_labels, spc_labels):
    hit = []
    for y_true, y_gnl, y_spc in zip(true_labels, gnl_labels, spc_labels):
        if y_true != '':
            if y_true in y_spc or y_true in y_gnl or (y_true == 'N' and y_gnl == '' and y_spc == ''):
                hit.append('Y')
            else:
                hit.append('N')
        else:
            hit.append('')
    return hit


def pattern_range_count(true_labels, matches, gs_hit):
    pattern_hit = {}
    for y_true, match, hit in zip(true_labels, matches, gs_hit):
        for label in match:
            idx = 1 if y_true == label else 0
            for pattern in match[label]:
                key = str(pattern)
                if key not in pattern_hit:
                    pattern_hit[key] = [0, 0, 0, pattern, label]
                pattern_hit[key][idx] += 1
                if hit == 'N' and (y_true == 'N' or y_true not in match):
                    pattern_hit[key][2] += 1
    return pattern_hit


def get_rank_labels(matches, rank_list, discard_list=None):
    ranked_labels = []
    first_patterns = []

    # rank_list_dict = {}
    # for i in range(len(rank_list)):
    #     rank_list_dict[str(rank_list[i])] = i

    for match in matches:

        # ranked_match_triples = []
        pos = None
        ranked_label = 'N'
        first_pattern = ''
        for tag in match:
            for pattern in match[tag]:
                if discard_list is not None and pattern in discard_list:
                    continue

                if pattern not in rank_list:
                    continue
                # if str(pattern) not in rank_list_dict:
                #     continue

                # ranked_match_triples.append((pattern, tag, rank_list.index(pattern)))
                # ranked_match_triples.append((pattern, tag, rank_list_dict[str(pattern)]))

                idx = rank_list.index(pattern)
                if pos is None or idx < pos:
                    pos = idx
                    ranked_label = tag
                    first_pattern = pattern
        # if len(ranked_match_triples) == 0:
        #     ranked_labels.append('N')
        #     first_patterns.append('')
        #     continue

        # ranked_match_triples.sort(key=lambda x: x[2])
        # ranked_labels.append(ranked_match_triples[0][1])
        # first_patterns.append(ranked_match_triples[0][0])
    
        ranked_labels.append(ranked_label)
        first_patterns.append(first_pattern)
        
    return ranked_labels, first_patterns


def get_pm_res(res_dict, ret_true=True):
    matches = []
    true_labels = []
    for key in res_dict:
        data = res_dict[key]
        for _, row in data.iterrows():
            if ret_true:
                true_labels.append(row[GT_HEADER])
            match = {}
            match.update(copy.deepcopy(row['gnl_match']))
            for tag in row['spc_match']:
                if tag not in match:
                    match[tag] = []
                match[tag].extend(copy.deepcopy(row['spc_match'][tag]))
            matches.append(match)

    return matches, true_labels


def get_metric(true_labels, pred_labels, mode):
    if mode == 'acc':
        # hits = get_hits(true_labels, pred_labels)
        # metric_val = hits.count('Y') / (hits.count('Y') + hits.count('N'))
        metric_val = accuracy_score(true_labels, pred_labels)
    elif mode == 'corr':
        metric_val = get_correctness(true_labels, pred_labels)
    elif mode == 'mis':
        metric_val = get_misclassification(true_labels, pred_labels)
    elif mode == 'mcc':
        metric_val = matthews_corrcoef(true_labels, pred_labels)
    elif mode == 'f-macro':
        metric_val = f1_score(true_labels, pred_labels, average='macro')
    elif mode == 'f-micro':
        metric_val = f1_score(true_labels, pred_labels, average='micro')
    elif mode == 'p-macro':
        metric_val = precision_score(true_labels, pred_labels, average='macro')
    elif mode == 'p-micro':
        metric_val = precision_score(true_labels, pred_labels, average='micro')
    elif mode == 'r-macro':
        metric_val = recall_score(true_labels, pred_labels, average='macro')
    elif mode == 'r-micro':
        metric_val = recall_score(true_labels, pred_labels, average='micro')
    else:
        raise Exception('Please select mode')
    return metric_val


def rank_matched_pattern(match, rank_list):
    ranked_match_triples = []
    for tag in match:
        for pattern in match[tag]:
            if pattern not in rank_list:
                continue
            ranked_match_triples.append((pattern, tag, rank_list.index(pattern)))
    ranked_match_triples.sort(key=lambda x: x[2])
    return ranked_match_triples


def init_pattern_rank(pattern_hit):
    pattern_strs = list(pattern_hit.keys())
    weights = [pattern_hit[key][0] / (pattern_hit[key][0] + pattern_hit[key][1]) for key in pattern_strs]
    idx_rank = np.argsort(weights)
    rank_list = [pattern_hit[pattern_strs[idx]][3] for idx in idx_rank]
    return rank_list


# def get_rank_labels_fast(matches_w_str, rank_list_dict, discard_list=None):
#     ranked_labels = []
#     first_patterns = []

#     for match in matches_w_str:
#         pos = None
#         ranked_label = 'N'
#         first_pattern = ''
#         for tag in match:
#             for item in match[tag]:
#                 pattern = item[0]
#                 pattern_str = item[1]
#                 if discard_list is not None and pattern in discard_list:
#                     continue
                
#                 try:
#                     idx = rank_list_dict[pattern_str]
#                 except KeyError:
#                     continue

#                 if pos is None or idx < pos:
#                     pos = idx
#                     ranked_label = tag
#                     first_pattern = pattern
    
#         ranked_labels.append(ranked_label)
#         first_patterns.append(first_pattern)
        
#     return ranked_labels, first_patterns


# import time

def insert_unit(args):
    position, rank_list_str, new_pattern_str, matches_table, prev_labels, prev_first_patterns, true_labels, mode = args

    # time_dict = {}

    # rank_list_dict = {}
    # for i in range(len(rank_list_str)):
    #     rank_list_dict[rank_list_str[i]] = i if i < position else i + 1
    # rank_list_dict[new_pattern] = position

    # time_start = time.perf_counter()
    retain_list_str = rank_list_str[:position]
    # temp_ranked_labels, temp_first_patterns = get_rank_labels_fast(matches_w_str, rank_list_dict)
    change_tuple = matches_table[new_pattern_str]
    change_tag = change_tuple[0]
    change_pattern = change_tuple[1]
    change_set = set(change_tuple[2])
    for pattern_str in retain_list_str:
        change_set -= matches_table[pattern_str][2]
    temp_ranked_labels = [(prev_labels[idx] if idx not in change_set else change_tag) for idx in range(len(prev_labels))]
    temp_first_patterns = [(prev_first_patterns[idx] if idx not in change_set else change_pattern) for idx in range(len(prev_first_patterns))]
    # time_end = time.perf_counter()
    # print ('Rank', time_end - time_start)
    # time_dict['Rank'] = time_end - time_start

    # time_start = time.perf_counter()
    temp_metric_val = get_metric(true_labels, temp_ranked_labels, mode)
    # time_end = time.perf_counter()
    # print ('Eval', time_end - time_start)
    # time_dict['Eval'] = time_end - time_start

    return temp_metric_val, temp_ranked_labels, temp_first_patterns, position


# def get_matches_w_str(matches):
#     matches_w_str = []

#     for match in matches:
#         match_w_str = {}
#         for tag in match:
#             if tag not in match_w_str:
#                 match_w_str[tag] = []
#             for pattern in match[tag]:
#                 match_w_str[tag].append((pattern, str(pattern)))
#         matches_w_str.append(match_w_str)
#     return matches_w_str


def get_matches_table(matches):
    matches_table = {}
    for i in range(len(matches)):
        match = matches[i]
        for tag in match:
            for pattern in match[tag]:
                key = str(pattern)
                if key not in matches_table:
                    matches_table[key] = (tag, pattern, set())
                matches_table[key][2].add(i)
    return matches_table


import time


def insert_rank(new_patterns, matches, true_labels, old_rank_list, mode, iter_num=-1):

    print ('Insert Patterns ...')

    # matches_w_str = get_matches_w_str(matches)
    matches_table = get_matches_table(matches)

    new_rank_list = copy.deepcopy(old_rank_list)
    new_rank_list_str = [str(item) for item in new_rank_list]

    new_ranked_labels, new_first_patterns = get_rank_labels(matches, new_rank_list)
    new_metric_val = get_metric(true_labels, new_ranked_labels, mode)

    new_patterns_seq = copy.deepcopy(new_patterns)
    new_patterns_seq_str = [str(item) for item in new_patterns_seq]
    update_flag = True

    with Pool() as pool:
        while update_flag:
            update_flag = False
            drop_patterns = []
            drop_patterns_str = []

            for new_pattern, new_pattern_str in zip(new_patterns_seq, new_patterns_seq_str):

                list_position_num = len(new_rank_list) + 1
                positions = list(range(list_position_num))
                # args_list = list(zip(positions, [new_rank_list] * list_position_num, [new_pattern] * list_position_num, [matches] * list_position_num, [true_labels] * list_position_num, [mode] * list_position_num))
                args_list = list(zip(positions, [new_rank_list_str] * list_position_num, [new_pattern_str] * list_position_num, [matches_table] * list_position_num, [new_ranked_labels] * list_position_num, [new_first_patterns] * list_position_num, [true_labels] * list_position_num, [mode] * list_position_num))

                time_start = time.perf_counter()
                res = pool.map(insert_unit, args_list)
                time_end = time.perf_counter()
                print ('\r' + str(len(args_list)) + ' ' + str(time_end - time_start), end='')

                # time_dict = {}
                # for item in res:
                #     for key in item[4]:
                #         if key not in time_dict:
                #             time_dict[key] = 0
                #         time_dict[key] += item[4][key]

                # for key in time_dict:
                #     time_dict[key] = np.round(time_dict[key], 5)
                # print ('\r' + str(len(args_list)) + ' ' + str(time_dict), end='')

                max_pos = max(res, key=lambda x: x[0])

                if max_pos[0] > new_metric_val:
                    new_metric_val = max_pos[0]
                    new_ranked_labels = max_pos[1]
                    new_first_patterns = max_pos[2]
                    new_rank_list.insert(max_pos[3], new_pattern)
                    new_rank_list_str.insert(max_pos[3], new_pattern_str)
                    drop_patterns.append(new_pattern)
                    drop_patterns_str.append(new_pattern_str)
                    update_flag = True

            new_patterns_seq = [pat for pat in new_patterns_seq if pat not in drop_patterns]
            new_patterns_seq_str = [pat for pat in new_patterns_seq_str if pat not in drop_patterns_str]
            if iter_num > 0:
                iter_num -= 1
            if iter_num == 0:
                break
    
    return new_rank_list, new_metric_val, new_ranked_labels, new_first_patterns


def update_rank(matches, true_labels, old_rank_list, mode, iter_num=-1):

    print ('Update Rank ...')

    new_rank_list = copy.deepcopy(old_rank_list)
    new_ranked_labels, new_first_patterns = get_rank_labels(matches, new_rank_list)
    new_metric_val = get_metric(true_labels, new_ranked_labels, mode)
    update_flag = True

    change_num = 0
    while update_flag:
        update_flag = False
        for y_true, match in zip(true_labels, matches):
            if y_true not in match:
                continue

            ranked_match_triples = rank_matched_pattern(match, new_rank_list)
            if len(ranked_match_triples) == 0:
                continue

            y_pred = ranked_match_triples[0][1]
            if y_true == y_pred:
                continue

            real_wins = [new_rank_list.index(pattern) for pattern in match[y_true] if pattern in new_rank_list]
            if len(real_wins) == 0:
                continue
            real_win = min(real_wins)

            first_pattern = ranked_match_triples[0][0]
            fake_win = new_rank_list.index(first_pattern)
            if real_win < fake_win:
                continue

            temp_rank_list = copy.deepcopy(new_rank_list)
            temp_rank_list.insert(fake_win, temp_rank_list.pop(real_win))

            temp_ranked_labels, temp_first_patterns = get_rank_labels(matches, temp_rank_list)
            temp_metric_val = get_metric(true_labels, temp_ranked_labels, mode)

            if temp_metric_val > new_metric_val:
                new_metric_val = temp_metric_val
                new_ranked_labels = temp_ranked_labels
                new_first_patterns = temp_first_patterns
                new_rank_list = temp_rank_list
                update_flag = True
                change_num += 1

        if iter_num > 0:
            iter_num -= 1
        if iter_num == 0:
            break

    print ('Change Num:', change_num)
    return new_rank_list, new_metric_val, new_ranked_labels, new_first_patterns


def discard_pattern(matches, true_labels, old_rank_list, mode, iter_num=-1, redundant=False):

    print ('Discard Rank ...')

    new_rank_list = copy.deepcopy(old_rank_list)
    new_ranked_labels, new_first_patterns = get_rank_labels(matches, new_rank_list)
    new_metric_val = get_metric(true_labels, new_ranked_labels, mode)
    update_flag = True

    while update_flag:
        update_flag = False
        for y_true, match in zip(true_labels, matches):

            ranked_match_triples = rank_matched_pattern(match, new_rank_list)
            if len(ranked_match_triples) == 0:
                continue

            y_pred = ranked_match_triples[0][1]
            if y_true == y_pred:
                continue

            if y_true in match:
                real_wins = [new_rank_list.index(pattern) for pattern in match[y_true] if pattern in new_rank_list]
                if len (real_wins) == 0:
                    continue
                real_win = min(real_wins)
            elif y_true == 'N':
                real_win = None
            else:
                continue

            discard_list = []
            for tag in match:
                for pattern in match[tag]:
                    if pattern in new_rank_list:
                        fake_win = new_rank_list.index(pattern)
                        if real_win is not None and real_win <= fake_win:
                            continue
                        discard_list.append(pattern)

            temp_ranked_labels, temp_first_patterns = get_rank_labels(matches, new_rank_list, discard_list)

            temp_metric_val = get_metric(true_labels, temp_ranked_labels, mode)

            if temp_metric_val > new_metric_val:
                new_metric_val = temp_metric_val
                new_ranked_labels = temp_ranked_labels
                new_first_patterns = temp_first_patterns
                new_rank_list = [pattern for pattern in new_rank_list if pattern not in discard_list]
                update_flag = True

        if iter_num > 0:
            iter_num -= 1
        if iter_num == 0:
            break
    
    if redundant:
        return new_rank_list, new_metric_val, new_ranked_labels, new_first_patterns
    else:
        return remove_redundant(matches, true_labels, new_rank_list, mode)


def remove_redundant(matches, true_labels, old_rank_list, mode, iter_num=-1):

    new_rank_list = copy.deepcopy(old_rank_list)
    new_ranked_labels, new_first_patterns = get_rank_labels(matches, new_rank_list)
    new_metric_val = get_metric(true_labels, new_ranked_labels, mode)
    update_flag = True

    while update_flag:
        update_flag = False
        pattern_list = copy.deepcopy(new_rank_list)
        # for pattern in new_rank_list:
        for pattern in pattern_list:
            discard_list = [pattern]
            temp_ranked_labels, temp_first_patterns = get_rank_labels(matches, new_rank_list, discard_list)
            temp_metric_val = get_metric(true_labels, temp_ranked_labels, mode)

            if temp_metric_val >= new_metric_val:
                new_metric_val = temp_metric_val
                new_ranked_labels = temp_ranked_labels
                new_first_patterns = temp_first_patterns
                new_rank_list.remove(pattern)
                # drop_patterns.append(pattern)
                update_flag = True

        # new_rank_list = [pat for pat in new_rank_list if pattern not in discard_list]
        if iter_num > 0:
            iter_num -= 1
        if iter_num == 0:
            break
    
    return new_rank_list, new_metric_val, new_ranked_labels, new_first_patterns


def get_correctness(true_labels, pred_labels):
    # pred_labels = [it if it != '' else 'N' for it in pred_labels]

    label_set = set(true_labels)
    if '' in label_set:
        label_set.remove('')

    correctness = 0.0
    for label in label_set:
        one_hot_true = []
        one_hot_pred = []
        for y_true, y_pred in zip(true_labels, pred_labels):
            if y_true == '':
                continue
            one_hot_true.append((1 if y_true == label else 0))
            one_hot_pred.append((1 if y_pred == label else 0))
        correctness += f1_score(one_hot_true, one_hot_pred)

    return correctness / len(label_set)


def get_misclassification(true_labels, pred_labels):
    # pred_labels = [it if it != '' else 'N' for it in pred_labels]
    label_set = set(true_labels)
    if '' in label_set:
        label_set.remove('')

    misclassification = 0.0
    for label in label_set:
        mis_num  = 0
        total_num = 0
        for y_true, y_pred in zip(true_labels, pred_labels):
            if y_true != label or y_true == '':
                continue
            mis_num += 1 if y_true != y_pred else 0
            total_num += 1
        misclassification += mis_num / total_num

    return misclassification / len(label_set)


def data_match(data_root, filename, voc_dict=None, gnl_patterns_dict=None, spc_patterns_dict=None, split_vunit_flag=True, pred=False, use_gpu=False, retain_list=None, n_rows=None, hit_insert=True, label_all=True):
    data_path = os.path.join(data_root, filename)
    data = pd.read_excel(data_path)
    data.fillna('', inplace=True)

    if n_rows is not None:
        data = data.iloc[:n_rows]

    if not label_all:
        data = data[data[GT_HEADER] != '']

    if len(data) == 0:
        return None
    
    if use_gpu:
        make_global(voc_dict, gnl_patterns_dict, spc_patterns_dict, split_vunit_flag, use_gpu, retain_list)
        res = []
        for content in tqdm.tqdm(data['comment_content'], total=len(data), ncols=100):
            res.append(pred_unit(content))
    else:
        with Pool(initializer=make_global, initargs=(voc_dict, gnl_patterns_dict, spc_patterns_dict, split_vunit_flag, use_gpu, retain_list)) as pool:
            res = list(tqdm.tqdm(pool.imap(pred_unit, data['comment_content']), total=len(data), ncols=100))

    gnl_matches = [item[0] for item in res]
    gnl_labels = [item[1] for item in res]
    spc_matches = [item[2] for item in res]
    spc_labels = [item[3] for item in res]
    gnl_match_contents = [item[4] for item in res]

    # if hit_insert:
    #     gnl_hits = get_hits(data[GT_HEADER], gnl_labels)
    #     spc_hits = get_hits(data[GT_HEADER], spc_labels)
    #     gs_hit = get_gs_hits(data[GT_HEADER], gnl_labels, spc_labels)

    #     col_idx = list(data.columns).index(GT_HEADER)
    #     data.insert(col_idx + 1, 'gnl_label', gnl_labels)
    #     data.insert(col_idx + 2, 'gnl_match', gnl_matches)
    #     data.insert(col_idx + 3, 'gnl_hit', gnl_hits)
    #     data.insert(col_idx + 4, 'gnl_match_content', gnl_match_contents)
    #     data.insert(col_idx + 5, 'spc_label', spc_labels)
    #     data.insert(col_idx + 6, 'spc_match', spc_matches)
    #     data.insert(col_idx + 7, 'spc_hit', spc_hits)
    #     data.insert(col_idx + 8, 'gs_hit', gs_hit)
    # else:
    #     col_idx = list(data.columns).index('time')

    #     data.insert(col_idx + 1, 'gnl_label', gnl_labels)
    #     data.insert(col_idx + 2, 'gnl_match', gnl_matches)
    #     data.insert(col_idx + 3, 'gnl_match_content', gnl_match_contents)
    #     data.insert(col_idx + 4, 'spc_label', spc_labels)
    #     data.insert(col_idx + 5, 'spc_match', spc_matches)
        
    col_idx = list(data.columns).index('comment_content')
    data.insert(col_idx + 1, 'gnl_match', gnl_matches)
    data.insert(col_idx + 2, 'spc_match', spc_matches)

    pj_matches, _ = get_pm_res({filename: data}, ret_true=False)
    pj_ranked_labels, _ = get_rank_labels(pj_matches, rank_list)

    data['pred_label'] = pj_ranked_labels
    return data[['comment_ID', 'comment_content', 'pred_label']]


def data_pd(project_id, data_root, save_root, filenames, mode, voc_dict=None, gnl_patterns_dict=None, spc_patterns_dict=None, rank_list=None, split_vunit_flag=True, use_gpu=False, table_root=None):

    pattern_hit = {}
    res_dict = {}

    for filename in filenames:
        if table_root is None:
            print ('Matching...')
            data = data_match(data_root, filename, voc_dict, gnl_patterns_dict, spc_patterns_dict, split_vunit_flag, use_gpu=use_gpu)
        else:
            repo_name = get_repo_name(filename)
            data_path = os.path.join(data_root, filename)
            tab_path = os.path.join(table_root, repo_name + '.csv')
            print ('From table:', tab_path)
            data = data_match_from_tab(data_path, tab_path, voc_dict, gnl_patterns_dict, spc_patterns_dict, split_vunit_flag)
        
        res_dict[filename] = data

        gnl_pattern_hit = pattern_range_count(data[GT_HEADER], data['gnl_match'], data['gs_hit'])
        spc_pattern_hit = pattern_range_count(data[GT_HEADER], data['spc_match'], data['gs_hit'])

        if len(set(gnl_pattern_hit.keys()).intersection(set(spc_pattern_hit.keys()))) > 0:
            print ('error')

        gnl_pattern_hit.update(spc_pattern_hit)

        for key in gnl_pattern_hit:
            if key not in pattern_hit:
                pattern_hit[key] = gnl_pattern_hit[key]
            else:
                pattern_hit[key][0] += gnl_pattern_hit[key][0]
                pattern_hit[key][1] += gnl_pattern_hit[key][1]
                pattern_hit[key][2] += gnl_pattern_hit[key][2]

    matches, true_labels = get_pm_res(res_dict)
    if rank_list is None:
        rank_list = []

    prev_rank_list = copy.deepcopy(rank_list)
    prev_ranked_labels, _ = get_rank_labels(matches, prev_rank_list)
    print ('##########################################################################################')
    print ('Prev Rank Len: ' + str(len(prev_rank_list)))
    print ('Prev Rank ACC: ' + str(get_metric(true_labels, prev_ranked_labels, 'acc')))
    print ('Prev Rank P-Macro: ' + str(get_metric(true_labels, prev_ranked_labels, 'p-macro')))
    print ('Prev Rank P-Micro: ' + str(get_metric(true_labels, prev_ranked_labels, 'p-micro')))
    print ('Prev Rank R-Macro: ' + str(get_metric(true_labels, prev_ranked_labels, 'r-macro')))
    print ('Prev Rank R-Micro: ' + str(get_metric(true_labels, prev_ranked_labels, 'r-micro')))
    print ('Prev Rank F-Macro: ' + str(get_metric(true_labels, prev_ranked_labels, 'f-macro')))
    print ('Prev Rank F-Micro: ' + str(get_metric(true_labels, prev_ranked_labels, 'f-micro')))
    print ('Prev Rank MCC: ' + str(get_metric(true_labels, prev_ranked_labels, 'mcc')))

    curr_rank_list = copy.deepcopy(rank_list)
    # curr_rank_list = []
    ext_rank_list = init_pattern_rank(pattern_hit)
    new_patterns = [pattern for pattern in ext_rank_list if pattern not in curr_rank_list]

    print ('##########################################################################################')
    curr_rank_list, _, _, _ = insert_rank(new_patterns, matches, true_labels, curr_rank_list, mode=mode)
    curr_ranked_labels, _ = get_rank_labels(matches, curr_rank_list)
    print ('Inserted Rank Len: ' + str(len(curr_rank_list)))
    print ('Inserted Rank ACC: ' + str(get_metric(true_labels, curr_ranked_labels, 'acc')))
    print ('Inserted Rank P-Macro: ' + str(get_metric(true_labels, curr_ranked_labels, 'p-macro')))
    print ('Inserted Rank P-Micro: ' + str(get_metric(true_labels, curr_ranked_labels, 'p-micro')))
    print ('Inserted Rank R-Macro: ' + str(get_metric(true_labels, curr_ranked_labels, 'r-macro')))
    print ('Inserted Rank R-Micro: ' + str(get_metric(true_labels, curr_ranked_labels, 'r-micro')))
    print ('Inserted Rank F-Macro: ' + str(get_metric(true_labels, curr_ranked_labels, 'f-macro')))
    print ('Inserted Rank F-Micro: ' + str(get_metric(true_labels, curr_ranked_labels, 'f-micro')))
    print ('Inserted Rank MCC: ' + str(get_metric(true_labels, curr_ranked_labels, 'mcc')))

    print ('##########################################################################################')
    curr_rank_list, _, _, _ = update_rank(matches, true_labels, curr_rank_list, mode=mode)
    curr_ranked_labels, _ = get_rank_labels(matches, curr_rank_list)
    print ('Updated Rank Len: ' + str(len(curr_rank_list)))
    print ('Updated Rank ACC: ' + str(get_metric(true_labels, curr_ranked_labels, 'acc')))
    print ('Updated Rank P-Macro: ' + str(get_metric(true_labels, curr_ranked_labels, 'p-macro')))
    print ('Updated Rank P-Micro: ' + str(get_metric(true_labels, curr_ranked_labels, 'p-micro')))
    print ('Updated Rank R-Macro: ' + str(get_metric(true_labels, curr_ranked_labels, 'r-macro')))
    print ('Updated Rank R-Micro: ' + str(get_metric(true_labels, curr_ranked_labels, 'r-micro')))
    print ('Updated Rank F-Macro: ' + str(get_metric(true_labels, curr_ranked_labels, 'f-macro')))
    print ('Updated Rank F-Micro: ' + str(get_metric(true_labels, curr_ranked_labels, 'f-micro')))
    print ('Updated Rank MCC: ' + str(get_metric(true_labels, curr_ranked_labels, 'mcc')))

    print ('##########################################################################################')
    curr_rank_list, _, _, _ = discard_pattern(matches, true_labels, curr_rank_list, mode=mode)
    curr_ranked_labels, _ = get_rank_labels(matches, curr_rank_list)
    print ('Discarded Rank Len: ' + str(len(curr_rank_list)))
    print ('Discarded Rank ACC: ' + str(get_metric(true_labels, curr_ranked_labels, 'acc')))
    print ('Discarded Rank P-Macro: ' + str(get_metric(true_labels, curr_ranked_labels, 'p-macro')))
    print ('Discarded Rank P-Micro: ' + str(get_metric(true_labels, curr_ranked_labels, 'p-micro')))
    print ('Discarded Rank R-Macro: ' + str(get_metric(true_labels, curr_ranked_labels, 'r-macro')))
    print ('Discarded Rank R-Micro: ' + str(get_metric(true_labels, curr_ranked_labels, 'r-micro')))
    print ('Discarded Rank F-Macro: ' + str(get_metric(true_labels, curr_ranked_labels, 'f-macro')))
    print ('Discarded Rank F-Micro: ' + str(get_metric(true_labels, curr_ranked_labels, 'f-micro')))
    print ('Discarded Rank MCC: ' + str(get_metric(true_labels, curr_ranked_labels, 'mcc')))
    print ('##########################################################################################')
    print ('')

    new_pattern_list = [pattern for pattern in curr_rank_list if pattern not in prev_rank_list]
    del_pattern_list = [pattern for pattern in prev_rank_list if pattern not in curr_rank_list]
    ad_dict = {'A': {}, 'D':{}}
    for pattern in new_pattern_list:
        tag = pattern_hit[str(pattern)][4]
        if tag not in ad_dict['A']:
            ad_dict['A'][tag] = []
        ad_dict['A'][tag].append(pattern)
    for pattern in del_pattern_list:
        tag = pattern_hit[str(pattern)][4]
        if tag not in ad_dict['D']:
            ad_dict['D'][tag] = []
        ad_dict['D'][tag].append(pattern)

    with open(os.path.join(save_root, str(project_id)), 'w') as fw:
        json.dump(ad_dict, fw)

    for filename in res_dict:
        data = res_dict[filename]
        pj_matches, pj_labels = get_pm_res({filename: data})
        pj_ranked_labels, pj_first_patterns = get_rank_labels(pj_matches, curr_rank_list)
        pj_hits = get_hits(pj_labels, pj_ranked_labels)

        pj_nondel_ranked_labels, pj_nondel_first_patterns =  get_rank_labels(pj_matches, prev_rank_list)
        pj_nondel_hits = get_hits(pj_labels, pj_nondel_ranked_labels)

        ad_influence = []
        hit_influence = []
        for pj_hit, pj_first_pattern, pj_nondel_hit, pj_nondel_first_pattern in zip(pj_hits, pj_first_patterns, pj_nondel_hits, pj_nondel_first_patterns):
            ad_state = ''
            if pj_first_pattern in new_pattern_list:
                ad_state += 'A'

            if pj_nondel_first_pattern in del_pattern_list:
                ad_state += 'D'

            if ad_state == '' and pj_first_pattern != pj_nondel_first_pattern:
                ad_state = 'R'

            pj_hit_v = 1 if pj_hit == 'Y' else 0
            pj_nondel_hit_v = 1 if pj_nondel_hit == 'Y' else 0

            hit_influence.append(pj_hit_v - pj_nondel_hit_v)
            ad_influence.append(ad_state)


        print ('***********************************************************************************')
        print (filename)
        if filename == filenames[project_id]:
            print ('-------------------------------------------------------------------------')
        print ('Project ACC: ' + str(get_metric(pj_labels, pj_ranked_labels, 'acc')))
        print ('Project P-Macro: ' + str(get_metric(pj_labels, pj_ranked_labels, 'p-macro')))
        print ('Project P-Micro: ' + str(get_metric(pj_labels, pj_ranked_labels, 'p-micro')))
        print ('Project R-Macro: ' + str(get_metric(pj_labels, pj_ranked_labels, 'r-macro')))
        print ('Project R-Micro: ' + str(get_metric(pj_labels, pj_ranked_labels, 'r-micro')))
        print ('Project F-Macro: ' + str(get_metric(pj_labels, pj_ranked_labels, 'f-macro')))
        print ('Project F-Micro: ' + str(get_metric(pj_labels, pj_ranked_labels, 'f-micro')))
        print ('Project MCC: ' + str(get_metric(pj_labels, pj_ranked_labels, 'mcc')))
        if filename == filenames[project_id]:
            print ('-------------------------------------------------------------------------')

        output_file = os.path.join(save_root, str(project_id) + '_pd_' + filename)

        col_idx = list(data.columns).index(GT_HEADER)
        data.insert(col_idx + 1, 'pred_label', pj_ranked_labels)
        data.insert(col_idx + 2, 'first_pattern', pj_first_patterns)
        data.insert(col_idx + 3, 'ranked_hit', pj_hits)
        data.insert(col_idx + 4, 'ad_influence', ad_influence)
        data.insert(col_idx + 5, 'hit_influence', hit_influence)
        data.insert(col_idx + 6, 'nondel_first_pattern', pj_nondel_first_patterns)
        data.to_excel(output_file, index=False)


        labels_set = list(set(data[GT_HEADER]))
        labels_set.sort()
        if '' in labels_set:
            labels_set.remove('')

        header = ''
        value = ''
        for label in labels_set:
            sub_data = data[data[GT_HEADER] == label]
            hit_data = sub_data[sub_data['ranked_hit'] == 'Y']
            header += label + '\t'
            value += str(len(sub_data)) + '(' + str(len(hit_data)) + ')\t'

        header += 'Total'
        value += str(len(data[data[GT_HEADER] != ''])) + '(' + str(len(data[data['ranked_hit'] == 'Y'])) + ')'

        print (header)
        print (value)

    print ('***********************************************************************************')

    print ('##########################################################################################')
    print ('Finish')
    print ('New Patterns Num: ' + str(len(new_pattern_list)))
    print ('Del Patterns Num: ' + str(len(del_pattern_list)))
    print ('Final Rank Len: ' + str(len(curr_rank_list)))
    print ('##########################################################################################')

    return curr_rank_list


def get_projects_funcs(projects):
    project_funcs = []
    for project in projects:
        if 'scikit-learn' in project or 'sklearn' in project:
            project_funcs.append(sklearn_patterns)
        elif 'ember' in project:
            project_funcs.append(emberjs_patterns)
        elif 'brew' in project:
            project_funcs.append(brew_patterns)
        elif 'atom' in project:
            project_funcs.append(atom_patterns)
        elif 'bitcoin' in project:
            project_funcs.append(bitcoin_patterns)

    return project_funcs



# ---------------------------------------------------
def pred_from_tab_unit(args):
    _, comment_row = args
    # gnl_patterns_dict = copy.deepcopy(matcher.gnl_patterns_dict)
    # spc_patterns_dict = copy.deepcopy(matcher.spc_patterns_dict)

    # if g_retain_list is None:
    #     gnl_patterns_dict = matcher.gnl_patterns_dict
    #     spc_patterns_dict = matcher.spc_patterns_dict

    #     gnl_patterns_list = []
    #     for key in gnl_patterns_dict:
    #         if matcher.split_vunit:
    #             for item in gnl_patterns_dict[key]:
    #                 gnl_patterns_list.extend(item[1])
    #         else:
    #             gnl_patterns_list.extend(gnl_patterns_dict[key])

    #     spc_patterns_list = []
    #     for key in curr_spc_patterns_dict:
    #         curr_patterns_list.extend(curr_spc_patterns_dict[key])
    # else:
    #     curr_patterns_list = g_retain_list

    # comment_tab = data.loc[comment_id]

    gnl_match = {}
    for key in matcher.gnl_patterns_dict:
        if matcher.split_vunit:
            patterns = []
            for item in matcher.gnl_patterns_dict[key]:
                patterns.extend(item[1])
        else:
            patterns = matcher.gnl_patterns_dict[key]

        for pattern in patterns:
            if g_retain_list is not None and pattern not in g_retain_list:
                continue
            if comment_row[str(pattern)] == 1:
                if key not in gnl_match:
                    gnl_match[key] = []
                gnl_match[key].append(pattern)

    if len(gnl_match) > 0:
        gnl_label = list(gnl_match.keys())
        gnl_label.sort()
        gnl_label = ','.join(gnl_label)
    else:
        gnl_label = 'N'

    spc_match = {}
    for key in matcher.spc_patterns_dict:
        for pattern in matcher.spc_patterns_dict[key]:
            if comment_row[str(pattern)] == 1:
                if key not in spc_match:
                    spc_match[key] = []
                spc_match[key].append(pattern)

    if len(spc_match) > 0:
        spc_label = list(spc_match.keys())
        spc_label.sort()
        spc_label = ','.join(spc_label)
    else:
        spc_label = 'N'

    return gnl_match, gnl_label, spc_match, spc_label, 'NA'


def data_match_from_tab(data_path, table_path, voc_dict=None, gnl_patterns_dict=None, spc_patterns_dict=None, split_vunit_flag=True, pred=False, retain_list=None, n_rows=None, hit_insert=True, label_all=True):
    data = pd.read_excel(data_path)
    data.fillna('', inplace=True)

    if n_rows is not None:
        data = data.iloc[:n_rows]

    if not label_all:
        data = data[data[GT_HEADER] != '']

    if len(data) == 0:
        return None
    
    table = pd.read_csv(table_path)
    table.set_index(keys='comment_ID', inplace=True)
    table = table.loc[data['comment_ID']]

    with Pool(initializer=make_global, initargs=(voc_dict, gnl_patterns_dict, spc_patterns_dict, split_vunit_flag, use_gpu, retain_list)) as pool:
        res = list(tqdm.tqdm(pool.imap(pred_from_tab_unit, table.iterrows()), total=len(table), ncols=100))

    gnl_matches = [item[0] for item in res]
    gnl_labels = [item[1] for item in res]
    spc_matches = [item[2] for item in res]
    spc_labels = [item[3] for item in res]
    gnl_match_contents = [item[4] for item in res]

    if hit_insert:
        gnl_hits = get_hits(data[GT_HEADER], gnl_labels)
        spc_hits = get_hits(data[GT_HEADER], spc_labels)
        gs_hit = get_gs_hits(data[GT_HEADER], gnl_labels, spc_labels)

        col_idx = list(data.columns).index(GT_HEADER)
        data.insert(col_idx + 1, 'gnl_label', gnl_labels)
        data.insert(col_idx + 2, 'gnl_match', gnl_matches)
        data.insert(col_idx + 3, 'gnl_hit', gnl_hits)
        data.insert(col_idx + 4, 'gnl_match_content', gnl_match_contents)
        data.insert(col_idx + 5, 'spc_label', spc_labels)
        data.insert(col_idx + 6, 'spc_match', spc_matches)
        data.insert(col_idx + 7, 'spc_hit', spc_hits)
        data.insert(col_idx + 8, 'gs_hit', gs_hit)
    else:
        col_idx = list(data.columns).index('time')

        data.insert(col_idx + 1, 'gnl_label', gnl_labels)
        data.insert(col_idx + 2, 'gnl_match', gnl_matches)
        data.insert(col_idx + 3, 'gnl_match_content', gnl_match_contents)
        data.insert(col_idx + 4, 'spc_label', spc_labels)
        data.insert(col_idx + 5, 'spc_match', spc_matches)

    return data
# ---------------------------------------------------


if __name__ == "__main__":

    use_gpu = True
    data_root = 'comment_data'
    save_root = 'pred'

    if not os.path.exists(save_root):
        os.makedirs(save_root)

    filenames = os.listdir(data_root)
    voc_dict, gnl_patterns_dict, spc_patterns_dict = get_patterns()
    with open('rank_list.pk', 'rb') as fr:
        rank_list = pickle.load(fr)

    for filename in filenames:
        print (filename)
        output_file = os.path.join(save_root, 'pd_' + filename)

        print ('Matching...')
        data = data_match(data_root, filename, voc_dict, gnl_patterns_dict, spc_patterns_dict, pred=True, use_gpu=use_gpu, hit_insert=False, retain_list=rank_list)
        data.to_excel(output_file, index=False)