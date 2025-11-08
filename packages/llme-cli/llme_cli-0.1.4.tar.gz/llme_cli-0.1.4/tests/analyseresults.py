#!/usr/bin/env python3

import csv
import datetime
import glob
import itertools
import json
import os
import re
import sys
from tabulate import tabulate

def inccell(rowid, colid, mat):
    if rowid not in mat:
        mat[rowid] = {}
    matrow = mat[rowid]
    if colid not in matrow:
        matrow[colid] = 1
    else:
        matrow[colid] += 1

linksmap = {} # url -> tag
linkstag = {} # tag -> url
def getlink(what, url):
    if url in linksmap:
        what2 = linksmap[url]
        if what != what2:
            print(f"warning: {what}: {url} already linked as {waht2}")
        return f"[{what}]"
    if what in linkstag:
        url2 = linkstag[what]
        if url != url2:
            print(f"warning: {what}: {url} already linked as {url2}")
        return f"[{what}]"
    linksmap[url] = what
    linkstag[what] = url
    return f"[{what}]"

def linkmodel(model):
    extra = ""
    if " " in model:
        model, conf = model.split(" ", 1)
        extra = " " + conf + extra
    if ":" in model:
        model, size = model.split(":", 1)
        extra = ":" + size + extra
    if '/' in model:
        return getlink(model, f"https://huggingface.co/{model}") + extra
    else:
        return getlink(model, f"https://ollama.com/library/{model}") + extra

def linksuite(suite):
    return getlink(suite, f"tests/{suite}.sh")

model_results = {}
def inc_model_results(model, result):
    inccell(model, result, model_results)

model_suites = {}
total_model_suites = {}
def inc_model_suites(model, suite):
    inccell(model, suite, model_suites)

suite_results = {}
def inc_suite_results(suite, result):
    inccell(suite, result, suite_results)

task_results = {}
def inc_task_results(task, result):
    inccell(task, result, task_results)

def get(mat, rowid, colid):
    return mat.get(rowid, {}).get(colid, 0)


def color(rate):
    colors = "💀🔥🔴🟠🟡🟢💎"
    if rate == 0:
        return colors[0]
    if rate < 15:
        return colors[1]
    if rate < 35:
        return colors[2]
    if rate < 65:
        return colors[3]
    if rate < 85:
        return colors[4]
    if rate < 100:
        return colors[5]
    else:
        return colors[6]

has_running = False
status = ['PASS', 'ALMOST', 'FAIL', 'ERROR', 'TIMEOUT', 'RUNNING']

def print_mat(mat, f, name):
    table = []
    headers = {}
    entriees = {}
    for rowid in mat:
        for colid in mat[rowid]:
            v = mat[rowid][colid]
            if colid not in headers:
                headers[colid] = v
            else:
                headers[colid] += v
    for rowid in reversed(sortrow(mat)):
        if mat is model_results:
            title = linkmodel(rowid)
        elif mat is suite_results:
            title = linksuite(rowid)
        elif mat is task_results:
            s, t = rowid.split(' ', 1)
            title = f"{linksuite(s)} {t}"
        else:
            title = rowid
        total=0
        for colid in mat[rowid]:
            total += mat[rowid][colid]
        rate = 100.0 * get(mat, rowid, "PASS") / total
        tablerow = [f"{color(rate)} {title}"]
        table.append(tablerow)
        for colid in status:
            n = get(mat, rowid, colid)
            if n == 0:
                tablerow.append("0")
            else:
                tablerow.append("%d (%.0f%%)" % (n, 100.0*n/total))
        tablerow.append(total)
    headers = [name] + status + ['Total']
    f.write(tabulate(table, headers=headers, tablefmt="pipe"))
    f.write("\n")


