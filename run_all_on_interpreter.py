import json
import subprocess
import os
import shutil

def move_to(path):
    #options = ["cd", path]
    #subprocess.check_call(options)
    os.chdir(path)

def run_compiler(src_path, second_round=False):
    move_to("../hrm_compiler")
    options = ["hrmc", src_path]
    if second_round:
        options.append("--no-unreachable")
    subprocess.check_call(options, stdout=subprocess.DEVNULL)

def run_interpreter(target_json_path, input_path):
    move_to("../hrm_interpreter")
    options = ["cargo", "run", "--",
               "--code", target_json_path,
               "--input", input_path]
    subprocess.check_call(options, stdout=subprocess.DEVNULL)

def copy_statedump(statedump_path, tmp_place):
    shutil.copy(statedump_path, tmp_place)

def check_statedump_differences():
    orig_path = "orig_dump.json"
    change_path = "change_dump.json"

    with open(orig_path) as src:
        orig_doc = json.load(src)
    with open(change_path) as src:
        change_doc = json.load(src)

    assert orig_doc["internal_state"]["input_tape"] == change_doc["internal_state"]["input_tape"]
    assert orig_doc["internal_state"]["output_tape"] == change_doc["internal_state"]["output_tape"]
    assert not orig_doc["ended_with_error"]
    assert not change_doc["ended_with_error"]

def clear_build_run_artifacts(compiled, statedump):
    os.remove(compiled)
    os.remove(statedump)

def main():
    for path, _, files in os.walk("examples/"):
        for file_ in files:
            if not file_.endswith(".hrm"):
                continue
            print("---", file_)
            full_path = os.path.join(path, file_)
            compiled_path = full_path.replace(".hrm", ".json")
            input_path = os.path.join("inputs/", file_.replace(".hrm", ".json"))
            statedump_path = compiled_path+"_state_dump.json"
            # run tests with a certain version
            run_compiler(full_path)
            run_interpreter("../hrm_compiler/"+compiled_path, "../hrm_compiler/"+input_path)
            move_to("../hrm_compiler")
            copy_statedump(statedump_path, "orig_dump.json")
            # run tests with a different version
            run_compiler(full_path)
            run_interpreter("../hrm_compiler/"+compiled_path, "../hrm_compiler/"+input_path)
            move_to("../hrm_compiler")
            copy_statedump(statedump_path, "change_dump.json")
            # check differences
            check_statedump_differences()
            # cleanup
            clear_build_run_artifacts(compiled_path, statedump_path)

main()
