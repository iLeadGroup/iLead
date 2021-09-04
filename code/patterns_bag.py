
def get_patterns(project_funcs=None, tag_list=None):
    if project_funcs is None or len(project_funcs) == 0:
        project_funcs = [sklearn_patterns, emberjs_patterns, brew_patterns, atom_patterns, bitcoin_patterns]
    if tag_list is None or len(tag_list) == 0:
        tag_list = ['LD1', 'LD2', 'LD3', 'LD4', 'LD5', 'LD6']

    voc_dict = {}
    gnl_patterns_dict = {}
    spc_patterns_dict = {}
    for project_func in project_funcs:
        for tag in tag_list:
            vocabulary, gnl_patterns, spc_patterns = project_func(tag)
            for key in vocabulary:
                if key not in voc_dict:
                    voc_dict[key] = vocabulary[key]
                else:
                    ext_words = [word for word in vocabulary[key] if word not in voc_dict[key]]
                    voc_dict[key].extend(ext_words)

            if tag not in gnl_patterns_dict:
                gnl_patterns_dict[tag] = []
            ext_gnl_patterns = [pattern for pattern in gnl_patterns if pattern not in gnl_patterns_dict[tag]]
            gnl_patterns_dict[tag].extend(ext_gnl_patterns)
            
            if tag not in spc_patterns_dict:
                spc_patterns_dict[tag] = []
            ext_spc_patterns = [pattern for pattern in spc_patterns if pattern not in spc_patterns_dict[tag]]
            spc_patterns_dict[tag].extend(ext_spc_patterns)

    return voc_dict, gnl_patterns_dict, spc_patterns_dict


