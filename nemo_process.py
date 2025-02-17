import argparse
import os
from helpers import *
import torch
from pydub import AudioSegment
from nemo.collections.asr.models.msdd_models import NeuralDiarizer

parser = argparse.ArgumentParser()
parser.add_argument(
    "-a", "--audio", help="name of the target audio file", required=True
)
parser.add_argument(
    "--device",
    dest="device",
    default="cuda" if torch.cuda.is_available() else "cpu",
    help="if you have a GPU use 'cuda', otherwise 'cpu'",
)
parser.add_argument(
    "--output-folder",
    default=None,
    help="path for the output",
)
parser.add_argument(
    "--output-filename",
    default="mono_file",
    help="filename for the output and the temporary files"
)
args = parser.parse_args()

# convert audio to mono for NeMo combatibility
sound = AudioSegment.from_file(args.audio).set_channels(1)

temp_path = args.output_folder if args.output_folder else os.path.join(os.getcwd(), "temp_outputs")
os.makedirs(temp_path, exist_ok=True)
sound.export(os.path.join(temp_path, args.output_filename + ".wav"), format="wav")

# Initialize NeMo MSDD diarization model
try:
    msdd_model = NeuralDiarizer(cfg=create_config(temp_path, args.output_filename + ".wav")).to(args.device)
    msdd_model.diarize()
except torch.cuda.OutOfMemoryError as oom:
    print("******** OOM ********")
    if args.device == "cuda":
        msdd_model = NeuralDiarizer(cfg=create_config(temp_path, args.output_filename + ".wav")).to("cpu")
        msdd_model.diarize()