def print_model_suites(f):
    table = []
    suites = list(reversed(sortrow(suite_results)))
    for rowid in reversed(sortrow(model_results)):
        tablerow = [linkmodel(rowid)]
        table.append(tablerow)
        for colid in suites:
            n = get(model_suites, rowid, colid)
            t = get(total_model_suites, rowid, colid)
            if t == 0:
                tablerow.append("")
            elif n == 0:
                tablerow.append(f"{color(0)} 0/{t}")
            else:
                p = 100.0 * n / t
                tablerow.append("%s %d/%d (%.0f%%)" % (color(p), n, t, p))
    titles = [linksuite(s) for s in suites]
    titles.insert(0, "Model")
    f.write(tabulate(table, headers=(titles), tablefmt="pipe"))
    f.write("\n")

def print_model_tokens(f):
    table = []
    data = []
    filter_out = {}
    for x in keept_results:
        if x.result == "ERROR":
            continue
        if not x.metrics:
            filter_out[x.model_config] = True
            continue
        all_predicted_n = x.metrics["total"].get("completion_tokens", 0)
        if not all_predicted_n:
            filter_out[x.model_config] = True
            continue
        passed = x.result == "PASS"
        pass_predicted_n = all_predicted_n if passed else 0
        data.append((x.model_config, pass_predicted_n, all_predicted_n, passed))
    data = sorted(data)
    score = {}
    for model, results in itertools.groupby(data, key = lambda x: x[0]):
        if model in filter_out:
            continue
        results = list(results)
        pass_predicted_n = sum(x[1] for x in results)
        all_predicted_n = sum(x[2] for x in results)
        pass_n = sum(x[3] for x in results)
        total_n = len(results)
        table.append([
            model_rank[model], linkmodel(model), int(pass_predicted_n / pass_n) if pass_n else None, int(all_predicted_n / total_n), f"{pass_n} / {total_n} ({pass_n/total_n*100:.0f}%)"
        ])
    table.sort()
    table = [x[1:] for x in table]
    f.write(tabulate(table, headers=["Model", "tokens/passed", "tokens/nonerror", "passed / nonerror"], tablefmt="pipe"))
    f.write("\n")

def print_model_time(f):
    table = []
    data = []
    filter_out = {}
    for x in keept_results:
        if x.result == "ERROR":
            continue
        if not x.metrics:
            filter_out[x.model_config] = True
            continue
        all_predicted_n = x.metrics["total"].get("total_ms", 0)
        if not all_predicted_n:
            filter_out[x.model_config] = True
            continue
        passed = x.result == "PASS"
        pass_predicted_n = all_predicted_n if passed else 0
        data.append((x.model_config, pass_predicted_n, all_predicted_n, passed))
    data = sorted(data)
    score = {}
    for model, results in itertools.groupby(data, key = lambda x: x[0]):
        if model in filter_out:
            continue
        results = list(results)
        pass_predicted_n = sum(x[1] for x in results)
        all_predicted_n = sum(x[2] for x in results)
        pass_n = sum(x[3] for x in results)
        total_n = len(results)
        table.append([
            model_rank[model], linkmodel(model), int(pass_predicted_n / pass_n / 1000) if pass_n else None, int(all_predicted_n / total_n / 1000), f"{pass_n} / {total_n} ({pass_n/total_n*100:.0f}%)"
        ])
    table.sort()
    table = [x[1:] for x in table]
    f.write(tabulate(table, headers=["Model", "s/passed", "s/nonerror", "passed / nonerror"], tablefmt="pipe"))
    f.write("\n")

def scorerow(row):
    scores = {"PASS": 1000000.0, "ALMOST": 1000.0, "FAIL": 1.0, "ERROR": 0.0, "TIMEOUT": 1.0}
    score = 0
    total = 0
    for colid in row:
        score += scores.get(colid,0) * row[colid]
        total += row[colid]
    return score / total


def sortrow(mat):
    res = list(mat)
    return sorted(res, key=lambda x: scorerow(mat[x]))
    return res

# an entry for each model x config x task.
# Used to aggregate multiple runs of the same task
model_config_tasks = {}

# Error results by modet_config
errors = {}