def bitcoin_patterns(tag):
	if tag == 'LD1':
		vocabulary = {
			'Order_Verb': ['should', 'need to', 'can not', 'have to', 'must', 'have not'],
			'Can_Verb': ['could', 'can'],
			'Alter_Verb': ['use', 'try', 'pass', 'build', 'see', 'run', 'clean', 'follow', 'consider', 'delete', 'retry', 'install', 'reinstall'],
			'Sol_Noun': ['option', 'solution', 'idea'],
			'Infer_Phrase': ['might', 'probably', 'may', 'seem', 'perhaps'],
			'Want_Verb': ['want'],
			'Sol_Verb': ['solve', 'fix', 'work around'],
			'Issue_Noun': ['issue'],
			'Good_Adj': ['reasonable'],
		}

		gnl_patterns = [
			[('you', 'w'), ('Order_Verb', 'v')],
			[('you', 'w'), ('Can_Verb', 'v'), ('Alter_Verb', 'v')],
			[('AUX', 'p'), ('you', 'w'), ('Alter_Verb', 'v')],
			[('NUM', 'p'), ('Sol_Noun', 'v')],
			[('you', 'w'), ('Infer_Phrase', 'v'), ('Want_Verb', 'v')],
			[('try', 'w'), ('Alter_Verb', 'v')],
			[('please', 'w'), ('Alter_Verb', 'v')],
			[('be', 'l'), ('Sol_Noun', 'v'), ('to', 'w')],
			[('i', 'w'), ('Sol_Verb', 'v')],
			[('try', 'w'), ('NOUN', 'p')],
			[('i', 'w'), ('suggest', 'wl')],
			[('you', 'w'), ('Want_Verb', 'v'), ('NUM', 'p')],
			[('you', 'w'), ('Want_Verb', 'v'), ('NOUN', 'p')],
			[('you', 'w'), ('mean', 'l'), ('NOUN', 'p')],
			[('Infer_Phrase', 'v'), ('useful', 'w')],
			[('Infer_Phrase', 'v'), ('be', 'l'), ('helpful', 'l')],
			[('to', 'w'), ('Sol_Verb', 'v'), ('Issue_Noun', 'v')],
			[('Can_Verb', 'v'), ('Sol_Verb', 'v'), ('by', 'w')],
			[('would', 'w'), ('be', 'l'), ('Sol_Noun', 'v')],
			[('Infer_Phrase', 'v'), ('Good_Adj', 'v'), ('to', 'w'), ('VERB', 'p')],
			[('Infer_Phrase', 'v'), ('you', 'w'), ('Want_Verb', 'v')],
		]

		spc_patterns = ['\\nalternatively', 'do you mean <URL>']

	elif tag == 'LD2':
		vocabulary = {
			'Guide_Phrase': ['duplicate', 'fix', 'cause', 'find', 'propose', 'submit', 'regression'],
			'PR_Phrase': ['pr'],
			'Direct_Verb': ['ask', 'file', 'report', 'take', 'post', 'open', 'move', 'direct'],
			'Place_Noun': ['repository', 'repo', 'issue tracker', 'tracker', 'place', 'channel', 'forum', 'site'],
			'Direct_Noun': ['question', 'issue', 'discussion'],
			'Place_ADV': ['elsewhere', 'somewhere', 'here'],
			'Order_Verb': ['have to'],
		}

		gnl_patterns = [
			[('Guide_Phrase', 'v'), ('ADP', 'p'), ('#', 'w'), ('NUM', 'p')],
			[('Guide_Phrase', 'v'), ('ADP', 'p'), ('X', 'p')],
			[('duplicate', 'l'), ('#', 'w'), ('NUM', 'p')],
			[('Guide_Phrase', 'v'), ('ADP', 'p'), ('PR_Phrase', 'v')],
			[('Direct_Verb', 'v'), ('ADP', 'p'), ('Place_Noun', 'v')],
			[('Direct_Noun', 'v'), ('be', 'l'), ('Direct_Verb', 'v'), ('Place_ADV', 'v')],
			[('Direct_Verb', 'v'), ('Direct_Noun', 'v'), ('ADP', 'p')],
			[('Direct_Verb', 'v'), ('this', 'w'), ('ADP', 'p')],
			[('this', 'w'), ('Place_Noun', 'v'), ('ADP', 'p')],
			[('Direct_Verb', 'v'), ('Direct_Noun', 'v'), ('Place_ADV', 'v')],
			[('this', 'w'), ('be', 'l'), ('not', 'l'), ('Place_Noun', 'v')],
			[('this', 'w'), ('be', 'l'), ('Place_Noun', 'v'), ('to', 'w')],
			[('Order_Verb', 'v'), ('contact', 'w'), ('PROPN', 'p')],
			[('Direct_Noun', 'v'), ('not', 'l'), ('belong', 'l')],
			[('directed to', 'w')],
			[('not', 'l'), ('provide', 'l'), ('support', 'l'), ('here', 'l')],
		]

		spc_patterns = ['cc\\W+@\\w+', 'stack.?exchange', 'stack.?overflow', 'mailing.?list']

	elif tag == 'LD3':
		vocabulary = {
			'Exp_Verb': ['have', 'run into', 'get', 'see', 'confirm', 'reproduce'],
			'Sim_Adj': ['same', 'similar'],
			'Issue_Noun': ['issue', 'problem', 'error', 'warning', 'bug'],
			'Sim_Adv': ['before', 'too', 'as well'],
			'Can_Verb': ['could', 'can', 'be able to'],
			'Ref_Word': ['as', 'like'],
			'Express_Verb': ['mention', 'point out', 'point', 'say'],
			'Infer_Phrase': ['might', 'seem', 'sound'],
			'Good_Adj': ['good', 'reasonable'],
			'Sol_Noun': ['point', 'idea', 'suggestion'],
			'Issue_None': ['issue'],
			'Confirm_Adj': ['right', 'true'],
			'Happen_Verb': ['report', 'happen'],
			'ACK_Phrase': ['ACK', 'NACK', 'NACKish'],
		}

		gnl_patterns = [
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('this', 'w'), ('Sim_Adv', 'v')],
			[('i', 'w'), ('Can_Verb', 'v'), ('reproduce', 'l')],
			[('i reproduced', 'w')],
			[('Ref_Word', 'v'), ('PROPN', 'p'), ('Express_Verb', 'v')],
			[('Infer_Phrase', 'v'), ('Good_Adj', 'v')],
			[('Good_Adj', 'v'), ('Sol_Noun', 'v')],
			[('Sim_Adj', 'v'), ('Issue_Noun', 'v')],
			[('this', 'w'), ('not', 'l'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('this', 'w')],
			[('Exp_Verb', 'v'), ('this', 'w'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v')],
			[('this', 'w'), ('be', 'l'), ('Issue_Noun', 'v')],
			[('make sense', 'wl')],
			[('i agree', 'wl')],
			[('Exp_Verb', 'v'), ('Sim_Adv', 'v')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v'), ('Issue_None', 'v')],
			[('Can_Verb', 'v'), ('not', 'l'), ('reproduce', 'l')],
			[('not', 'l'), ('Issue_Noun', 'v')],
			[('work for i', 'wl')],
			[('be', 'l'), ('Good_Adj', 'v'), ('Sol_Noun', 'v')],
			[('Exp_Verb', 'v'), ('Issue_Noun', 'v'), ('Sim_Adv', 'v')],
			[('PRON', 'p'), ('be', 'l'), ('Confirm_Adj', 'v')],
			[('agree with', 'wl')],
			[('not', 'l'), ('think', 'w'), ('be', 'l'), ('Issue_Noun', 'v')],
			[('not', 'l'), ('think', 'w'), ('this', 'w'), ('Issue_Noun', 'v')],
			[('i disagree', 'wl')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v'), ('thing', 'w')],
			[('Can_Verb', 'v'), ('reproduce', 'l'), ('this', 'w')],
			[('Sim_Adj', 'v'), ('to', 'w'), ('me', 'w')],
			[('as point out', 'wl')],
			[('also', 'w'), ('Happen_Verb', 'v'), ('#', 'w'), ('NUM', 'p')],
			[('also', 'w'), ('Happen_Verb', 'v'), ('X', 'p')],
			[('concept', 'wl'), ('ACK_Phrase', 'v')],
			[('i', 'w'), ('be', 'l'), ('ACK_Phrase', 'v')],
			[('succeed on', 'wl')],
			[('still not fix', 'wl')],
			[('like', 'l'), ('plan', 'l')],
		]

		spc_patterns = ['^yes', '^indeed', '^yep', '^right', 'yep', '^yeah', '^i agree', '@\\w+\\s*-?\\s*yes', '^yea', '^confirmed', '^confirm', '^can confirm', '^agree', '^ACK', '^correct', '^NACK', '@\\w+\\s*-?\\s*i agree']

	elif tag == 'LD4':
		vocabulary = {
			'Inquiry_Verb': ['provide', 'explain', 'post', 'give', 'specify', 'elaborate', 'sure', 'let me know', 'make sure', 'show', 'verify', 'upload', 'point to', 'share', 'let us know', 'add', 'include'],
			'Wh_Word': ['how', 'what', 'which', 'when', 'where', 'why'],
			'Inquiry_Noun': ['information', 'step', 'code', 'output'],
		}

		gnl_patterns = [
			[('AUX', 'p'), ('you', 'w'), ('Inquiry_Verb', 'v')],
			[('Wh_Word', 'v'), ('?', 'e')],
			[('AUX', 'p'), ('PRON', 'p'), ('?', 'e')],
			[('AUX', 'p'), ('the', 'w'), ('?', 'e')],
			[('be', 'l'), ('PRON', 'p'), ('?', 'e')],
			[('be', 'l'), ('the', 'w'), ('?', 'e')],
			[('please', 'w'), ('Inquiry_Verb', 'v')],
			[('Inquiry_Verb', 'v'), ('Inquiry_Noun', 'v')],
		]

		spc_patterns = []

	elif tag == 'LD5':
		vocabulary = {
			'Issue_Action': ['close', 'reopen', 're-open'],
			'Issue_Noun': ['issue'],
			'Can_Verb': ['could', 'can'],
			'Plan_Phrase': ['should be', 'going to', 'can be'],
			'New_Word': ['new'],
		}

		gnl_patterns = [
			[('Issue_Action', 'v'), ('Issue_Noun', 'v')],
			[('Issue_Action', 'v'), ('this', 'w')],
			[('Issue_Action', 'v'), ('it', 'w')],
			[('Can_Verb', 'v'), ('Issue_Action', 'v')],
			[('Plan_Phrase', 'v'), ('Issue_Action', 'v')],
			[('open', 'l'), ('New_Word', 'v'), ('issue', 'w')],
			[('Issue_Noun', 'v'), ('be', 'l'), ('Issue_Action', 'v')],
			[('close for now', 'wl')],
		]

		spc_patterns = ['^closing', '\\W closing', '\\nclosing', '^closed', 'closed by #\\d+']

	elif tag == 'LD6':
		vocabulary = {
			'Plan_Phrase': ['will', 'would', 'decide to'],
			'Volun_Verb': ['open', 'prepare', 'give', 'take', 'review', 'test', 'help'],
			'Volun_Noun': ['pr', 'fix', 'try', 'stab'],
			'Intend_Phrase': ['would like', 'happy to'],
			'Contri_Verb': ['help'],
			'Progress_Phrase': ['propose', 'work on'],
			'PR_Phrase': ['pull request'],
			'Can_Verb': ['can'],
		}

		gnl_patterns = [
			[('Plan_Phrase', 'v'), ('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Intend_Phrase', 'v'), ('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Intend_Phrase', 'v'), ('Contri_Verb', 'v')],
			[('i', 'w'), ('Plan_Phrase', 'v'), ('Progress_Phrase', 'v')],
			[('Plan_Phrase', 'v'), ('Progress_Phrase', 'v')],
			[('Intend_Phrase', 'v'), ('Progress_Phrase', 'v')],
			[('PR_Phrase', 'v'), ('welcome', 'l')],
			[('Intend_Phrase', 'v'), ('Volun_Verb', 'v')],
			[('i', 'w'), ('Can_Verb', 'v'), ('do', 'w')],
			[('we', 'w'), ('be', 'l'), ('Progress_Phrase', 'v')],
		]

		spc_patterns = []

	return vocabulary, gnl_patterns, spc_patterns


def sklearn_patterns(tag):
	if tag == 'LD1':
		vocabulary = {
			'Order_Verb': ['should', 'need to', 'can not', 'have to', 'can also'],
			'Can_Verb': ['could', 'can', 'be able to'],
			'Alter_Verb': ['use', 'try', 'install', 'pass', 'set', 'build', 'see', 'update', 'reinstall', 'follow', 'run'],
			'Sol_Noun': ['solution', 'option'],
			'Offer_Verb': ['give'],
			'Material_Noun': ['article'],
			'Infer_Phrase': ['might', 'perhaps'],
			'Want_Verb': ['want'],
			'Sol_Verb': ['solve'],
			'Issue_Noun': ['issue'],
		}

		gnl_patterns = [
			[('you', 'w'), ('Order_Verb', 'v')],
			[('you', 'w'), ('Can_Verb', 'v'), ('Alter_Verb', 'v')],
			[('AUX', 'p'), ('you', 'w'), ('Alter_Verb', 'v')],
			[('Sol_Noun', 'v'), ('Offer_Verb', 'v'), ('ADP', 'p'), ('X', 'p')],
			[('DET', 'p'), ('Material_Noun', 'v'), ('help', 'l')],
			[('NUM', 'p'), ('Sol_Noun', 'v')],
			[('you', 'w'), ('Infer_Phrase', 'v'), ('Want_Verb', 'v')],
			[('try', 'w'), ('Alter_Verb', 'v')],
			[('please', 'w'), ('Alter_Verb', 'v')],
			[('try', 'w'), ('NOUN', 'p')],
			[('you', 'w'), ('Want_Verb', 'v'), ('NUM', 'p')],
			[('you', 'w'), ('Want_Verb', 'v'), ('NOUN', 'p')],
			[('Infer_Phrase', 'v'), ('be', 'l'), ('helpful', 'l')],
			[('to', 'w'), ('Sol_Verb', 'v'), ('Issue_Noun', 'v')],
		]

		spc_patterns = []

	elif tag == 'LD2':
		vocabulary = {
			'Guide_Phrase': ['duplicate', 'fix', 'related', 'report', 'introduce'],
			'Direct_Verb': ['report'],
			'Place_Noun': ['issue tracker', 'tracker'],
			'Direct_Noun': ['issue'],
		}

		gnl_patterns = [
			[('Guide_Phrase', 'v'), ('ADP', 'p'), ('#', 'w'), ('NUM', 'p')],
			[('Guide_Phrase', 'v'), ('ADP', 'p'), ('X', 'p')],
			[('duplicate', 'l'), ('#', 'w'), ('NUM', 'p')],
			[('Direct_Verb', 'v'), ('ADP', 'p'), ('Place_Noun', 'v')],
			[('Direct_Verb', 'v'), ('Direct_Noun', 'v'), ('ADP', 'p')],
			[('this', 'w'), ('Place_Noun', 'v'), ('ADP', 'p')],
		]

		spc_patterns = ['cc\\W+@\\w+', 'stack.?exchange', 'stack.?overflow', 'mailing.?list']

	elif tag == 'LD3':
		vocabulary = {
			'Sim_Adj': ['same', 'similar'],
			'Exp_Verb': ['have', 'face', 'run into', 'encounter', 'see'],
			'Issue_Noun': ['issue', 'problem', 'error', 'bug'],
			'Sim_Adv': ['too'],
			'Can_Verb': ['can'],
			'Ref_Word': ['as'],
			'Express_Verb': ['mention'],
			'Highly_Adj': ['completely', 'absolutely'],
			'Confirm_Adj': ['right', 'correct'],
			'Infer_Phrase': ['seem', 'sound'],
			'Good_Adj': ['good', 'reasonable'],
			'Sol_Noun': ['solution', 'point'],
			'Issue_None': ['issue'],
		}

		gnl_patterns = [
			[('Sim_Adj', 'v'), ('for', 'w'), ('me', 'w')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('this', 'w'), ('Sim_Adv', 'v')],
			[('we', 'w'), ('Can_Verb', 'v'), ('reproduce', 'l')],
			[('i', 'w'), ('Can_Verb', 'v'), ('reproduce', 'l')],
			[('i reproduced', 'w')],
			[('me too', 'wl')],
			[('Ref_Word', 'v'), ('PROPN', 'p'), ('Express_Verb', 'v')],
			[('Highly_Adj', 'v'), ('agree', 'l')],
			[('Highly_Adj', 'v'), ('Confirm_Adj', 'v')],
			[('Infer_Phrase', 'v'), ('Good_Adj', 'v')],
			[('Good_Adj', 'v'), ('Sol_Noun', 'v')],
			[('Sim_Adj', 'v'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('this', 'w')],
			[('Exp_Verb', 'v'), ('this', 'w'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v')],
			[('this', 'w'), ('be', 'l'), ('Issue_Noun', 'v')],
			[('i agree', 'wl')],
			[('Exp_Verb', 'v'), ('Sim_Adv', 'v')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v'), ('Issue_None', 'v')],
			[('Can_Verb', 'v'), ('not', 'l'), ('reproduce', 'l')],
			[('not', 'l'), ('Issue_Noun', 'v')],
			[('work for i', 'wl')],
			[('be', 'l'), ('Good_Adj', 'v'), ('Sol_Noun', 'v')],
			[('Exp_Verb', 'v'), ('Issue_Noun', 'v'), ('Sim_Adv', 'v')],
			[('PRON', 'p'), ('be', 'l'), ('Confirm_Adj', 'v')],
			[('agree with', 'wl')],
		]

		spc_patterns = ['^yes', '^indeed', '^yep', '\\nagree', '@\\w+\\s*-?\\s*agree', '^right', 'yep', '^same', '^i agree', '^yea']

	elif tag == 'LD4':
		vocabulary = {
			'Inquiry_Verb': ['paste', 'provide', 'explain', 'describe', 'post', 'give', 'confirm', 'specify', 'elaborate', 'sure', 'share', 'let us know'],
			'Wh_Word': ['how', 'what', 'which', 'when', 'why'],
			'Inquiry_Noun': ['output', 'code', 'information'],
		}

		gnl_patterns = [
			[('AUX', 'p'), ('you', 'w'), ('Inquiry_Verb', 'v')],
			[('Wh_Word', 'v'), ('?', 'e')],
			[('AUX', 'p'), ('PRON', 'p'), ('?', 'e')],
			[('AUX', 'p'), ('the', 'w'), ('?', 'e')],
			[('be', 'l'), ('PRON', 'p'), ('?', 'e')],
			[('be', 'l'), ('the', 'w'), ('?', 'e')],
			[('please', 'w'), ('Inquiry_Verb', 'v')],
			[('Inquiry_Verb', 'v'), ('Inquiry_Noun', 'v')],
		]

		spc_patterns = []

	elif tag == 'LD5':
		vocabulary = {
			'Issue_Action': ['close', 'reopen', 're-open'],
			'Issue_Noun': ['issue'],
			'Can_Verb': ['could', 'can'],
			'Plan_Phrase': ['should be', 'will', 'going to', 'can be'],
			'New_Word': ['another', 'new'],
		}

		gnl_patterns = [
			[('Issue_Action', 'v'), ('Issue_Noun', 'v')],
			[('Issue_Action', 'v'), ('this', 'w')],
			[('Issue_Action', 'v'), ('it', 'w')],
			[('Can_Verb', 'v'), ('Issue_Action', 'v')],
			[('i', 'w'), ('Issue_Action', 'v'), ('then', 'w')],
			[('Plan_Phrase', 'v'), ('Issue_Action', 'v')],
			[('open', 'l'), ('New_Word', 'v'), ('issue', 'w')],
			[('Issue_Noun', 'v'), ('be', 'l'), ('Issue_Action', 'v')],
		]

		spc_patterns = ['^closing', '\\W closing', 'hence closing', '\\nclosing', '^closed']

	elif tag == 'LD6':
		vocabulary = {
			'Plan_Phrase': ['will', 'would'],
			'Volun_Verb': ['propose', 'submit', 'open', 'make', 'push', 'fix', 'help', 'review', 'give', 'do', 'assign to', 'send', 'create', 'take', 'test'],
			'Volun_Noun': ['pr', 'fix', 'pull request', 'try', 'release'],
			'Intend_Phrase': ['intend to', 'want to', 'be interested in', 'happy to', 'would like'],
			'Issue_Noun': ['issue'],
			'Can_Verb': ['can', 'could'],
			'Progress_Phrase': ['work on', 'fix up', 'propose'],
			'Contri_Verb': ['help', 'contribute'],
			'Done_Phrase': ['have'],
			'PR_Phrase': ['pull request'],
		}

		gnl_patterns = [
			[('Plan_Phrase', 'v'), ('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Intend_Phrase', 'v'), ('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Intend_Phrase', 'v'), ('Volun_Verb', 'v'), ('Issue_Noun', 'v')],
			[('Can_Verb', 'v'), ('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('i', 'w'), ('Plan_Phrase', 'v'), ('do', 'w')],
			[('Progress_Phrase', 'v'), ('this', 'w'), ('Issue_Noun', 'v')],
			[('i', 'w'), ('Can_Verb', 'v'), ('Progress_Phrase', 'v')],
			[('Intend_Phrase', 'v'), ('Contri_Verb', 'v')],
			[('Plan_Phrase', 'v'), ('Volun_Verb', 'v'), ('Issue_Noun', 'v')],
			[('i', 'w'), ('Plan_Phrase', 'v'), ('Volun_Verb', 'v'), ('it', 'w')],
			[('i', 'w'), ('Plan_Phrase', 'v'), ('Progress_Phrase', 'v')],
			[('assign', 'l'), ('this', 'w'), ('to', 'w'), ('me', 'w')],
			[('assign', 'l'), ('it', 'w'), ('to', 'w'), ('me', 'w')],
			[('Plan_Phrase', 'v'), ('Progress_Phrase', 'v')],
			[('i', 'w'), ('be', 'l'), ('Progress_Phrase', 'v')],
			[('Can_Verb', 'v'), ('PRON', 'p'), ('Progress_Phrase', 'v')],
			[('Done_Phrase', 'v'), ('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Intend_Phrase', 'v'), ('Progress_Phrase', 'v')],
			[('i', 'w'), ('Progress_Phrase', 'v'), ('Volun_Verb', 'v')],
			[('PR_Phrase', 'v'), ('welcome', 'l')],
			[('Intend_Phrase', 'v'), ('Volun_Verb', 'v')],
			[('i', 'w'), ('Can_Verb', 'v'), ('do', 'w')],
		]

		spc_patterns = []

	return vocabulary, gnl_patterns, spc_patterns


def emberjs_patterns(tag):
	if tag == 'LD1':
		vocabulary = {
			'Order_Verb': ['should', 'need to', 'can not', 'have to', 'can also', 'must'],
			'Can_Verb': ['could', 'can', 'be able to'],
			'Alter_Verb': ['use', 'consider', 'try', 'pass', 'run', 'update', 'install'],
			'Sol_Noun': ['option', 'solution', 'idea'],
			'Avoid_Verb': ['avoid'],
			'Issue_Noun': ['error', 'problem'],
			'Infer_Phrase': ['probably'],
			'Want_Verb': ['want'],
			'Sol_Verb': ['solve'],
		}

		gnl_patterns = [
			[('you', 'w'), ('Order_Verb', 'v')],
			[('you', 'w'), ('Can_Verb', 'v'), ('Alter_Verb', 'v')],
			[('AUX', 'p'), ('you', 'w'), ('Alter_Verb', 'v')],
			[('NUM', 'p'), ('Sol_Noun', 'v')],
			[('Avoid_Verb', 'v'), ('Issue_Noun', 'v')],
			[('you', 'w'), ('Infer_Phrase', 'v'), ('Want_Verb', 'v')],
			[('try', 'w'), ('Alter_Verb', 'v')],
			[('please', 'w'), ('Alter_Verb', 'v')],
			[('be', 'l'), ('Sol_Noun', 'v'), ('to', 'w')],
			[('try', 'w'), ('NOUN', 'p')],
			[('i', 'w'), ('suggest', 'wl')],
			[('to', 'w'), ('Sol_Verb', 'v'), ('Issue_Noun', 'v')],
			[('would', 'w'), ('be', 'l'), ('Sol_Noun', 'v')],
		]

		spc_patterns = []

	elif tag == 'LD2':
		vocabulary = {
			'Guide_Phrase': ['duplicate', 'fix', 'address', 'same', 'resolve', 'similar', 'report'],
			'Direct_Verb': ['move'],
			'Place_Noun': ['repo'],
			'Direct_Noun': ['issue'],
		}

		gnl_patterns = [
			[('Guide_Phrase', 'v'), ('ADP', 'p'), ('#', 'w'), ('NUM', 'p')],
			[('Guide_Phrase', 'v'), ('ADP', 'p'), ('X', 'p')],
			[('duplicate', 'l'), ('#', 'w'), ('NUM', 'p')],
			[('Direct_Verb', 'v'), ('ADP', 'p'), ('Place_Noun', 'v')],
			[('Direct_Verb', 'v'), ('Direct_Noun', 'v'), ('ADP', 'p')],
			[('Direct_Verb', 'v'), ('this', 'w'), ('ADP', 'p')],
		]

		spc_patterns = ['cc\\W+@\\w+', 'stack.?overflow']

	elif tag == 'LD3':
		vocabulary = {
			'Exp_Verb': ['have', 'face', 'run into', 'get', 'see', 'hit', 'experience', 'encounter', 'find', 'confirm', 'reproduce', 'second', 'walk into'],
			'Sim_Adj': ['same', 'similar'],
			'Issue_Noun': ['issue', 'problem', 'error', 'bug'],
			'Sim_Adv': ['as well', 'too', 'before'],
			'Can_Verb': ['could', 'be able to'],
			'Highly_Adj': ['absolutely', 'totally', 'definitely'],
			'Confirm_Adj': ['correct'],
			'Infer_Phrase': ['seem', 'sound'],
			'Good_Adj': ['great', 'good'],
			'Sol_Noun': ['point', 'suggestion', 'reproduction'],
			'Issue_None': ['issue'],
		}

		gnl_patterns = [
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('this', 'w'), ('Sim_Adv', 'v')],
			[('i', 'w'), ('Can_Verb', 'v'), ('reproduce', 'l')],
			[('me too', 'wl')],
			[('Highly_Adj', 'v'), ('agree', 'l')],
			[('Highly_Adj', 'v'), ('Confirm_Adj', 'v')],
			[('Infer_Phrase', 'v'), ('Good_Adj', 'v')],
			[('Good_Adj', 'v'), ('Sol_Noun', 'v')],
			[('Sim_Adj', 'v'), ('Issue_Noun', 'v')],
			[('this', 'w'), ('not', 'l'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('this', 'w')],
			[('Exp_Verb', 'v'), ('this', 'w'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v')],
			[('this', 'w'), ('be', 'l'), ('Issue_Noun', 'v')],
			[('this', 'w'), ('be', 'l'), ('not', 'l'), ('Issue_Noun', 'v')],
			[('it', 'w'), ('be', 'l'), ('not', 'l'), ('Issue_Noun', 'v')],
			[('make sense', 'wl')],
			[('i agree', 'wl')],
			[('Exp_Verb', 'v'), ('Sim_Adv', 'v')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v'), ('Issue_None', 'v')],
			[('Can_Verb', 'v'), ('not', 'l'), ('reproduce', 'l')],
			[('not', 'l'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('Issue_Noun', 'v'), ('Sim_Adv', 'v')],
			[('PRON', 'p'), ('be', 'l'), ('Confirm_Adj', 'v')],
			[('agree with', 'wl')],
			[('not', 'l'), ('think', 'w'), ('be', 'l'), ('Issue_Noun', 'v')],
			[('not', 'l'), ('think', 'w'), ('this', 'w'), ('Issue_Noun', 'v')],
			[('this', 'w'), ('seem', 'l'), ('Issue_Noun', 'v')],
			[('i disagree', 'wl')],
			[('Highly_Adj', 'v'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v'), ('thing', 'w')],
			[('Can_Verb', 'v'), ('reproduce', 'l'), ('this', 'w')],
		]

		spc_patterns = ['^yes', '^yep', 'yep', '^yup', '^yeah', '^same', '^i agree', '^yea', '^ya', '^confirmed', '@\\w+\\s*-?\\s*right', '^confirm', '^same here', '^agree']

	elif tag == 'LD4':
		vocabulary = {
			'Inquiry_Verb': ['provide', 'explain', 'describe', 'post', 'confirm', 'share', 'show', 'say', 'let us know', 'paste', 'include'],
			'Wh_Word': ['how', 'what', 'where', 'why'],
			'Inquiry_Noun': ['code', 'information', 'output'],
			'Order_Verb': ['should'],
		}

		gnl_patterns = [
			[('AUX', 'p'), ('you', 'w'), ('Inquiry_Verb', 'v')],
			[('Wh_Word', 'v'), ('?', 'e')],
			[('AUX', 'p'), ('PRON', 'p'), ('?', 'e')],
			[('AUX', 'p'), ('the', 'w'), ('?', 'e')],
			[('be', 'l'), ('PRON', 'p'), ('?', 'e')],
			[('be', 'l'), ('the', 'w'), ('?', 'e')],
			[('please', 'w'), ('Inquiry_Verb', 'v')],
			[('Inquiry_Verb', 'v'), ('Inquiry_Noun', 'v')],
			[('Order_Verb', 'v'), ('Inquiry_Verb', 'v'), ('ADP', 'p'), ('X', 'p')],
		]

		spc_patterns = []

	elif tag == 'LD5':
		vocabulary = {
			'Issue_Action': ['close', 'reopen'],
			'Issue_Noun': ['issue', 'bug'],
			'Can_Verb': ['could', 'can'],
			'Plan_Phrase': ['will', 'going to', 'can be'],
			'New_Word': ['another', 'new'],
		}

		gnl_patterns = [
			[('Issue_Action', 'v'), ('Issue_Noun', 'v')],
			[('Issue_Action', 'v'), ('this', 'w')],
			[('Issue_Action', 'v'), ('it', 'w')],
			[('Can_Verb', 'v'), ('Issue_Action', 'v')],
			[('Plan_Phrase', 'v'), ('Issue_Action', 'v')],
			[('open', 'l'), ('New_Word', 'v'), ('issue', 'w')],
			[('Issue_Noun', 'v'), ('be', 'l'), ('Issue_Action', 'v')],
			[('close for now', 'wl')],
		]

		spc_patterns = ['^closing', '\\W closing', '^reopen', '^reopening', '\\nclosing', '^closed', 'closed by #\\d+']

	elif tag == 'LD6':
		vocabulary = {
			'Plan_Phrase': ['would', 'will'],
			'Volun_Verb': ['take', 'make', 'help', 'submit', 'do', 'give', 'send', 'test', 'push up', 'trigger', 'gauge', 'fix', 'finish up'],
			'Volun_Noun': ['stab', 'attempt', 'fix', 'pr', 'try', 'release'],
			'Intend_Phrase': ['want to', 'would like', 'happy to'],
			'Can_Verb': ['can'],
			'Contri_Verb': ['contribute', 'help'],
			'Progress_Phrase': ['work on', 'try to', 'working to', 'take a look'],
			'Done_Phrase': ['have'],
		}

		gnl_patterns = [
			[('Plan_Phrase', 'v'), ('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Intend_Phrase', 'v'), ('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Can_Verb', 'v'), ('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Intend_Phrase', 'v'), ('Contri_Verb', 'v')],
			[('i', 'w'), ('Plan_Phrase', 'v'), ('Progress_Phrase', 'v')],
			[('Plan_Phrase', 'v'), ('Progress_Phrase', 'v')],
			[('i', 'w'), ('be', 'l'), ('Progress_Phrase', 'v')],
			[('Done_Phrase', 'v'), ('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Intend_Phrase', 'v'), ('Progress_Phrase', 'v')],
			[('i', 'w'), ('Progress_Phrase', 'v'), ('Volun_Verb', 'v')],
			[('Intend_Phrase', 'v'), ('Volun_Verb', 'v')],
			[('i', 'w'), ('Can_Verb', 'v'), ('do', 'w')],
			[('i', 'w'), ('Can_Verb', 'v'), ('Contri_Verb', 'v')],
			[('i', 'w'), ('Progress_Phrase', 'v'), ('get', 'l'), ('Volun_Noun', 'v'), ('out', 'w')],
			[('i', 'w'), ('Progress_Phrase', 'v'), ('get', 'l'), ('this', 'w'), ('out', 'w')],
			[('Can_Verb', 'v'), ('PRON', 'p'), ('Contri_Verb', 'v')],
			[('Done_Phrase', 'v'), ('Volun_Verb', 'v'), ('X', 'p')],
		]

		spc_patterns = []

	return vocabulary, gnl_patterns, spc_patterns


def brew_patterns(tag):
	if tag == 'LD1':
		vocabulary = {
			'Order_Verb': ['should', 'need to', 'have to', 'must'],
			'Can_Verb': ['could', 'can', 'be able to'],
			'Alter_Verb': ['use', 'try', 'install', 'look at', 'set', 'update', 'run', 'delete', 'see', 'clean', 'build'],
			'Infer_Phrase': ['probably', 'may'],
			'Want_Verb': ['want', 'look for'],
		}

		gnl_patterns = [
			[('you', 'w'), ('Order_Verb', 'v')],
			[('you', 'w'), ('Can_Verb', 'v'), ('Alter_Verb', 'v')],
			[('AUX', 'p'), ('you', 'w'), ('Alter_Verb', 'v')],
			[('you', 'w'), ('Infer_Phrase', 'v'), ('Want_Verb', 'v')],
			[('try', 'w'), ('Alter_Verb', 'v')],
			[('please', 'w'), ('Alter_Verb', 'v')],
			[('try', 'w'), ('NOUN', 'p')],
			[('you', 'w'), ('Want_Verb', 'v'), ('NUM', 'p')],
			[('you', 'w'), ('Want_Verb', 'v'), ('NOUN', 'p')],
			[('Infer_Phrase', 'v'), ('you', 'w'), ('Want_Verb', 'v')],
		]

		spc_patterns = ['\\nalternatively']

	elif tag == 'LD2':
		vocabulary = {
			'Guide_Phrase': ['duplicate', 'fix', 'cause', 'same', 'report', 'introduce', 'propose', 'regression', 'resolve'],
			'PR_Phrase': ['pr'],
			'Direct_Verb': ['ask', 'report', 'move', 'open'],
			'Place_Noun': ['community', 'forum', 'repo', 'place'],
			'Direct_Noun': ['discussion', 'issue', 'question'],
			'Place_ADV': ['somewhere', 'there'],
		}

		gnl_patterns = [
			[('Guide_Phrase', 'v'), ('ADP', 'p'), ('#', 'w'), ('NUM', 'p')],
			[('Guide_Phrase', 'v'), ('ADP', 'p'), ('X', 'p')],
			[('duplicate', 'l'), ('#', 'w'), ('NUM', 'p')],
			[('Guide_Phrase', 'v'), ('ADP', 'p'), ('PR_Phrase', 'v')],
			[('Direct_Verb', 'v'), ('ADP', 'p'), ('Place_Noun', 'v')],
			[('Direct_Noun', 'v'), ('be', 'l'), ('Direct_Verb', 'v'), ('Place_ADV', 'v')],
			[('Direct_Verb', 'v'), ('Direct_Noun', 'v'), ('ADP', 'p')],
			[('Direct_Verb', 'v'), ('this', 'w'), ('ADP', 'p')],
			[('Direct_Verb', 'v'), ('Direct_Noun', 'v'), ('Place_ADV', 'v')],
			[('this', 'w'), ('be', 'l'), ('not', 'l'), ('Place_Noun', 'v')],
		]

		spc_patterns = ['cc\\W+@\\w+']

	elif tag == 'LD3':
		vocabulary = {
			'Exp_Verb': ['have', 'get', 'find', 'experience', 'run into', 'reproduce', 'hit', 'second', 'encounter', 'see'],
			'Sim_Adj': ['same'],
			'Issue_Noun': ['issue', 'error', 'problem', 'bug'],
			'Sim_Adv': ['too', 'previously', 'as well', 'before'],
			'Can_Verb': ['can'],
			'Ref_Word': ['as'],
			'Express_Verb': ['mention', 'say', 'note'],
			'Highly_Adj': ['absolutely', 'totally'],
			'Infer_Phrase': ['might', 'sound'],
			'Good_Adj': ['good', 'great'],
			'Sol_Noun': ['solution', 'point', 'idea'],
			'Issue_None': ['issue'],
			'Confirm_Adj': ['right', 'correct'],
		}

		gnl_patterns = [
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('this', 'w'), ('Sim_Adv', 'v')],
			[('we', 'w'), ('Can_Verb', 'v'), ('reproduce', 'l')],
			[('i', 'w'), ('Can_Verb', 'v'), ('reproduce', 'l')],
			[('Ref_Word', 'v'), ('PROPN', 'p'), ('Express_Verb', 'v')],
			[('Highly_Adj', 'v'), ('agree', 'l')],
			[('Infer_Phrase', 'v'), ('Good_Adj', 'v')],
			[('Good_Adj', 'v'), ('Sol_Noun', 'v')],
			[('Sim_Adj', 'v'), ('Issue_Noun', 'v')],
			[('this', 'w'), ('not', 'l'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('this', 'w')],
			[('Exp_Verb', 'v'), ('this', 'w'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v')],
			[('this', 'w'), ('be', 'l'), ('Issue_Noun', 'v')],
			[('this', 'w'), ('be', 'l'), ('not', 'l'), ('Issue_Noun', 'v')],
			[('it', 'w'), ('be', 'l'), ('not', 'l'), ('Issue_Noun', 'v')],
			[('make sense', 'wl')],
			[('i agree', 'wl')],
			[('Exp_Verb', 'v'), ('Sim_Adv', 'v')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v'), ('Issue_None', 'v')],
			[('Can_Verb', 'v'), ('not', 'l'), ('reproduce', 'l')],
			[('Ref_Word', 'v'), ('Express_Verb', 'v'), ('by', 'w'), ('PROPN', 'p')],
			[('not', 'l'), ('Issue_Noun', 'v')],
			[('work for i', 'wl')],
			[('be', 'l'), ('Good_Adj', 'v'), ('Sol_Noun', 'v')],
			[('PRON', 'p'), ('be', 'l'), ('Confirm_Adj', 'v')],
			[('agree with', 'wl')],
			[('i disagree', 'wl')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v'), ('thing', 'w')],
			[('Can_Verb', 'v'), ('reproduce', 'l'), ('this', 'w')],
		]

		spc_patterns = ['^yes', '^indeed', '^yep', '\\nagree', '\\ni agree', 'yep', '^yeah', '^sure', '^i agree', '@\\w+\\s*-?\\s*yes', '^yea', '^agree', '^disagree']

	elif tag == 'LD4':
		vocabulary = {
			'Inquiry_Verb': ['paste', 'provide', 'describe', 'post', 'give', 'elaborate', 'sure', 'share', 'add', 'include', 'verify', 'point to', 'confirm', 'fill out'],
			'Wh_Word': ['how', 'what', 'which', 'when'],
			'Inquiry_Noun': ['output', 'information', 'template', 'issue template'],
		}

		gnl_patterns = [
			[('AUX', 'p'), ('you', 'w'), ('Inquiry_Verb', 'v')],
			[('Wh_Word', 'v'), ('?', 'e')],
			[('AUX', 'p'), ('PRON', 'p'), ('?', 'e')],
			[('AUX', 'p'), ('the', 'w'), ('?', 'e')],
			[('be', 'l'), ('PRON', 'p'), ('?', 'e')],
			[('be', 'l'), ('the', 'w'), ('?', 'e')],
			[('please', 'w'), ('Inquiry_Verb', 'v')],
			[('Inquiry_Verb', 'v'), ('Inquiry_Noun', 'v')],
		]

		spc_patterns = []

	elif tag == 'LD5':
		vocabulary = {
			'Issue_Action': ['close', 'reopen'],
			'Issue_Noun': ['issue'],
			'Plan_Phrase': ['will', 'going to'],
			'New_Word': ['new'],
		}

		gnl_patterns = [
			[('Issue_Action', 'v'), ('Issue_Noun', 'v')],
			[('Issue_Action', 'v'), ('this', 'w')],
			[('Plan_Phrase', 'v'), ('Issue_Action', 'v')],
			[('open', 'l'), ('New_Word', 'v'), ('issue', 'w')],
			[('close for now', 'wl')],
			[('so close', 'wl')],
		]

		spc_patterns = ['^closing', '\\W closing', '\\nclosing', '^reopning']

	elif tag == 'LD6':
		vocabulary = {
			'Plan_Phrase': ['will', 'would'],
			'Volun_Verb': ['send', 'submit', 'open', 'review', 'help', 'create', 'take'],
			'Volun_Noun': ['pr', 'pull request', 'fix', 'prs'],
			'Intend_Phrase': ['would like', 'happy to'],
			'Can_Verb': ['could', 'can'],
			'Contri_Verb': ['help'],
			'Progress_Phrase': ['take a look', 'have a fix', 'work on'],
			'Done_Phrase': ['have'],
			'Expect_Phrase': ['look forward to'],
			'PR_Phrase': ['pull request', 'pr'],
		}

		gnl_patterns = [
			[('Plan_Phrase', 'v'), ('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Intend_Phrase', 'v'), ('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Can_Verb', 'v'), ('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Intend_Phrase', 'v'), ('Contri_Verb', 'v')],
			[('i', 'w'), ('Plan_Phrase', 'v'), ('Volun_Verb', 'v'), ('it', 'w')],
			[('i', 'w'), ('Plan_Phrase', 'v'), ('Progress_Phrase', 'v')],
			[('Plan_Phrase', 'v'), ('Progress_Phrase', 'v')],
			[('Done_Phrase', 'v'), ('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Expect_Phrase', 'v'), ('PR_Phrase', 'v')],
			[('Can_Verb', 'v'), ('PRON', 'p'), ('PR_Phrase', 'v')],
			[('Intend_Phrase', 'v'), ('Volun_Verb', 'v')],
			[('i', 'w'), ('Can_Verb', 'v'), ('do', 'w')],
			[('Done_Phrase', 'v'), ('Volun_Verb', 'v'), ('X', 'p')],
		]

		spc_patterns = []

	return vocabulary, gnl_patterns, spc_patterns


def atom_patterns(tag):
	if tag == 'LD1':
		vocabulary = {
			'Order_Verb': ['should', 'need to', 'can not', 'have to', 'can also', 'have not'],
			'Can_Verb': ['could', 'can'],
			'Alter_Verb': ['use', 'try', 'run', 'install', 'look at', 'build', 'update'],
			'Material_Noun': ['article'],
			'Infer_Phrase': ['may', 'probably'],
			'Want_Verb': ['want'],
			'Sol_Verb': ['solve'],
		}

		gnl_patterns = [
			[('you', 'w'), ('Order_Verb', 'v')],
			[('you', 'w'), ('Can_Verb', 'v'), ('Alter_Verb', 'v')],
			[('AUX', 'p'), ('you', 'w'), ('Alter_Verb', 'v')],
			[('DET', 'p'), ('Material_Noun', 'v'), ('help', 'l')],
			[('you', 'w'), ('Infer_Phrase', 'v'), ('Want_Verb', 'v')],
			[('try', 'w'), ('Alter_Verb', 'v')],
			[('please', 'w'), ('Alter_Verb', 'v')],
			[('i', 'w'), ('Sol_Verb', 'v')],
			[('try', 'w'), ('NOUN', 'p')],
			[('i', 'w'), ('suggest', 'wl')],
			[('you', 'w'), ('Want_Verb', 'v'), ('NOUN', 'p')],
		]

		spc_patterns = []

	elif tag == 'LD2':
		vocabulary = {
			'Guide_Phrase': ['duplicate', 'fix', 'report', 'same', 'dupe'],
			'PR_Phrase': ['pr'],
			'Direct_Verb': ['ask', 'report', 'post', 'file', 'open', 'move'],
			'Place_Noun': ['repo', 'repository', 'discuss'],
			'Direct_Noun': ['message', 'issue'],
			'Place_ADV': ['there'],
		}

		gnl_patterns = [
			[('Guide_Phrase', 'v'), ('ADP', 'p'), ('#', 'w'), ('NUM', 'p')],
			[('Guide_Phrase', 'v'), ('ADP', 'p'), ('X', 'p')],
			[('duplicate', 'l'), ('#', 'w'), ('NUM', 'p')],
			[('Guide_Phrase', 'v'), ('ADP', 'p'), ('PR_Phrase', 'v')],
			[('Direct_Verb', 'v'), ('ADP', 'p'), ('Place_Noun', 'v')],
			[('Direct_Verb', 'v'), ('Direct_Noun', 'v'), ('ADP', 'p')],
			[('Direct_Verb', 'v'), ('this', 'w'), ('ADP', 'p')],
			[('should', 'w'), ('be', 'l'), ('Direct_Noun', 'v'), ('in', 'w')],
			[('Direct_Verb', 'v'), ('Direct_Noun', 'v'), ('Place_ADV', 'v')],
		]

		spc_patterns = ['cc\\W+@\\w+']

	elif tag == 'LD3':
		vocabulary = {
			'Sim_Adj': ['same', 'similar'],
			'Exp_Verb': ['have', 'face', 'get', 'encounter', 'see', 'confirm', 'experience', 'hit', 'run into', 'reproduce'],
			'Issue_Noun': ['issue', 'problem', 'error', 'bug'],
			'Sim_Adv': ['too', 'as well', 'before'],
			'Can_Verb': ['can'],
			'Ref_Word': ['like'],
			'Express_Verb': ['say'],
			'Issue_None': ['issue'],
			'Confirm_Adj': ['right'],
		}

		gnl_patterns = [
			[('Sim_Adj', 'v'), ('for', 'w'), ('me', 'w')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('this', 'w'), ('Sim_Adv', 'v')],
			[('i', 'w'), ('Can_Verb', 'v'), ('reproduce', 'l')],
			[('me too', 'wl')],
			[('Ref_Word', 'v'), ('PROPN', 'p'), ('Express_Verb', 'v')],
			[('Sim_Adj', 'v'), ('Issue_Noun', 'v')],
			[('this', 'w'), ('not', 'l'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('this', 'w')],
			[('Exp_Verb', 'v'), ('this', 'w'), ('Issue_Noun', 'v')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v')],
			[('this', 'w'), ('be', 'l'), ('Issue_Noun', 'v')],
			[('this', 'w'), ('be', 'l'), ('not', 'l'), ('Issue_Noun', 'v')],
			[('make sense', 'wl')],
			[('i agree', 'wl')],
			[('Exp_Verb', 'v'), ('Sim_Adv', 'v')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v'), ('Issue_None', 'v')],
			[('Can_Verb', 'v'), ('not', 'l'), ('reproduce', 'l')],
			[('not', 'l'), ('Issue_Noun', 'v')],
			[('work for i', 'wl')],
			[('Exp_Verb', 'v'), ('Issue_Noun', 'v'), ('Sim_Adv', 'v')],
			[('PRON', 'p'), ('be', 'l'), ('Confirm_Adj', 'v')],
			[('agree with', 'wl')],
			[('Exp_Verb', 'v'), ('Sim_Adj', 'v'), ('thing', 'w')],
			[('Can_Verb', 'v'), ('reproduce', 'l'), ('this', 'w')],
		]

		spc_patterns = ['^yes', '^yep', 'yep', '^yeah', '^same', '^i agree', '@\\w+\\s*-?\\s*yes', '^yea', '^confirmed', '^confirm', '^same here', '^can confirm']

	elif tag == 'LD4':
		vocabulary = {
			'Inquiry_Verb': ['paste', 'provide', 'describe', 'post', 'confirm', 'elaborate', 'share', 'add', 'verify', 'give'],
			'Wh_Word': ['how', 'what', 'which', 'when', 'where', 'why'],
			'Inquiry_Noun': ['information', 'step', 'code'],
		}

		gnl_patterns = [
			[('AUX', 'p'), ('you', 'w'), ('Inquiry_Verb', 'v')],
			[('Wh_Word', 'v'), ('?', 'e')],
			[('AUX', 'p'), ('PRON', 'p'), ('?', 'e')],
			[('AUX', 'p'), ('the', 'w'), ('?', 'e')],
			[('be', 'l'), ('PRON', 'p'), ('?', 'e')],
			[('be', 'l'), ('the', 'w'), ('?', 'e')],
			[('please', 'w'), ('Inquiry_Verb', 'v')],
			[('Inquiry_Verb', 'v'), ('Inquiry_Noun', 'v')],
		]

		spc_patterns = []

	elif tag == 'LD5':
		vocabulary = {
			'Issue_Action': ['close', 'reopen', 're-open'],
			'Issue_Noun': ['issue'],
			'Can_Verb': ['could'],
			'Plan_Phrase': ['should be', 'will', 'going to'],
			'New_Word': ['another', 'new'],
		}

		gnl_patterns = [
			[('Issue_Action', 'v'), ('Issue_Noun', 'v')],
			[('Issue_Action', 'v'), ('this', 'w')],
			[('Issue_Action', 'v'), ('it', 'w')],
			[('Can_Verb', 'v'), ('Issue_Action', 'v')],
			[('Plan_Phrase', 'v'), ('Issue_Action', 'v')],
			[('open', 'l'), ('New_Word', 'v'), ('issue', 'w')],
		]

		spc_patterns = ['^closing']

	elif tag == 'LD6':
		vocabulary = {
			'Can_Verb': ['can'],
			'Volun_Verb': ['put in', 'make', 'do', 'give'],
			'Volun_Noun': ['pr', 'release', 'try'],
			'Plan_Phrase': ['will'],
			'Progress_Phrase': ['take a look'],
			'Contri_Verb': ['help'],
		}

		gnl_patterns = [
			[('Can_Verb', 'v'), ('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('Volun_Verb', 'v'), ('Volun_Noun', 'v')],
			[('i', 'w'), ('Plan_Phrase', 'v'), ('Progress_Phrase', 'v')],
			[('Plan_Phrase', 'v'), ('Progress_Phrase', 'v')],
			[('Can_Verb', 'v'), ('PRON', 'p'), ('Contri_Verb', 'v')],
		]

		spc_patterns = []

	return vocabulary, gnl_patterns, spc_patterns