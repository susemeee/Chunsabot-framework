import os
import json
import shutil
import subprocess
import string
import random

from chunsabot.database import Database
from chunsabot.botlogic import brain

RNN_PATH = Database.load_config('rnn_library_path')
MODEL_PATH = os.path.join(RNN_PATH, "models/checkpoint_v1.t7_cpu.t7")

def id_generator(size=12, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@brain.route("@image")
def add_image_description(msg, extras):
    attachment = extras['attachment']
    if not attachment:
        return None

    path = os.path.join(brain.__temppath__, "{}_{}".format(id_generator(), 'image_processing'))
    if not os.path.isdir(path):
        os.mkdir(path)
    # Moving to temp path
    img = shutil.move(attachment, path)
    img_folder = os.path.dirname(img)

    result = subprocess.Popen(
        "th eval.lua -model {} -gpuid -1 -image_folder {} -batch_size 1"\
        .format(MODEL_PATH, img_folder).split(" "),
        cwd=RNN_PATH
    ).wait()

    shutil.rmtree(img_folder)

    result_message = None
    with open(os.path.join(RNN_PATH, "vis/vis.json"), 'r') as output:
        json_output = json.loads(output.read())
        result_message = json_output[0]['caption']

    return result_message
