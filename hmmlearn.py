import sys
import os
import re
import numpy as np
import random
from copy import deepcopy
import time






def file_reader(path):

    file = open(path)
    lines = file.read().splitlines()
    p_emit = {}
    p_trans = {}
    total_tokens = {}
    total_tags = {}
    emit_tran_available = {}
    tags = set()
    tokens = set()

    for line in lines:
        tt = line.split(" ")
        last_word_finder = 0

        for item in tt:
            last_word_finder += 1
            temp = ""

            token_tag = item.split("/")
            if len(token_tag) > 2:
                slash_tag = token_tag.pop()
                for rest in token_tag:
                    temp += rest
                    temp += "/"
                token_tag = [temp[0:-1], slash_tag]

            tags.add(token_tag[1])
            tokens.add(token_tag[0])

            try:
                emit_tran_available[token_tag[0]].add(token_tag[1])
            except KeyError:
                emit_tran_available[token_tag[0]] = set()
                emit_tran_available[token_tag[0]].add(token_tag[1])




            if last_word_finder == 1:
                try:
                    p_trans[("$$$START$$$", token_tag[1])] += 1
                except KeyError:
                    p_trans[("$$$START$$$", token_tag[1])] = 1

                try:
                    total_tags["$$$START$$$"] += 1
                except KeyError:
                    total_tags["$$$START$$$"] = 1

            else:
                try:
                    p_trans[(prev, token_tag[1])] += 1
                except KeyError:
                    p_trans[(prev, token_tag[1])] = 1
                if last_word_finder == len(tt):
                    try:
                        p_trans[(token_tag[1], "$$$END$$$")] += 1
                    except KeyError:
                        p_trans[(token_tag[1], "$$$END$$$")] = 1

                    try:
                        total_tags["$$$END$$$"] += 1
                    except KeyError:
                        total_tags["$$$END$$$"] = 1

            prev = token_tag[1]

            # token_tag[0] ---> token
            # token_tag[1] ---> tag

            try:
                p_emit[(token_tag[1], token_tag[0])] += 1
            except KeyError:
                p_emit[(token_tag[1], token_tag[0])] = 1

            try:
                total_tags[token_tag[1]] += 1
            except KeyError:
                total_tags[token_tag[1]] = 1
            try:
                total_tokens[token_tag[0]] += 1
            except KeyError:
                total_tokens[token_tag[0]] = 1

    file.close()

    return p_trans, p_emit, tags, tokens,  total_tags, total_tokens, emit_tran_available


def prob_maker(trans, emit, total_tags,  tags):
    emit_probs = {}
    trans_probs = {}

    list_tags = list(tags)

    for i1 in range(0, len(list_tags)):
        for i2 in range(0, len(list_tags)):
            try:
                trans[list_tags[i1], list_tags[i2]] += 1
                try:
                    total_tags[list_tags[i1]] += 1
                except KeyError:
                    total_tags[list_tags[i1]] = 1
            except KeyError:
                trans[list_tags[i1], list_tags[i2]] = 1
                try:
                    total_tags[list_tags[i1]] += 1
                except KeyError:
                    total_tags[list_tags[i1]] = 1
    for i1 in range(0, len(list_tags)):
        try:
            trans["$$$START$$$", list_tags[i1]] += 1
            try:
                total_tags["$$$START$$$"] += 1
            except KeyError:
                total_tags["$$$START$$$"] = 1
        except KeyError:
            trans["$$$START$$$", list_tags[i1]] = 1
            try:
                total_tags["$$$START$$$"] += 1
            except KeyError:
                total_tags["$$$START$$$"] = 1

    for i1 in range(0, len(list_tags)):
        try:
            trans[list_tags[i1], "$$$END$$$"] += 1
            try:
                total_tags[list_tags[i1]] += 1
            except KeyError:
                total_tags[list_tags[i1]] = 1
        except KeyError:
            trans[list_tags[i1], "$$$END$$$"] = 1
            try:
                total_tags[list_tags[i1]] += 1
            except KeyError:
                total_tags[list_tags[i1]] = 1

    for x, y in emit:
        emit_probs[x, y] = emit[x, y]/total_tags[x]
    for x, y in trans:
        trans_probs[x, y] = trans[x, y]/total_tags[x]

    return trans_probs, emit_probs


def model_maker(tp_it, ep_it, it_em_tr_av):

    output = open("hmmmodel.txt", "w")
    output.write("$$$MATINAK$$$Trans\n")

    for x, y in tp_it:
        output.write(str(x) + "\t" + str(y) + "\t" + str(tp_it[x, y]) + "\n")

    output.write("$$$MATINAK$$$Emit\n")

    for x, y in ep_it:
        output.write(str(x) + "\t" + str(y) + "\t" + str(ep_it[x, y]) + "\n")

    output.write("$$$MATINAK$$$EMIT_TRAN_AVAILABLE\n")

    for x in it_em_tr_av:
        output.write(str(x) + "\t" + str(it_em_tr_av[x]) + "\n")
    output.close()


if __name__ == "__main__":
    training_path_it = sys.argv[1]
    p_trans_it, p_emit_it, it_tags, it_tokens, it_total_tags, it_total_tokens, it_emit_tran_available = file_reader(training_path_it)
    trans_probs_it, emit_probs_it = prob_maker(p_trans_it, p_emit_it, it_total_tags, it_tags)
    model_maker(trans_probs_it, emit_probs_it, it_emit_tran_available)


