class Result:
    def __init__(self, directory):
        self.directory = directory
        self.result = None
        self.config = None
        self.cause = None
        self.metrics = None
        pathjson = f"{directory}/result.json"
        if os.path.exists(pathjson):
            with open(pathjson, 'r') as file:
                data = json.load(file)
                for k in data:
                    setattr(self, k, data[k])
        else:
            # Convert old csv format
            pathcsv = f"{directory}/result.csv"
            if not os.path.exists(pathcsv):
                #print(f"{directory}: no result. skip")
                return
            with open(pathcsv, 'r') as file:
                reader = csv.reader(file)
                row = next(reader)
                self.suite = row[0]
                self.task = row[1]
                self.result = row[4]
                self.comment = row[5]
                if len(row) > 6:
                    self.msgs = row[6]
                if len(row) > 7:
                    self.words = row[7]
                self.path = directory[:-1]
                self.date = int(self.path.split('-')[-1])
                data = vars(self)
                with open(pathjson, 'w') as file:
                    json.dump(data, file, indent=0)
        patherr = f"{self.directory}/err.txt"
        if os.path.exists(patherr):
            with open(patherr, "r") as f:
                causes = list(f.readlines())
                while causes and not causes[-1]:
                    causes.pop()
                if causes:
                    cause = causes[-1].strip()[:80]
                else:
                    cause = "???"
            self.cause = cause
        pathmetrics = f"{self.directory}/metrics.json"
        if os.path.exists(pathmetrics):
            with open(pathmetrics, 'r') as f:
                self.metrics = json.load(f)

        self.date = datetime.datetime.fromtimestamp(self.date)

        pathconfig = f"{directory}/config.json"
        if os.path.exists(pathconfig) and os.path.getsize(pathconfig) > 0:
            with open(pathconfig, 'r') as f:
                self.config = json.load(f)
        else:
            print(f"{directory}: no config. skip")
            return

        self.model = self.config["model"]
        self.model_config = self.model
        t = self.config.get("temperature")
        if t is not None:
            self.model_config = f"{self.model_config} t={t}"
        t = self.config.get("tool_mode")
        if t is None:
            t = "markdown"
            self.config["tool_mode"] = t
        self.model_config = f"{self.model_config} mode={t}"

        self.model_config_task = f"{self.model_config} {self.suite} {self.task}"
        if self.model_config_task not in model_config_tasks:
            model_config_tasks[self.model_config_task] = [self]
        else:
            model_config_tasks[self.model_config_task].append(self)

    def __repr__(self):
        return self.model_config_task + " " + self.directory
    def __str__(self):
        return self.model_config_task + " " + self.directory

    def process(self):
        inc_model_results(self.model_config, self.result)
        inc_suite_results(self.suite, self.result)
        inc_task_results(self.suite+" "+self.task, self.result)
        inccell(self.model_config, self.suite, total_model_suites)
        if self.result == "PASS":
            inc_model_suites(self.model_config, self.suite)
        if self.result == "RUNNING":
            global has_running
            has_running = True
        if self.result == "ERROR":
            if self.cause in errors:
                errors[self.cause].append(self)
            else:
                errors[self.cause] = [self]
        if self.metrics:
            total = self.metrics.get("total")
            prompt_ms = total.get("prompt_ms", 0)
            prompt_n = total.get("prompt_n", 0)

    def replay(self):
        res = f"./tests/{self.suite}.sh -m {self.model}"
        t = self.config.get("temperature")
        if t is not None:
            res += f" --temperature={t}"
        t = self.config.get("tool_mode")
        if t is not None:
            res += f" --tool-mode={t}"
        c = self.config["config"]
        if c:
            res += f" -c {c[0]}"
        return res

keep = {}
base_models = {}
keept_results = []
model_order = None
model_rank = {}

