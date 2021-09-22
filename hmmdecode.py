import sys
import os
import re
import numpy as np
import random
from copy import deepcopy
import time

trans_probs = {}
emit_probs = {}
emits_available = {}
all_tags = []





def file_reader(path):

    file = open(path)
    lines = file.read().splitlines()

    for line in lines:
        tt = line.split(" ")
        decoder(tt)
    file.close()


def decoder(sentence):
    forward_probs = {}
    states = [["$$$START$$$"]]
    unseen = []

    for i in range(0, len(sentence)):

        try:
            states.append(emits_available[sentence[i]])
        except KeyError:
            states.append(all_tags)
            unseen.append(sentence[i])


    states.append(["$$$END$$$"])
    forward_probs[0, "$$$START$$$"] = 1*10**50


    for s_i in range(0, len(sentence)):
        for tag1 in states[s_i]:
            for tag2 in states[s_i + 1]:

                if sentence[s_i] in unseen:
                    try:
                        forward_probs[s_i + 1, tag2] = deepcopy(
                            max(forward_probs[s_i, tag1] * trans_probs[tag1, tag2], forward_probs[s_i + 1, tag2]))
                    except KeyError:
                        forward_probs[s_i + 1, tag2] = forward_probs[s_i, tag1] * trans_probs[tag1, tag2]

                else:
                    try:
                        forward_probs[s_i + 1, tag2] = deepcopy(
                            max(forward_probs[s_i, tag1] * trans_probs[tag1, tag2] *
                                emit_probs[tag2, sentence[s_i]], forward_probs[s_i + 1, tag2]))

                    except KeyError:
                        forward_probs[s_i + 1, tag2] = forward_probs[s_i, tag1] \
                                                       * trans_probs[tag1, tag2] * emit_probs[tag2, sentence[s_i]]

    for tag1 in states[len(sentence)]:
        try:
            forward_probs[len(sentence) + 1, "$$$END$$$"] = \
                deepcopy(max(forward_probs[len(sentence), tag1] * trans_probs[tag1, "$$$END$$$"] ,
                             forward_probs[len(sentence) + 1, "$$$END$$$"]))

        except KeyError:
            forward_probs[len(sentence) + 1, "$$$END$$$"] = \
                deepcopy(forward_probs[len(sentence), tag1] * trans_probs[tag1, "$$$END$$$"])
    final_tag = []

    remaining = len(sentence) + 1

    current_state = "$$$END$$$"

    while remaining > 1:

        for state in states[remaining-1]:
            if current_state == "$$$END$$$" or (sentence[remaining-1] in unseen):
                if forward_probs[remaining-1, state] * trans_probs[state, current_state] == forward_probs[remaining, current_state]:
                    current_state = deepcopy(state)
                    final_tag.append(state)
                    break
            else:
                if forward_probs[remaining-1, state] * trans_probs[state, current_state] * emit_probs[current_state, sentence[remaining-1]] == forward_probs[remaining, current_state]:
                    current_state = deepcopy(state)
                    final_tag.append(state)
                    break

        remaining -= 1
    final_tag.reverse()

    line = ""

    for i in range(0, len(sentence)):
        line += sentence[i] + "/" + final_tag[i]+ " "
    line = deepcopy(line[0:-1]) + "\n"
    final_output.write(line)











def model_reader(model_path):
    file = open(model_path)
    lines = file.read().splitlines()
    file.close()
    tags = set()
    global all_tags


    for i in range(0, len(lines)):

        if lines[i] == "$$$MATINAK$$$Emit":
            emit_num = i

        if lines[i] == "$$$MATINAK$$$EMIT_TRAN_AVAILABLE":
            em_tr_av_num = i

    for i in range(1, emit_num):
        trans_line = lines[i].split("\t")
        trans_probs[trans_line[0], trans_line[1]] = float(trans_line[2])

    for i in range(emit_num + 1, em_tr_av_num):
        emit_line = lines[i].split("\t")
        emit_probs[emit_line[0], emit_line[1]] = float(emit_line[2])

    for i in range(em_tr_av_num + 1, len(lines)):
        em_av_line = lines[i].split("\t")
        emits_available[em_av_line[0]] = em_av_line[1].strip("'}{'").split("', '")
        for item in emits_available[em_av_line[0]]:
            tags.add(item)
    all_tags = deepcopy(list(tags))




if __name__ == "__main__":
    test_path_it = sys.argv[1]
    final_output = open("hmmoutput.txt", "w")
    model_reader("hmmmodel.txt")
    file_reader(test_path_it)
    final_output.close()