def main():
    results = []
    for d in glob.glob('logs/*/') + glob.glob('logs/*/*/'):
        try:
            result = Result(d)
            if result.config:
                results.append(result)
        except json.decoder.JSONDecodeError as e:
            print(f"{d}: {e}")
        except Exception as e:
            print(f"{d}: {e}")
            raise e

    for result in results:
        if result.result == "ERROR":
            continue
        model = result.model_config
        keep[model] = True

    for ts, tests in model_config_tasks.items():
        tests.sort(key=lambda x: x.date)
        t = tests[-1]
        if t.model_config in keep:
            t.process()
            keept_results.append(t)
            base_models[t.model] = True

    if not has_running:
        status.remove('RUNNING')

    global model_order
    model_order = list(reversed(sortrow(model_results)))
    for i, m in enumerate(model_order):
        model_rank[m] = i

    with open("benchmark.md", 'r') as f:
        results = f.read()

    cut = "\n<!-- the contents bellow this line are generated -->\n"
    head = results.split(cut, 1)[0]
    print(len(head),len(results))

    message_n = 0
    prompt_n = 0
    predicted_n = 0
    for result in keept_results:
        if not result.metrics:
            continue
        message_n += result.metrics.get("total").get("message_n", 0)
        prompt_n += result.metrics.get("total").get("prompt_tokens", 0)
        predicted_n += result.metrics.get("total").get("completion_tokens", 0)

    with open("benchmark.md", 'w') as f:

        f.write(head)
        f.write(cut)

        f.write("\n")
        f.write(f"* {len(base_models)} models\n")
        f.write(f"* {len(model_results)} model configurations\n")
        f.write(f"* {len(suite_results)} task suites\n")
        f.write(f"* {len(task_results)} tasks\n")
        f.write(f"* {len(keept_results)} task executions\n")
        f.write(f"* {message_n:,} messages\n")
        f.write(f"* {predicted_n:,} predicted tokens\n")

        f.write("\n## Results by models\n\n")
        print_mat(model_results, f, "Model")

        f.write("\n## Task suites by models\n\n")
        print_model_suites(f)

        f.write("\n## Predicted tokens by models\n\n")
        f.write("The average number of predicted tokens per execution that passed (PASS), and per non error execution (!ERROR). Do not compare models that do not share the same tasks. Not all experiments have this information yet.\n\n")
        print_model_tokens(f)

        f.write("\n## Conversation time by models\n\n")
        f.write("The average time in requests with the server. Because we used different servers with different GPU, and different load average, do not think too much about the absolute values.\n\n")
        print_model_time(f)

        f.write("\n## Results by task suites\n\n")
        print_mat(suite_results, f, "Task suite")

        f.write("\n## Results by tasks\n\n")
        print_mat(task_results, f, "Task")

        f.write("\n\n")
        for link in sorted(linkstag.keys()):
            f.write(f"  [{link}]: {linkstag[link]}\n")

    with open("benchmark_more.md", "w") as f:
        f.write("\n## Error Causes\n\n")
        causes = sorted(errors.keys(), key=lambda x: -len(errors[x]))
        table=[]
        for c in causes:
            f.write(f"{c} ({len(errors[c])})\n")
            for e in errors[c][:10]:
                f.write(f" * {e} {e.directory}\n")
            f.write("\n")

        f.write("\n## Replay ERRORs\n\n")
        key = lambda x: (x.model_config, x.suite)
        data = keept_results
        data = itertools.filterfalse(lambda x: x.result != "ERROR", data)
        data = sorted(data, key=key)
        for config_task, results in itertools.groupby(data, key):
            results = list(results)
            f.write(f"{results[0].replay()} # {len(results)} {results[0].cause}\n")

        f.write("\n## Missing tests\n\n")
        all_suites = suite_results.keys()
        key = lambda x: x.model_config
        data = keept_results
        data = sorted(data, key=key)
        for config, results in itertools.groupby(data, key):
            suites = {}
            for r in results:
                suites[r.suite] = True
            for s in all_suites:
                if s not in suites:
                    missing = Result(r.directory)
                    missing.suite = s
                    f.write(f"{missing.replay()} # {config} missing {s}\n")


if __name__ == "__main__":
    main()
